# devflow_guide

Developer Workflow Governance · Practical Guide

软件工程流程治理 Skill，供 Codex 以及兼容 Agent Skills 的开发代理使用。覆盖嵌入式（Linux / MCU / DSP / ISP）、Web / API、桌面和移动应用，并按失败后果选择 lite、standard 或 high。

A software-engineering governance skill for Codex and other Agent Skills-compatible coding agents. It covers embedded Linux, MCU, DSP, and ISP work, Web and API services, and desktop or mobile applications. Rigor is chosen from the consequence of failure: lite, standard, or high.

## Manuals

- [中文手册](manual/zh/devflow_guide.html)
- [English manual](manual/en/devflow_guide.html)

两份手册是同一份离线单文件 HTML，版式和交互一致，可在浏览器中直接打开，不依赖第三方脚本。

The two manuals are the same offline single-file HTML. Layout and interaction match. Open either file in a browser. There is no third-party script.

## Install

Copy the whole `devflow-guide/` directory. Do not copy only `SKILL.md`.

- Project: `.agents/skills/devflow-guide/`
- User: `~/.agents/skills/devflow-guide/`

The folder name and the `name` in `SKILL.md` are `devflow-guide`. The display name is `devflow_guide`.

## Layout

- `devflow-guide/` — skill entry, references, templates, and `scripts/devflow.py`
- `manual/zh/`、`manual/en/` — Chinese and English offline manuals
- `examples/` — format samples, not evidence from a real project
- `VALIDATION_REPORT.md` — local checks recorded for v1.0.0

## First use

Run from this repository and replace `<repo>`. On Windows the command may be `python` or `py -3`. Python 3.9+ is required. Git is optional.

```bash
python devflow-guide/scripts/devflow.py inspect --root <repo>
python devflow-guide/scripts/devflow.py init --root <repo> --profile embedded --assurance standard --dry-run
```

Review the files the dry run would create. Only then remove `--dry-run`. An existing repository must add `--adopt`, and the dry run must be reviewed before initialization. The CLI does not overwrite an existing `.devflow.json`, source, documents, CI, or Git history, and it does not create a missing root directory.

## Review and gates

```bash
python devflow-guide/scripts/devflow.py audit --root <repo>
python devflow-guide/scripts/devflow.py gate --root <repo> --stage design
python devflow-guide/scripts/devflow.py gate --root <repo> --stage merge
python devflow-guide/scripts/devflow.py gate --root <repo> --stage release
```

`audit` checks structure, paths, unfilled placeholders, trace rows, and Git document-change hints. It does not build or test the project. `gate` is a local preflight. `READY_FOR_HUMAN_REVIEW` is not remote CI, hardware acceptance, human review, or release approval. External state stays `UNKNOWN` until it is checked on the system that actually owns it.

`audit` returns 2 on a structural error, 1 for warnings when `--strict` is set, and 0 otherwise. `gate` returns 2 when it blocks.

## Boundaries

This package is not an ISO 26262, ASPICE, or IEC 62304 certification system, and it does not prove that code or hardware is free of defects. Profile detection is advisory. Mixed Web, Qt, and driver repositories need a human-selected scope. `verified` in the CSV is a self-reported status unless a trusted tool or approval record says otherwise.

## Self-test

```bash
python devflow-guide/scripts/test_devflow.py
```

Specification: <https://agentskills.io/specification>

License: GPL-3.0. See [LICENSE](LICENSE).
