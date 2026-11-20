# Contributing

1. Fork/clone and create a branch. Never push to the upstream repository.
2. Install the dev extras: `python -m pip install -e ".[dev]"`.
3. Make the change with tests. All public behaviour must be covered by assertions with
   known-valid and known-invalid vectors — no stubs, TODOs, or skipped tests.
4. Before opening a PR run, all green:

   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m mypy
   python -m coverage run -m pytest
   python -m coverage report
   python -m build
   ```

5. Commit with a Conventional Commit message (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).

Gramatical references for numbers are listed at the top of `src/falabr/numbers.py`.
When changing number spelling, update the corresponding table cases with a source comment.
