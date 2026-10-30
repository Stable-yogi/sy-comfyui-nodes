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
        if not getattr(_mod, "SY_REGISTER", True):  # a module that needs a newer ComfyUI says so and is skipped
            print("[SY] %s not loaded, the other SY nodes are fine: %s" % (_fn, getattr(_mod, "SY_NOT_LOADED_REASON", "")))
            continue
        NODE_CLASS_MAPPINGS.update(getattr(_mod, "NODE_CLASS_MAPPINGS", {}))
        NODE_DISPLAY_NAME_MAPPINGS.update(getattr(_mod, "NODE_DISPLAY_NAME_MAPPINGS", {}))

try:  # web helpers for the Save and Load nodes (list folders, open Explorer inside output/input only)
    from .nodes import _sy_folder_api
    _sy_folder_api.register_routes()
except Exception as _err:  # the nodes still work without the buttons
    print("[SY] folder buttons not available:", _err)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
