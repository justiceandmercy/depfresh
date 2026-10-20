from depfresh.models import Dependency
from depfresh.registry import InMemoryRegistry
from depfresh.report import audit, is_outdated, scan_imports


def test_is_outdated():
    assert is_outdated("1.0.0", "2.0.0") is True
    assert is_outdated("2.0.0", "2.0.0") is False
    assert is_outdated("", "2.0.0") is False


def test_outdated_finding():
    dep = Dependency(name="requests", version="2.0.0", ecosystem="pypi")
    reg = InMemoryRegistry({("pypi", "requests"): {"latest": "2.31.0", "license": "Apache-2.0"}})
    findings = audit([dep], reg, source_texts=[])
    assert any(f.kind == "outdated" for f in findings)


def test_risky_license():
    dep = Dependency(name="gpllib", version="1.0.0", ecosystem="pypi")
    reg = InMemoryRegistry({("pypi", "gpllib"): {"latest": "1.0.0", "license": "GPL-3.0"}})
    findings = audit([dep], reg, source_texts=[])
    assert any(f.kind == "risky-license" and f.severity == "error" for f in findings)


def test_unused_detection():
    dep = Dependency(name="unused-pkg", version="1.0.0", ecosystem="pypi")
    reg = InMemoryRegistry({("pypi", "unused-pkg"): {"latest": "1.0.0", "license": "MIT"}})
    findings = audit([dep], reg, source_texts=["import os\n"])
    assert any(f.kind == "unused" for f in findings)


def test_used_not_flagged():
    dep = Dependency(name="used-pkg", version="1.0.0", ecosystem="pypi")
    reg = InMemoryRegistry({("pypi", "used-pkg"): {"latest": "1.0.0", "license": "MIT"}})
    findings = audit([dep], reg, source_texts=["import used_pkg\n"])
    assert not any(f.kind == "unused" for f in findings)


def test_scan_imports():
    assert "react" in scan_imports(["import React from 'react'", "const x = require('lodash')"])
