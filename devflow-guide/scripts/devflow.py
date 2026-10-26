#!/usr/bin/env python3
"""devflow-guide offline advisory CLI, Python 3.9+, standard library only.

No remote network, no project build commands, no git modifications and no overwrite.
Local audit/gate status never certifies remote CI, hardware testing or human approval.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / 'assets' / 'templates'
KINDS = ('embedded', 'web', 'app')
ASSURANCES = ('lite', 'standard', 'high')
MANAGED = 'docs/devflow/'
DOCS = {
    'index': ('docs/devflow/INDEX.md', 'index.md.tmpl'),
    'requirements': ('docs/devflow/requirements/REQUIREMENTS.md', 'requirements.md.tmpl'),
    'architecture': ('docs/devflow/architecture/ARCHITECTURE.md', 'architecture.md.tmpl'),
    'contracts': ('docs/devflow/interfaces/CONTRACTS.md', 'contracts.md.tmpl'),
    'test_plan': ('docs/devflow/testing/TEST_PLAN.md', 'test_plan.md.tmpl'),
    'traceability': ('docs/devflow/testing/TRACEABILITY.csv', 'traceability.csv.tmpl'),
    'release_plan': ('docs/devflow/release/RELEASE_PLAN.md', 'release_plan.md.tmpl'),
    'review_log': ('docs/devflow/reviews/REVIEW_LOG.md', 'review_log.md.tmpl'),
    'risk_register': ('docs/devflow/risk/RISK_REGISTER.md', 'risk_register.md.tmpl'),
    'baseline': ('docs/devflow/governance/BASELINE.md', 'baseline.md.tmpl'),
    'board_matrix': ('docs/devflow/embedded/BOARD_MATRIX.md', 'board_matrix.md.tmpl'),
    'hardware_contract': ('docs/devflow/embedded/HARDWARE_CONTRACT.md', 'hardware_contract.md.tmpl'),
    'realtime_memory': ('docs/devflow/embedded/REALTIME_MEMORY.md', 'realtime_memory.md.tmpl'),
    'target_verification': ('docs/devflow/embedded/TARGET_VERIFICATION.md', 'target_verification.md.tmpl'),
    'firmware_manifest': ('docs/devflow/embedded/FIRMWARE_MANIFEST.md', 'firmware_manifest.md.tmpl'),
    'api_data': ('docs/devflow/web/API_DATA.md', 'api_data.md.tmpl'),
    'web_security': ('docs/devflow/web/SECURITY.md', 'web_security.md.tmpl'),
    'service_ops': ('docs/devflow/web/SERVICE_OPERATIONS.md', 'service_ops.md.tmpl'),
    'ui_state': ('docs/devflow/app/UI_STATE.md', 'ui_state.md.tmpl'),
    'compatibility': ('docs/devflow/app/COMPATIBILITY.md', 'compatibility.md.tmpl'),
    'packaging': ('docs/devflow/app/PACKAGING.md', 'packaging.md.tmpl'),
}
ALTERNATES = {
    'requirements': ['docs/requirements/REQUIREMENTS.md', 'docs/SRS.md', 'docs/REQUIREMENTS.md', 'REQUIREMENTS.md'],
    'architecture': ['docs/architecture/ARCHITECTURE.md', 'docs/ARCHITECTURE.md', 'ARCHITECTURE.md'],
    'contracts': ['docs/interfaces/CONTRACTS.md', 'docs/API.md', 'docs/PROTOCOL.md', 'docs/api/openapi.yaml'],
    'test_plan': ['docs/testing/TEST_PLAN.md', 'docs/TEST_PLAN.md', 'TEST_PLAN.md'],
    'traceability': ['docs/testing/TRACEABILITY.csv', 'docs/TRACEABILITY.csv'],
    'release_plan': ['docs/release/RELEASE_PLAN.md', 'docs/RELEASE.md'],
    'review_log': ['docs/reviews/REVIEW_LOG.md'],
    'risk_register': ['docs/risk/RISK_REGISTER.md'],
    'baseline': ['docs/governance/BASELINE.md'],
    'board_matrix': ['docs/embedded/BOARD_MATRIX.md'],
    'hardware_contract': ['docs/embedded/HARDWARE_CONTRACT.md'],
    'realtime_memory': ['docs/embedded/REALTIME_MEMORY.md'],
    'target_verification': ['docs/embedded/TARGET_VERIFICATION.md'],
    'firmware_manifest': ['docs/embedded/FIRMWARE_MANIFEST.md'],
    'api_data': ['docs/web/API_DATA.md', 'openapi.yaml', 'openapi.json'],
    'web_security': ['docs/web/SECURITY.md', 'SECURITY.md'],
    'service_ops': ['docs/operations/RUNBOOK.md'],
    'ui_state': ['docs/app/UI_STATE.md'],
    'compatibility': ['docs/app/COMPATIBILITY.md'],
    'packaging': ['docs/app/PACKAGING.md'],
}
TRACECOLS = ['requirement_id', 'design_ref', 'test_id', 'evidence_ref', 'status']
REQPAT = re.compile(r'\bREQ-[A-Z0-9]+(?:-[A-Z0-9]+)+\b')
TESTPAT = re.compile(r'^TEST-[A-Z0-9]+(?:-[A-Z0-9]+)+$')


def safe_relative(root: Path, p: str) -> Path:
    """Reject path traversal and symlink escape from repository root."""
    candidate = Path(p)
    if not p or candidate.is_absolute() or '..' in candidate.parts or '\\' in p or '\x00' in p:
        raise ValueError('unsafe relative path: ' + repr(p))
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('path escapes repository (possibly via symlink): ' + repr(p))
    return root / candidate


def read_text(p: Path) -> str:
    return p.read_text(encoding='utf-8-sig', errors='replace')


def git(root: Path, *args: str) -> str | None:
    try:
        cp = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                            text=True, timeout=8, check=False,
                            env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'})
        return cp.stdout.strip() if cp.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def inspect(root: Path) -> dict:
    markers = {'embedded': [], 'web': [], 'app': []}
    # Avoid traversing huge repositories, hidden metadata, dependencies or build outputs.
    ignored = {'.git', '.venv', 'node_modules', 'vendor', 'dist', 'build', 'out',
               'target', '.next', '.idea', 'coverage', '__pycache__', '.gradle'}
    checked = 0
    for base, dirs, names in os.walk(root, followlinks=False):
        depth = len(Path(base).relative_to(root).parts)
        dirs[:] = sorted(d for d in dirs if d not in ignored and not d.startswith('.'))[:120] if depth < 4 else []
        if depth > 4:
            continue
        for name in sorted(names):
            checked += 1
            if checked > 5000:
                break
            rel = str((Path(base) / name).relative_to(root)).replace('\\', '/')
            lo = name.lower()
            if lo in {'west.yml', 'kconfig', 'prj.conf', 'platformio.ini', 'idf_component.yml', 'zephyr.dts'} or lo.endswith(('.dts', '.dtsi', '.ld', '.ioc')):
                markers['embedded'].append(rel)
            elif any(part in rel.lower() for part in ('/drivers/', '/bsp/', '/firmware/')):
                markers['embedded'].append(rel)
            if lo in {'package.json', 'vite.config.ts', 'vite.config.js', 'next.config.js', 'next.config.mjs',
                      'angular.json', 'manage.py', 'pom.xml', 'openapi.yaml', 'openapi.json'} or lo.endswith('.csproj') and 'web' in rel.lower():
                markers['web'].append(rel)
            if lo in {'mainwindow.cpp', 'mainactivity.kt', 'androidmanifest.xml', 'pubspec.yaml',
                      'appdelegate.swift', 'info.plist', 'tauri.conf.json', 'electron-builder.yml'} or lo.endswith(('.pro', '.qml')):
                markers['app'].append(rel)
        if checked > 5000:
            break
    scores = {kind: len(val) for kind, val in markers.items()}
    ranked = sorted(scores, key=lambda k: scores[k], reverse=True)
    populated = [k for k in ranked if scores[k] > 0]
    if not populated:
        candidate = 'unknown'
    elif len(populated) > 1 and scores[ranked[1]] >= max(2, scores[ranked[0]] * 0.5):
        candidate = 'hybrid/ambiguous'
    else:
        candidate = populated[0]
    return {
        'root': str(root), 'suggested_profile': candidate, 'scores': scores,
        'sample_evidence': {k: v[:12] for k, v in markers.items()},
        'git_head': git(root, 'rev-parse', 'HEAD'),
        'branch': git(root, 'branch', '--show-current'),
        'has_devflow_config': (root / '.devflow.json').exists(),
        'scanned_files_upper_bound': checked,
        'caution': 'Heuristic only. Manually confirm project scope, profile, assurance and target environment.'
    }


def required_keys(profile: str, assurance: str) -> list[str]:
    base = ['index', 'requirements', 'architecture', 'contracts', 'test_plan', 'traceability']
    if assurance in ('standard', 'high'):
        base += ['release_plan', 'review_log']
    if assurance == 'high':
        base += ['risk_register', 'baseline']
    overlay = {
        'embedded': ['board_matrix', 'hardware_contract', 'realtime_memory', 'target_verification', 'firmware_manifest'],
        'web': ['api_data', 'web_security', 'service_ops'],
        'app': ['ui_state', 'compatibility', 'packaging'],
    }[profile]
    if assurance == 'lite':
        # keep lite truly lightweight; domain-specific details can be inline with common docs
        return base
    return base + overlay


def project_has_content(root: Path) -> bool:
    return any(x.name not in {'.git', '.DS_Store', '.agents', '.gitignore'} for x in root.iterdir())


def mapping_for(root: Path, profile: str, assurance: str, adopt: bool) -> dict:
    result = {}
    for key in required_keys(profile, assurance):
        default, _ = DOCS[key]
        if adopt:
            candidates = ALTERNATES.get(key, []) + [default]
            match = next((p for p in candidates if (root / p).is_file()), None)
            if match:
                result[key] = match
                continue
        result[key] = default
    return result


def format_template(key: str, cfg: dict) -> str:
    templ = read_text(TEMPLATES / DOCS[key][1])
    return templ.replace('{{PROJECT_NAME}}', cfg['project_name']).replace('{{PROFILE}}', cfg['project_type']).replace('{{ASSURANCE}}', cfg['assurance'])


def cmd_init(args) -> int:
    root = args.root.resolve()
    if not root.is_dir():
        print('ERROR: project root must be an existing directory.', file=sys.stderr)
        return 2
    if project_has_content(root) and not args.adopt and not (root / '.devflow.json').exists():
        print('BLOCKED: non-empty project; run --dry-run --adopt first, then explicitly approve adoption.', file=sys.stderr)
        return 2
    cfgp = root / '.devflow.json'
    if cfgp.exists():
        print('BLOCKED: .devflow.json already exists. Do not silently change profile, assurance, or document mapping.', file=sys.stderr)
        return 2
    cfg = {
        'schema_version': 1,
        'project_name': args.name or root.name,
        'project_type': args.profile,
        'assurance': args.assurance,
        'document_map': mapping_for(root, args.profile, args.assurance, args.adopt),
        'policy': {'docs_and_tests_in_same_change': True, 'external_ci_review_required': args.assurance != 'lite',
                   'release_approval_is_manual': True, 'auto_overwrite': False}
    }
    planned = []
    for key, rel in cfg['document_map'].items():
        try:
            path = safe_relative(root, rel)
        except ValueError as exc:
            print('BLOCKED:', exc, file=sys.stderr)
            return 2
        if path.is_file():
            planned.append({'action': 'map-existing', 'key': key, 'path': rel})
        elif path.exists():
            print('BLOCKED: expected file but path is not a regular file: ' + rel, file=sys.stderr)
            return 2
        else:
            planned.append({'action': 'create', 'key': key, 'path': rel})
    planned.insert(0, {'action': 'create', 'key': 'config', 'path': '.devflow.json'})
    print(json.dumps({'dry_run': args.dry_run, 'profile': args.profile, 'assurance': args.assurance,
                      'planned': planned}, indent=2, ensure_ascii=False))
    if args.dry_run:
        return 0
    # Race-safe exclusive file creation; we never replace an existing path.
    def exclusive_write(path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags, 0o644)
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
    try:
        for item in planned[1:]:
            if item['action'] == 'create':
                exclusive_write(safe_relative(root, item['path']), format_template(item['key'], cfg))
        exclusive_write(cfgp, json.dumps(cfg, ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError) as exc:
        print('PARTIAL/ERROR: safe initialization stopped without overwriting files:', exc, file=sys.stderr)
        print('Inspect created templates before retrying. Existing files were never overwritten.', file=sys.stderr)
        return 2
    print('INITIALIZED: review/fill the placeholders; run audit. No project code or CI changed.')
    return 0


def load_cfg(root: Path) -> dict:
    cfgp = root / '.devflow.json'
    if not cfgp.is_file():
        raise ValueError('missing .devflow.json (run inspect/init with approval)')
    try:
        cfg = json.loads(read_text(cfgp))
    except (ValueError, OSError) as exc:
        raise ValueError('invalid .devflow.json: ' + str(exc))
    if cfg.get('schema_version') != 1 or cfg.get('project_type') not in KINDS or cfg.get('assurance') not in ASSURANCES:
        raise ValueError('schema_version/profile/assurance invalid in .devflow.json')
    if not isinstance(cfg.get('document_map'), dict):
        raise ValueError('document_map must be an object')
    return cfg


def issue(items, severity, code, message, path=''):
    items.append({'severity': severity, 'code': code, 'message': message, 'path': path})


def audit(root: Path, base: str | None = None) -> dict:
    result = {'root': str(root), 'checks': [], 'assessment': 'NOT_EVALUATED',
              'disclaimer': 'Local structural audit only; not verification of CI, hardware, correctness, or approval.'}
    findings = result['checks']
    try:
        cfg = load_cfg(root)
    except ValueError as e:
        issue(findings, 'ERROR', 'CONFIG', str(e), '.devflow.json')
        result['assessment'] = 'BLOCKED'
        return result
    result['project_type'] = cfg['project_type']
    result['assurance'] = cfg['assurance']
    docmap = cfg['document_map']
    contents = {}
    for key in required_keys(cfg['project_type'], cfg['assurance']):
        rel = docmap.get(key)
        if not isinstance(rel, str):
            issue(findings, 'ERROR', 'DOC_MAP', 'missing required mapping for ' + key)
            continue
        try:
            path = safe_relative(root, rel)
        except ValueError as exc:
            issue(findings, 'ERROR', 'UNSAFE_PATH', str(exc), rel)
            continue
        if not path.is_file():
            issue(findings, 'ERROR', 'MISSING_DOC', 'mapped required document is missing', rel)
            continue
        if path.suffix.lower() == '.md':
            content = read_text(path)
            contents[key] = content
            if re.search(r'\bTODO\b|\[待填写\]|\bTBD\b', content, flags=re.I):
                issue(findings, 'WARN', 'PLACEHOLDER', 'document contains unfilled placeholders', rel)
        elif key == 'traceability' and path.suffix.lower() != '.csv':
            issue(findings, 'ERROR', 'TRACE_FORMAT', 'traceability document must be CSV for built-in checker', rel)
    reqids = set(REQPAT.findall(contents.get('requirements', '')))
    # Drop fenced/illustrative examples by convention: user must keep true REQ IDs in requirements doc.
    if not reqids:
        issue(findings, 'WARN', 'NO_REQ', 'no well-formed REQ-ID in requirement document')
    rel = docmap.get('traceability')
    rows = []
    if isinstance(rel, str):
        try:
            tracepath = safe_relative(root, rel)
            if tracepath.is_file() and tracepath.suffix.lower() == '.csv':
                with tracepath.open(encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    missing_cols = [c for c in TRACECOLS if c not in (reader.fieldnames or [])]
                    if missing_cols:
                        issue(findings, 'ERROR', 'TRACE_COLS', 'missing CSV columns: ' + ', '.join(missing_cols), rel)
                    else:
                        rows = list(reader)
        except (OSError, ValueError, csv.Error) as exc:
            issue(findings, 'ERROR', 'TRACE_READ', str(exc), rel)
    covered, seen_pairs = set(), set()
    for i, row in enumerate(rows, 2):
        req = (row.get('requirement_id') or '').strip()
        design = (row.get('design_ref') or '').strip()
        test = (row.get('test_id') or '').strip()
        evidence = (row.get('evidence_ref') or '').strip()
        state = (row.get('status') or '').strip().lower()
        if not REQPAT.fullmatch(req):
            issue(findings, 'ERROR', 'TRACE_REQ', f'row {i} invalid requirement id', rel)
        elif req not in reqids:
            issue(findings, 'WARN', 'TRACE_ORPHAN', f'row {i} {req} not found in requirements document', rel)
        else:
            covered.add(req)
        if not TESTPAT.fullmatch(test):
            issue(findings, 'ERROR', 'TRACE_TEST', f'row {i} invalid test id', rel)
        if (req, test) in seen_pairs:
            issue(findings, 'WARN', 'TRACE_DUP', f'row {i} duplicate REQ/TEST pair', rel)
        seen_pairs.add((req, test))
        if state not in {'planned', 'implemented', 'verified', 'retired'}:
            issue(findings, 'ERROR', 'TRACE_STATUS', f'row {i} unknown status {state!r}', rel)
        for label, target in [('design', design), ('evidence', evidence)]:
            if not target:
                if label == 'design' or (label == 'evidence' and state == 'verified'):
                    issue(findings, 'ERROR', 'TRACE_REF', f'row {i} missing {label} reference', rel)
                continue
            if target.startswith(('http://', 'https://')):
                issue(findings, 'INFO', 'EXTERNAL_REF', f'row {i} {label} URL not verified offline', rel)
            else:
                try:
                    path = safe_relative(root, target.split('#', 1)[0])
                    if not path.is_file():
                        issue(findings, 'ERROR', 'BROKEN_REF', f'row {i} missing {label} file: {target}', rel)
                except ValueError as exc:
                    issue(findings, 'ERROR', 'UNSAFE_REF', f'row {i} {exc}', rel)
            if label == 'evidence' and state == 'verified':
                issue(findings, 'INFO', 'SELF_REPORTED', f'row {i} verified is a self-reported status; validate genuine evidence externally', rel)
    for req in sorted(reqids - covered):
        issue(findings, 'WARN', 'UNCOVERED_REQ', f'{req} has no traceability row', rel or '')
    if base:
        changed = git(root, 'diff', '--name-only', f'{base}...HEAD')
        if changed is None:
            issue(findings, 'WARN', 'GIT_BASE', 'cannot compare with git baseline: ' + base)
        else:
            files = [s.strip() for s in changed.splitlines() if s.strip()]
            code = [f for f in files if not f.startswith(('docs/', '.github/')) and not f.endswith(('.md', '.csv', '.json'))]
            docs = [f for f in files if f.startswith('docs/') or f.endswith('.md')]
            result['changed_paths'] = files
            if code and not docs:
                issue(findings, 'WARN', 'DOC_DRIFT', 'code changed with no documentation update; check impact, can be intentional')
    errors = sum(x['severity'] == 'ERROR' for x in findings)
    warnings = sum(x['severity'] == 'WARN' for x in findings)
    result['counts'] = {'errors': errors, 'warnings': warnings, 'requirements': len(reqids),
                        'trace_rows': len(rows), 'covered_requirements': len(covered)}
    result['assessment'] = 'BLOCKED' if errors else ('REVIEW_REQUIRED' if warnings else 'LOCALLY_CONSISTENT')
    return result


def render(result: dict, as_json: bool):
    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print('Project:', result.get('root'))
        if result.get('project_type'):
            print('Profile:', result['project_type'], '/ Assurance:', result['assurance'])
        for f in result.get('checks', []):
            print(f"[{f['severity']}] {f['code']}: {f['message']}" + (' (' + f['path'] + ')' if f.get('path') else ''))
        print('LOCAL ASSESSMENT:', result['assessment'])
        print('NOTE:', result['disclaimer'])


def cmd_audit(args) -> int:
    root = args.root.resolve()
    if not root.is_dir():
        print('ERROR: root directory not found', file=sys.stderr)
        return 2
    result = audit(root, args.base)
    render(result, args.json)
    if result['assessment'] == 'BLOCKED':
        return 2
    if args.strict and result['assessment'] != 'LOCALLY_CONSISTENT':
        return 1
    return 0


def cmd_gate(args) -> int:
    root = args.root.resolve()
    if not root.is_dir():
        print('ERROR: root directory not found', file=sys.stderr)
        return 2
    result = audit(root, args.base)
    blockers = [x for x in result['checks'] if x['severity'] == 'ERROR']
    if result['assessment'] != 'BLOCKED':
        # All stages require unfinished placeholders to be resolved; no inference of acceptance.
        critical_keys = ({'requirements', 'architecture', 'contracts', 'test_plan', 'risk_register'}
                         if args.stage == 'design' else
                         {'index', 'requirements', 'architecture', 'contracts', 'test_plan', 'review_log',
                          'risk_register', 'baseline'} if args.stage == 'merge' else
                         set(load_cfg(root)['document_map']))
        cfg = load_cfg(root)
        critical_paths = {cfg['document_map'].get(k) for k in critical_keys}
        for x in result['checks']:
            if x['code'] in {'NO_REQ', 'UNCOVERED_REQ', 'TRACE_ORPHAN'}:
                blockers.append(x)
            elif x['code'] == 'PLACEHOLDER' and x.get('path') in critical_paths:
                blockers.append(x)
        if args.stage in ('merge', 'release') and result['counts']['trace_rows'] == 0:
            blockers.append({'code': 'NO_TRACE', 'message': 'no linked requirement/test entries'})
        if args.stage == 'release':
            if not git(root, 'rev-parse', 'HEAD'):
                blockers.append({'code': 'NO_GIT_SHA', 'message': 'cannot determine immutable source baseline (Git HEAD)'})
            status = git(root, 'status', '--porcelain', '--untracked-files=no')
            if status is None or status:
                blockers.append({'code': 'DIRTY_TREE', 'message': 'tracked working tree unclean or Git state unknown'})
    summary = {
        'stage': args.stage,
        'local_preflight': 'BLOCKED' if blockers else 'READY_FOR_HUMAN_REVIEW',
        'blocking_findings': blockers,
        'external_status': 'UNKNOWN',
        'external_checks_required': {
            'design': ['owner/qualified reviewer accepts requirements, risks and design status'],
            'merge': ['real required CI results at correct SHA', 'PR approval and branch protection status'],
            'release': ['trusted build artifact hashes', 'target/environment verification', 'release owner approval', 'rollback evidence']
        }[args.stage],
        'disclaimer': 'This command is a local preflight. It never approves a merge, production release, hardware verification or compliance.'
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 2 if blockers else 0


def main() -> int:
    p = argparse.ArgumentParser(description='devflow_guide: safe project discovery, initialization and offline preflight')
    subs = p.add_subparsers(dest='cmd', required=True)
    q = subs.add_parser('inspect', help='read-only heuristic project classification and context')
    q.add_argument('--root', type=Path, default=Path('.'))
    q.set_defaults(func=lambda a: (print(json.dumps(inspect(a.root.resolve()), indent=2, ensure_ascii=False)), 0)[1])
    q = subs.add_parser('init', help='create ONLY missing governance docs after explicit authorization')
    q.add_argument('--root', type=Path, default=Path('.'))
    q.add_argument('--profile', choices=KINDS, required=True)
    q.add_argument('--assurance', choices=ASSURANCES, default='standard')
    q.add_argument('--name', help='human-readable project name')
    q.add_argument('--dry-run', action='store_true', help='no writes; show exact changes')
    q.add_argument('--adopt', action='store_true', help='map existing docs in a non-empty repository')
    q.set_defaults(func=cmd_init)
    q = subs.add_parser('audit', help='read-only structure, traceability and docs/code drift scan')
    q.add_argument('--root', type=Path, default=Path('.'))
    q.add_argument('--base', help='optional Git diff baseline for docs/code co-change review')
    q.add_argument('--strict', action='store_true', help='nonzero exit for warnings')
    q.add_argument('--json', action='store_true', help='machine-readable result')
    q.set_defaults(func=cmd_audit)
    q = subs.add_parser('gate', help='local design/merge/release preflight, NEVER external approval')
    q.add_argument('--root', type=Path, default=Path('.'))
    q.add_argument('--stage', choices=['design', 'merge', 'release'], required=True)
    q.add_argument('--base', help='optional Git baseline')
    q.set_defaults(func=cmd_gate)
    a = p.parse_args()
    return a.func(a)

if __name__ == '__main__':
    sys.exit(main())
