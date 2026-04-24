---
name: improve-tests
description: Find uncovered lines and add or refine tests to improve coverage while keeping tests green.
on: workflow_dispatch
---

# Improve Tests

## Objective
Increase and maintain test coverage for `order_processor.py` while preserving passing tests.

## Steps
1. Run `pytest tests/ --cov=order_processor --cov-report=term-missing -v`.
2. Identify missing lines in `order_processor.py`.
3. Add or update tests under `tests/` to cover missing lines.
4. Re-run `pytest tests/ -v` and the coverage command.
5. Stop only when tests pass and coverage is at least 80%.

## Constraints
- Do not modify production behavior in `order_processor.py` unless required to fix a real defect.
- Prefer minimal, focused test changes.
- Keep mocking at the import location used by the code under test.

## Output
Provide:
- Files changed
- New or updated tests added
- Final test and coverage summary
