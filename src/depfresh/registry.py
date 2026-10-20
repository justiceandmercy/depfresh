from typing import Optional, Dict, Tuple


class RegistryClient:
    """Protocol-ish base; implement latest_version and license_for."""

    def latest_version(self, name: str, ecosystem: str) -> Optional[str]:
        raise NotImplementedError

    def license_for(self, name: str, ecosystem: str, version: str) -> Optional[str]:
        raise NotImplementedError


class InMemoryRegistry(RegistryClient):
    def __init__(self, data=None):
        # data: dict mapping (ecosystem, name) -> {latest, license}
        self.data: Dict[Tuple[str, str], dict] = {}
        if data:
            for k, v in data.items():
                # allow string keys like '("pypi", "requests")' already evaluated by caller
                self.data[k] = v

    def latest_version(self, name, ecosystem):
        entry = self.data.get((ecosystem, name))
        return entry.get("latest") if entry else None

    def license_for(self, name, ecosystem, version):
        entry = self.data.get((ecosystem, name))
        if not entry:
            return None
        return entry.get("license")
