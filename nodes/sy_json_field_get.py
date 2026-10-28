"""JSON Field Get SY: reads one value from a JSON text using a path like a.b.0."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def get_field(json_text, path):
    """Pure function. Path parts are split by '.'; a number picks a list item (or a key made of digits).
    Returns the value as text: strings as they are, everything else as JSON."""
    if not isinstance(json_text, str):
        raise ValueError("json_text must be text, got %s" % type(json_text).__name__)
    if not isinstance(path, str):
        raise ValueError("path must be text, got %s" % type(path).__name__)
    try:
        node = json.loads(json_text)
    except ValueError as e:
        raise ValueError("json_text is not valid JSON (%s): fix the JSON first" % e)
    path = path.strip()
    walked = []
    if path:
        for part in path.split("."):
            where = ".".join(walked) or "the top"
            if part == "":
                raise ValueError("path %r has an empty part: write it like a.b.0" % path)
            if isinstance(node, dict):
                if part not in node:
                    raise ValueError("key %r not found at %s: available keys are %s" % (part, where, ", ".join(map(str, node)) or "(none)"))
                node = node[part]
            elif isinstance(node, list):
                try:
                    idx = int(part)
                except ValueError:
                    raise ValueError("at %s the value is a list: use a number, not %r" % (where, part))
                if idx < -len(node) or idx >= len(node):
                    raise ValueError("index %d is out of range at %s: the list has %d items" % (idx, where, len(node)))
                node = node[idx]
            else:
                raise ValueError("cannot go into %r at %s: that value is not an object or list" % (part, where))
            walked.append(part)
    if isinstance(node, str):
        return node
    return json.dumps(node, ensure_ascii=False)


class SYJSONFieldGet:
    DESCRIPTION = "Reads one value from a JSON text. The path is dots between keys, and numbers pick list items, like a.b.0."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "tooltip": "The JSON text to read from."}),
                "path": ("STRING", {"default": "", "tooltip": "Keys joined by dots, numbers for list items, like a.b.0. Empty gives it all."}),
            }
        }

    def run(self, json_text, path):
        return (get_field(json_text, path),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "JSONFieldGet", SYJSONFieldGet)
NODE_DISPLAY_NAME_MAPPINGS["SYJSONFieldGet"] = "JSON Field Get SY"
