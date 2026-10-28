"""SY Nodes for ComfyUI by Stable Yogi. MIT. Loads every nodes/sy_*.py module."""
import importlib
import os

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./js"

_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nodes")
for _fn in sorted(os.listdir(_dir)):
    if _fn.startswith("sy_") and _fn.endswith(".py"):
        _mod = importlib.import_module("%s.nodes.%s" % (__name__, _fn[:-3]))
        NODE_CLASS_MAPPINGS.update(getattr(_mod, "NODE_CLASS_MAPPINGS", {}))
        NODE_DISPLAY_NAME_MAPPINGS.update(getattr(_mod, "NODE_DISPLAY_NAME_MAPPINGS", {}))

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
