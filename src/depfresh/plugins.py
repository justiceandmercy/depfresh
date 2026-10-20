class PluginManager:
    def __init__(self):
        self._hooks = {}

    def register(self, hook, fn):
        self._hooks.setdefault(hook, []).append(fn)

    def run(self, hook, *args, **kwargs):
        results = []
        for fn in self._hooks.get(hook, []):
            results.append(fn(*args, **kwargs))
        return results

    def list_hooks(self):
        return sorted(self._hooks)
