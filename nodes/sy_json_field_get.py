"""JSON Field Get SY: reads one value from a JSON text using a path like a.b.0."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class MissingPath(ValueError):
    """The path does not exist in the JSON (a different problem from bad JSON)."""


def _parse(json_text):
    """Loads JSON; if that fails, tries again without a ``` fence around it (common in chat replies)."""
    try:
        return json.loads(json_text)
    except ValueError as first:
        t = json_text.strip()
        if t.startswith("```"):
            lines = t.split("\n")[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            try:
                return json.loads("\n".join(lines))
            except ValueError:
                pass
        raise ValueError("json_text is not valid JSON (%s): fix the JSON first" % first)


def kind_of(value):
    """Pure function. A plain word for the type of a JSON value."""
    if value is None:
        return "empty"
    if isinstance(value, bool):
        return "true/false"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "text"
    if isinstance(value, list):
        return "list"
    return "object"


def get_field(json_text, path):
    """Pure function. Path parts are split by '.'; a number picks a list item (or a key made of digits).
    Returns the value as text: strings as they are, everything else as JSON."""
    return get_field_ex(json_text, path)[0]


def get_field_ex(json_text, path, default=None):
    """Pure function. Returns (text, found, kind). When default is not None, a path that does not exist gives (default, False, 'default')."""
    try:
        return _walk(json_text, path)
    except MissingPath:
        if default is None:
            raise
        return default, False, "default"


def _walk(json_text, path):
    if not isinstance(json_text, str):
        raise ValueError("json_text must be text, got %s" % type(json_text).__name__)
    if not isinstance(path, str):
        raise ValueError("path must be text, got %s" % type(path).__name__)
    node = _parse(json_text)
    path = path.strip()
    walked = []
    if path:
        for part in path.split("."):
            where = ".".join(walked) or "the top"
            if part == "":
                raise ValueError("path %r has an empty part: write it like a.b.0" % path)
            if isinstance(node, dict):
                if part not in node:
                    raise MissingPath("key %r not found at %s: available keys are %s" % (part, where, ", ".join(map(str, node)) or "(none)"))
                node = node[part]
            elif isinstance(node, list):
                try:
                    idx = int(part)
                except ValueError:
                    raise MissingPath("at %s the value is a list: use a number, not %r" % (where, part))
                if idx < -len(node) or idx >= len(node):
                    raise MissingPath("index %d is out of range at %s: the list has %d items" % (idx, where, len(node)))
                node = node[idx]
            else:
                raise MissingPath("cannot go into %r at %s: that value is not an object or list" % (part, where))
            walked.append(part)
    if isinstance(node, str):
        return node, True, "text"
    return json.dumps(node, ensure_ascii=False), True, kind_of(node)


class SYJSONFieldGet:
    DESCRIPTION = ("Reads one value from a JSON text. The path is dots between keys, and numbers pick list items, like a.b.0. A missing key "
                   "can give a fallback value instead of stopping, a JSON wrapped in ``` fences is accepted, and it also tells if the "
                   "key was found and what type the value is.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("value", "found", "kind")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "tooltip": "The JSON text to read from."}),
                "path": ("STRING", {"default": "", "tooltip": "Keys joined by dots, numbers for list items, like a.b.0. Empty gives it all."}),
            },
            "optional": {
                "if_missing": (["error", "use default"], {"default": "error", "tooltip": "What to do when the path is not in the JSON: stop with a message, or give the default value."}),
                "default_value": ("STRING", {"default": "", "tooltip": "Value given when the path is missing and if_missing is use default. Can be empty."}),
            },
        }

    def run(self, json_text, path, if_missing="error", default_value=""):
        default = default_value if if_missing == "use default" else None
        return get_field_ex(json_text, path, default)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "JSONFieldGet", SYJSONFieldGet)
NODE_DISPLAY_NAME_MAPPINGS["SYJSONFieldGet"] = "JSON Field Get SY"
