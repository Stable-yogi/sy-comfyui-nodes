# Node template

Copy this to `nodes/sy_<snake>.py`. Replace `Thing`.

```python
"""Thing SY: one line about what it does."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def do_thing(value):
    """Pure function. All the logic lives here."""
    return value


class SYThing:
    DESCRIPTION = "One or two plain sentences."
    CATEGORY = category("Utility")   # Image Text Values Logic Resize Utility Editors Notes
    FUNCTION = "run"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("INT", {"default": 0, "min": 0, "max": 2 ** 31})}}

    def run(self, value):
        return (do_thing(value),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Thing", SYThing)
```

Test file `tests/test_sy_thing.py`:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_thing as m

def run():
    assert m.do_thing(3) == 3
    return 1  # number of checks
```
