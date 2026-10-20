import json
import re
import tomllib

from .models import Dependency


def parse_package_json(text, source="package.json"):
    data = json.loads(text)
    deps = []
    for section, dev in (("dependencies", False), ("devDependencies", True)):
        for name, spec in (data.get(section) or {}).items():
            version = spec.lstrip("^~>=< ") if isinstance(spec, str) else str(spec)
            deps.append(Dependency(name=name, version=version, ecosystem="npm", dev=dev, source=source))
    return deps


def parse_requirements(text, source="requirements.txt"):
    deps = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = re.match(r"^([A-Za-z0-9_.-]+)\s*([<>=!~].*)?$", line)
        if not m:
            continue
        name = m.group(1)
        spec = (m.group(2) or "").strip()
        version = spec.lstrip("=<>!~ ") if spec else ""
        deps.append(Dependency(name=name, version=version, ecosystem="pypi", source=source))
    return deps


def _clean_version(v):
    if not v:
        return ""
    if isinstance(v, dict):
        v = v.get("version", "")
    return str(v).strip().lstrip("=<>!~^ ")


def _split_pep508(spec):
    m = re.match(r"^([A-Za-z0-9_.-]+)\s*(.*)$", spec.strip())
    name = m.group(1)
    version = m.group(2).strip()
    return name, _clean_version(version)


def parse_pyproject(text, source="pyproject.toml"):
    data = tomllib.loads(text)
    deps = []
    project = data.get("project", {}) or {}
    for spec in project.get("dependencies", []) or []:
        name, version = _split_pep508(spec)
        deps.append(Dependency(name=name, version=version, ecosystem="pypi", source=source))
    for group in (project.get("optional-dependencies") or {}).values():
        for spec in group:
            name, version = _split_pep508(spec)
            deps.append(Dependency(name=name, version=version, ecosystem="pypi", dev=True, source=source))
    poetry = data.get("tool", {}).get("poetry", {}) or {}
    for name, spec in (poetry.get("dependencies") or {}).items():
        if name.lower() == "python":
            continue
        version = spec if isinstance(spec, str) else (spec.get("version", "") if isinstance(spec, dict) else "")
        deps.append(Dependency(name=name, version=_clean_version(version), ecosystem="pypi", source=source))
    for name, spec in (poetry.get("dev-dependencies") or {}).items():
        version = spec if isinstance(spec, str) else (spec.get("version", "") if isinstance(spec, dict) else "")
        deps.append(Dependency(name=name, version=_clean_version(version), ecosystem="pypi", dev=True, source=source))
    return deps


def parse_cargo(text, source="Cargo.toml"):
    data = tomllib.loads(text)
    deps = []
    for section, dev in (("dependencies", False), ("dev-dependencies", True)):
        for name, spec in (data.get(section) or {}).items():
            version = spec if isinstance(spec, str) else (spec.get("version", "") if isinstance(spec, dict) else "")
            deps.append(Dependency(name=name, version=str(version), ecosystem="cargo", dev=dev, source=source))
    return deps
