"""JSON Prompt Builder SY: turns 'key: value' lines into a valid JSON string, with correct escaping."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def _auto_type(value):
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low == "null":
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        number = float(value)
        if number == number and number not in (float("inf"), float("-inf")):
            return number
    except ValueError:
        pass
    return value


def build_json(lines_text, auto_types=True, indent=2):
    """Pure function. Each line is 'key: value' (or 'key=value'). Blank lines and lines starting with # are skipped."""
    if not isinstance(lines_text, str):
        raise ValueError("lines must be text, got %s" % type(lines_text).__name__)
    indent = int(indent)
    if indent < 0 or indent > 8:
        raise ValueError("indent must be 0 to 8, got %d" % indent)
    data = {}
    for number, raw in enumerate(lines_text.split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cut = -1
        for sep in (":", "="):
            pos = line.find(sep)
            if pos != -1 and (cut == -1 or pos < cut):
                cut = pos
        if cut == -1:
            raise ValueError("line %d has no ':' or '=': write it as key: value" % number)
        key = line[:cut].strip()
        value = line[cut + 1:].strip()
        if not key:
            raise ValueError("line %d has an empty key: write it as key: value" % number)
        if key in data:
            raise ValueError("line %d repeats the key %r: use each key once" % (number, key))
        data[key] = _auto_type(value) if auto_types else value
    if not data:
        raise ValueError("no key: value lines found: write at least one line")
    return json.dumps(data, ensure_ascii=False, indent=indent if indent > 0 else None)


class SYJSONPromptBuilder:
    DESCRIPTION = "Turns lines like 'subject: a fox' into a valid JSON text. Quotes and special characters are escaped for you."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lines": ("STRING", {"multiline": True, "default": "subject: a fox\nmood: calm", "tooltip": "One key: value per line. Lines starting with # are skipped."}),
                "auto_types": ("BOOLEAN", {"default": True, "tooltip": "On: true, false, null and numbers become real JSON values. Off: all text."}),
                "indent": ("INT", {"default": 2, "min": 0, "max": 8, "tooltip": "Spaces per level. 0 gives one compact line."}),
            }
        }

    def run(self, lines, auto_types, indent):
        return (build_json(lines, auto_types, indent),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "JSONPromptBuilder", SYJSONPromptBuilder)
NODE_DISPLAY_NAME_MAPPINGS["SYJSONPromptBuilder"] = "JSON Prompt Builder SY"
