from dataclasses import dataclass, field
from typing import Literal, Optional

Ecosystem = Literal["npm", "pypi", "cargo"]


@dataclass
class Dependency:
    name: str
    version: str
    ecosystem: Ecosystem
    dev: bool = False
    source: str = ""


@dataclass
class Finding:
    kind: str
    dependency: Dependency
    detail: str
    severity: str = "warning"
