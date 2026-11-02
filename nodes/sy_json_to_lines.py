"""JSON To Lines SY: turns JSON text into plain lines, one value per line."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FORMATS = ["key: value", "key = value", "value only", "dotted.path: value"]


def _compact(value, sort_keys):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False, sort_keys=sort_keys)


def _scalar(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, str):
        return v.replace("\r", "\\r").replace("\n", "\\n")
    return json.dumps(v)


def _line(fmt, key, value):
    if fmt == "value only" or key == "":
        return value
    if fmt == "key = value":
        return "%s = %s" % (key, value)
    return "%s: %s" % (key, value)


def json_to_lines(value, fmt="key: value", max_depth=4, sort_keys=False):
    """Pure function. Returns a list of lines.
    Plain formats use the last key name (lists: key[0]); the dotted format uses the whole path (path.0).
    A top-level object or list is depth 1; containers nested deeper than max_depth are written as compact JSON."""
    if fmt not in FORMATS:
        raise ValueError("format must be one of: %s (got %r)" % (", ".join(FORMATS), fmt))
    max_depth = int(max_depth)
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1, got %d" % max_depth)
    dotted = fmt == "dotted.path: value"
    out = []

    def walk(v, key, path, depth):
        if isinstance(v, (dict, list)):
            if depth > max_depth or len(v) == 0:
                out.append(_line(fmt, path if dotted else key, _compact(v, sort_keys)))
                return
            if isinstance(v, dict):
                items = sorted(v.items(), key=lambda kv: kv[0]) if sort_keys else list(v.items())
                for k, child in items:
                    walk(child, k, (path + "." + k) if path else k, depth + 1)
            else:
                for i, child in enumerate(v):
                    walk(child, "%s[%d]" % (key, i), (path + "." + str(i)) if path else str(i), depth + 1)
        else:
            out.append(_line(fmt, path if dotted else key, _scalar(v)))

    walk(value, "", "", 1)
    return out


def parse_json(text):
    """Pure function. json.loads with a plain error message that says where the problem is."""
    if not isinstance(text, str) or text.strip() == "":
        raise ValueError("Invalid JSON: the text is empty. Paste some JSON")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON: line %d, column %d: %s" % (e.lineno, e.colno, e.msg))
    except RecursionError:
        raise ValueError("Invalid JSON: it is nested too deeply to read")


class SYJSONToLines:
    DESCRIPTION = ("Turns JSON text into plain lines, one value per line. Lists become key[0], key[1]. "
                   "Very deep parts are written as short one-line JSON.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "line_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "tooltip": "The JSON to turn into lines."}),
                "format": (FORMATS, {"default": "key: value", "tooltip": "How each line looks. Dotted shows the whole path, like a.b.0."}),
                "max_depth": ("INT", {"default": 4, "min": 1, "max": 10, "tooltip": "Levels to open up. Deeper parts become one line of JSON."}),
                "sort_keys": ("BOOLEAN", {"default": False, "tooltip": "On: list the keys in alphabetical order instead of file order."}),
                "on_error": (["raise", "empty text"], {"default": "raise", "tooltip": "What to do with bad JSON: stop with a message, or give empty text."}),
            }
        }

    def run(self, json_text, format, max_depth, sort_keys, on_error):
        try:
            lines = json_to_lines(parse_json(json_text), format, max_depth, sort_keys)
        except ValueError:
            if on_error == "empty text":
                return ("", 0)
            raise
        return ("\n".join(lines), len(lines))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "JSONToLines", SYJSONToLines)
NODE_DISPLAY_NAME_MAPPINGS["SYJSONToLines"] = "JSON To Lines SY"
