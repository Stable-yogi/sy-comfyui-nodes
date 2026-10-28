"""Show Text SY: shows any text or number inside the node and passes it on unchanged."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class AnyType(str):
    """ComfyUI any-type trick: never reports a type mismatch."""

    def __ne__(self, other):
        return False


ANY = AnyType("*")


def to_display(value):
    """Pure function. Turns text, numbers, true/false, lists and dicts into one display string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(to_display(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, default=str, indent=2)
    return str(value)


class SYShowText:
    DESCRIPTION = "Shows any text or number inside the node so you can read it. The value also passes through to the output."
    CATEGORY = category("Text")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": (ANY, {"tooltip": "Any text or number to show. It also comes out as text on the output."})}}

    def run(self, value):
        text = to_display(value)
        return {"ui": {"text": [text]}, "result": (text,)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ShowText", SYShowText)
NODE_DISPLAY_NAME_MAPPINGS["SYShowText"] = "Show Text SY"
