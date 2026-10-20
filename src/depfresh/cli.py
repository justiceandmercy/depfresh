import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .parsers import (
    parse_package_json,
    parse_requirements,
    parse_pyproject,
    parse_cargo,
)
from .registry import InMemoryRegistry
from .report import audit


MANIFESTS = {
    "package.json": parse_package_json,
    "requirements.txt": parse_requirements,
    "pyproject.toml": parse_pyproject,
    "Cargo.toml": parse_cargo,
}


def collect_deps(root):
    root = Path(root)
    deps = []
    for name, parser in MANIFESTS.items():
        p = root / name
        if p.exists():
            deps.extend(parser(p.read_text(), source=str(p)))
    return deps


def collect_sources(root):
    root = Path(root)
    texts = []
    for ext in ("*.py", "*.js", "*.ts", "*.tsx", "*.rs"):
        for p in root.rglob(ext):
            if "node_modules" in p.parts or ".git" in p.parts:
                continue
            try:
                texts.append(p.read_text(errors="ignore"))
            except Exception:
                pass
    return texts


def _load_registry(path):
    if not path:
        return InMemoryRegistry()
    return InMemoryRegistry(json.loads(Path(path).read_text()))


def cmd_scan(args):
    deps = collect_deps(args.path)
    reg = _load_registry(args.registry)
    sources = collect_sources(args.path) if args.check_unused else []
    findings = audit(deps, reg, source_texts=sources)
    if args.format == "json":
        print(json.dumps([
            {"kind": f.kind, "name": f.dependency.name,
             "ecosystem": f.dependency.ecosystem, "detail": f.detail,
             "severity": f.severity} for f in findings
        ], indent=2))
    else:
        if not findings:
            print("No findings.")
        for f in findings:
            print(f"[{f.severity}] {f.kind}: {f.detail}")
    return 0


def cmd_check(args):
    deps = collect_deps(args.path)
    reg = _load_registry(args.registry)
    sources = collect_sources(args.path) if args.check_unused else []
    findings = audit(deps, reg, source_texts=sources)
    errors = [f for f in findings if f.severity == "error"]
    if len(errors) > args.max_errors:
        for f in findings:
            print(f"[{f.severity}] {f.kind}: {f.detail}")
        return 1
    return 0


def cmd_plugins(args):
    print("No plugins loaded. (Discovery not implemented in v0.1)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="depfresh")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_scan = sub.add_parser("scan")
    p_scan.add_argument("path", nargs="?", default=".")
    p_scan.add_argument("--format", choices=["text", "json"], default="text")
    p_scan.add_argument("--check-unused", action="store_true")
    p_scan.add_argument("--registry", help="JSON file with registry data")
    p_scan.set_defaults(func=cmd_scan)
    p_check = sub.add_parser("check")
    p_check.add_argument("path", nargs="?", default=".")
    p_check.add_argument("--max-errors", type=int, default=0)
    p_check.add_argument("--check-unused", action="store_true")
    p_check.add_argument("--registry", help="JSON file with registry data")
    p_check.set_defaults(func=cmd_check)
    p_plugins = sub.add_parser("plugins")
    p_plugins.set_defaults(func=cmd_plugins)
    args = parser.parse_args(argv)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
