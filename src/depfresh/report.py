import re

from .models import Dependency, Finding

DENIED_LICENSES = {"GPL-3.0", "AGPL-3.0", "GPL-2.0"}
RISKY_LICENSES = {"UNKNOWN", "", None}


def _vkey(v):
    parts = []
    for chunk in str(v).replace("-", ".").split("."):
        try:
            parts.append(int(chunk))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_outdated(current, latest):
    if not current or not latest:
        return False
    return _vkey(current) < _vkey(latest)


def normalize_import_name(name, ecosystem):
    if ecosystem == "npm" and name.startswith("@"):
        name = name.split("/")[-1]
    return name.replace("-", "_").lower()


def scan_imports(source_texts):
    found = set()
    for text in source_texts:
        for m in re.finditer(r"(?:^|\n)\s*(?:import|from)\s+([A-Za-z0-9_.-]+)", text):
            found.add(m.group(1).split(".")[0].lower().replace("-", "_"))
        for m in re.finditer(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)", text):
            mod = m.group(1).split("/")[0]
            found.add(mod.lower().replace("-", "_"))
    return found


def audit(deps, registry, source_texts=None, denied=None, risky_threshold=True):
    denied = denied if denied is not None else DENIED_LICENSES
    found_imports = scan_imports(source_texts or [])
    findings = []
    for d in deps:
        latest = registry.latest_version(d.name, d.ecosystem)
        if latest and is_outdated(d.version, latest):
            findings.append(Finding("outdated", d, f"{d.name}: {d.version} -> {latest}", "warning"))
        lic = registry.license_for(d.name, d.ecosystem, d.version or (latest or ""))
        if lic in denied:
            findings.append(Finding("risky-license", d, f"{d.name} uses {lic}", "error"))
        elif lic in RISKY_LICENSES and risky_threshold:
            findings.append(Finding("unknown-license", d, f"{d.name} license unknown", "info"))
        if not d.dev and found_imports:
            imp = normalize_import_name(d.name, d.ecosystem)
            if imp not in found_imports:
                findings.append(Finding("unused", d, f"{d.name} not imported in source", "info"))
    return findings
