# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based CLI tool and reusable GitHub Actions workflow for evaluating which federal health regulations (HIPAA, FDA, FTC, COPPA, etc.) may apply to a health application. It is driven by a `compliance-config.json` provided by the consuming repository.

## Commands

**Package manager:** UV (not pip directly)

```bash
# Install dev dependencies
uv sync --dev

# Run the compliance checker
uv run main.py <path-to-compliance-config.json>

# Lint
uv run pylint main.py
```

There is no build step and no test suite. The tool runs directly with Python 3.13+.

## Architecture

**`main.py`** is the entire application (~460 lines, no external dependencies):
- `ComplianceResult` dataclass — structured container for warnings, recommendations, applicable laws, and resources
- `HealthAppComplianceChecker` class — accepts a parsed config dict; exposes `run_checks()` which calls 8 `_check_*()` methods, one per regulation:
  - `_check_hipaa()` — HIPAA Rules (covered entities, business associates)
  - `_check_fda()` — FDA medical device regulation
  - `_check_information_blocking()` — 21st Century Cures Act
  - `_check_ftc_act()` — FTC Act Section 5
  - `_check_health_breach_notification()` — FTC Health Breach Notification Rule
  - `_check_coppa()` — Children's Online Privacy Protection Act
  - `_check_oarfpa()` — Opioid Addiction Recovery Fraud Prevention Act
  - `_add_general_recommendations()` — Best-practice suggestions always appended
- CLI entry point reads a JSON config file, instantiates the checker, and exits with code `0` (no warnings) or `1` (warnings present)

**`.github/workflows/compliance-check.yaml`** is a reusable workflow (`on: workflow_call`) meant to be called from consuming repositories. It runs `main.py` against a `compliance-config.json` in the calling repo, generates a step summary, and optionally uploads a compliance report artifact.

## Key Conventions

- **Zero runtime dependencies** — only Python standard library (`json`, `argparse`, `sys`, `typing`, `dataclasses`). Keep it that way.
- **Pylint score must be 10/10** — `.pylintrc` sets `fail-under=10`. Run pylint before committing.
- **Python 3.13+** — specified in both `.python-version` and `pyproject.toml`.
- **Exit codes are semantically significant:** `0` = no warnings, `1` = warnings detected. Consuming workflows depend on this.
- GitHub Actions in this repo use pinned SHA hashes for all third-party actions (supply-chain security requirement enforced by OSSF Scorecard).
