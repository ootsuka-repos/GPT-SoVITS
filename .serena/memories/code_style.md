# Code Style & Conventions
- Python modules follow traditional snake_case naming; class names use PascalCase. Type hints are sparse—most functions rely on dynamic typing.
- Docstrings are uncommon; code typically explains itself via descriptive variable names. Add concise comments only when behaviour is non-obvious.
- Logging/printing uses standard `print` or `logger.info`; no enforced logging framework beyond module-specific choices.
- Configuration values are centralized in `config/config.py` and environment variables; keep new settings consistent with existing patterns.
- When extending CLI scripts, prefer `argparse` (as seen in utilities under `tools/`) and maintain compatibility with both Windows and Unix paths via `os.path`/`pathlib`.
- Repo does not enforce auto-formatting; adhere to existing spacing/indentation (4 spaces) and avoid introducing trailing whitespace.