#!/usr/bin/env python3
"""Offline regression tests for devflow.py; no external dependencies."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).with_name('devflow.py')


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          text=True, capture_output=True, timeout=20)


class DevflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def init(self, profile='embedded', assurance='standard', *extra):
        return run('init', '--root', self.root, '--profile', profile, '--assurance', assurance, *extra)

    def test_dryrun_does_not_write(self):
        ret = self.init('web', 'standard', '--dry-run')
        self.assertEqual(ret.returncode, 0, ret.stderr)
        self.assertFalse((self.root / '.devflow.json').exists())
        self.assertIn('api_data', ret.stdout)

    def test_init_then_audit_reports_placeholders(self):
        ret = self.init()
        self.assertEqual(ret.returncode, 0, ret.stderr)
        cfg = json.loads((self.root / '.devflow.json').read_text())
        self.assertEqual(cfg['project_type'], 'embedded')
        self.assertIn('target_verification', cfg['document_map'])
        au = run('audit', '--root', self.root, '--json')
        self.assertEqual(au.returncode, 0, au.stderr)
        obj = json.loads(au.stdout)
        self.assertEqual(obj['assessment'], 'REVIEW_REQUIRED')
        gt = run('gate', '--root', self.root, '--stage', 'design')
        self.assertEqual(gt.returncode, 2)
        self.assertEqual(json.loads(gt.stdout)['external_status'], 'UNKNOWN')

    def test_adoption_maps_existing_without_overwrite(self):
        existing = self.root / 'docs' / 'REQUIREMENTS.md'
        existing.parent.mkdir()
        existing.write_text('# Real project requirements\nREQ-AUTH-001\n')
        before = existing.read_bytes()
        blocked = self.init('web')
        self.assertEqual(blocked.returncode, 2)
        ok = self.init('web', 'standard', '--adopt')
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(existing.read_bytes(), before)
        cfg = json.loads((self.root / '.devflow.json').read_text())
        self.assertEqual(cfg['document_map']['requirements'], 'docs/REQUIREMENTS.md')
        self.assertEqual(self.init('web', 'standard', '--adopt').returncode, 2)

    def test_trace_valid_and_broken_evidence(self):
        self.assertEqual(self.init('app', 'lite').returncode, 0)
        cfg = json.loads((self.root / '.devflow.json').read_text())
        req = self.root / cfg['document_map']['requirements']
        req.write_text('# R\nREQ-PLAY-001 supports decoding\n', encoding='utf-8')
        tr = self.root / cfg['document_map']['traceability']
        with tr.open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['requirement_id', 'design_ref', 'test_id', 'evidence_ref', 'status'])
            w.writerow(['REQ-PLAY-001', cfg['document_map']['architecture'], 'TEST-PLAY-001', 'no-evidence.txt', 'verified'])
        au = json.loads(run('audit', '--root', self.root, '--json').stdout)
        self.assertTrue(any(x['code'] == 'BROKEN_REF' for x in au['checks']))
        self.assertEqual(au['assessment'], 'BLOCKED')

    def test_confined_path_and_missing_docs(self):
        self.assertEqual(self.init('web', 'high').returncode, 0)
        cfgpath = self.root / '.devflow.json'
        cfg = json.loads(cfgpath.read_text())
        cfg['document_map']['requirements'] = '../../other/requires.md'
        cfgpath.write_text(json.dumps(cfg))
        out = json.loads(run('audit', '--root', self.root, '--json').stdout)
        self.assertTrue(any(x['code'] == 'UNSAFE_PATH' for x in out['checks']))
        self.assertEqual(run('audit', '--root', self.root, '--strict').returncode, 2)

    def test_profile_inspector(self):
        (self.root / 'soc-board.dts').write_text('/dts-v1/;')
        obj = json.loads(run('inspect', '--root', self.root).stdout)
        self.assertEqual(obj['suggested_profile'], 'embedded')


if __name__ == '__main__':
    unittest.main(verbosity=2)
