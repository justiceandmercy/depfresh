# depfresh

Audit project dependencies for staleness, license risk, and unused packages across
npm, pip (requirements/pyproject), and cargo ecosystems.

## Features

- Parse `package.json`, `requirements.txt`, `pyproject.toml`, and `Cargo.toml`.
- Compare declared versions against a registry (pluggable, in-memory for tests/offline).
- Flag outdated, unused (not imported in source), and risky-licensed dependencies.
- Text and JSON output; `check` subcommand for CI gating.
- Plugin hook points for custom parsers/rules.
- No network required to run tests; registries are injectable.

## Install

```bash
pip install -e .
```

## Usage

```bash
depfresh scan .
depfresh scan . --format json --check-unused
depfresh check . --max-errors 0
depfresh plugins
```

Provide registry data as JSON via `--registry`:

```json
{
  "(\"pypi\", \"requests\")": {"latest": "2.32.0", "license": "Apache-2.0"}
}
```

## Architecture

- `models.py` - dataclasses `Dependency`, `Finding`.
- `parsers.py` - manifest parsers returning `Dependency` lists.
- `registry.py` - `RegistryClient` protocol + `InMemoryRegistry`.
- `report.py` - audit logic: outdated, license risk, unused detection.
- `plugins.py` - hook-based plugin manager.
- `cli.py` - argparse subcommands.

## License

MIT
