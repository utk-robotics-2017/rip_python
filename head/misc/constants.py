import json


class Constants(object):
    kEpsilon = 1E-9
    _shared_state = {}

    def __init__(self, **kwargs):
        self.__dict__ = self._shared_state
        if not hasattr(self, "config_loaded"):
            self.load_config()

    def load_config(self):
        with open("/Robot/robot.json") as f:
            config = json.loads(f.read())
        for a, b in iter(config.items()):
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)
        self.config_loaded = True


class obj(object):
    def __init__(self, d):
        for a, b in iter(d.items()):
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)
