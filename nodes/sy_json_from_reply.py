"""JSON From Reply SY: finds the first JSON object or list inside a chatty reply and returns it as compact JSON."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000


def find_balanced(text, start):
    """Pure function. From text[start] (a { or [), return the end index (exclusive) of the balanced block, or -1."""
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                return i + 1
            if depth < 0:
                return -1
    return -1


def remove_trailing_commas(block):
    """Pure function. Removes a comma right before } or ], but never inside a string."""
    out = []
    in_str = False
    esc = False
    n = len(block)
    i = 0
    while i < n:
        ch = block[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
        elif ch == ",":
            j = i + 1
            while j < n and block[j] in " \t\r\n":
                j += 1
            if j < n and block[j] in "}]":
                i += 1
                continue
            out.append(ch)
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def json_from_reply(text, sorted_keys=False, raise_if_missing=True):
    """Pure function. Returns (compact_json_text, found)."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    pos = 0
    while True:
        starts = [p for p in (text.find("{", pos), text.find("[", pos)) if p >= 0]
        if not starts:
            break
        s = min(starts)
        e = find_balanced(text, s)
        if e > 0:
            block = remove_trailing_commas(text[s:e])
            try:
                value = json.loads(block)
            except ValueError:
                value = None
            else:
                dumped = json.dumps(value, separators=(",", ":"), sort_keys=bool(sorted_keys), ensure_ascii=False)
                return dumped, True
        pos = s + 1
    if raise_if_missing:
        raise ValueError("no valid JSON object or list found in the text. Check the reply, or turn off raise_if_missing.")
    return "", False


class SYJSONFromReply:
    DESCRIPTION = "Finds the first {...} or [...] in a text reply, fixes trailing commas, and gives clean compact JSON."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("json_text", "found")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The reply that contains JSON somewhere inside it."}),
                "sorted_keys": ("BOOLEAN", {"default": False, "tooltip": "On: sort the keys of every object alphabetically."}),
                "raise_if_missing": ("BOOLEAN", {"default": True, "tooltip": "On: stop with an error if no JSON is found. Off: give empty text and found = false."}),
            }
        }

    def run(self, text, sorted_keys=False, raise_if_missing=True):
        return json_from_reply(text, sorted_keys, raise_if_missing)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "JSONFromReply", SYJSONFromReply)
NODE_DISPLAY_NAME_MAPPINGS["SYJSONFromReply"] = "JSON From Reply SY"
