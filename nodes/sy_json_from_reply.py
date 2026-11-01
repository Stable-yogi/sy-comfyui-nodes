"""JSON From Reply SY: finds the first JSON object or list inside a chatty reply and returns it as compact JSON."""
import ast
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
WHICH = ("first", "last", "largest")
_FAIL = object()


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


def _parse_block(block, python_style):
    try:
        return json.loads(block)
    except ValueError:
        pass
    if python_style:
        try:
            value = ast.literal_eval(block)
            json.dumps(value)
            return value
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
            pass
    return _FAIL


def extract_blocks(text, python_style=False, limit=0):
    """Pure function. Every valid JSON object or list in the text, in order (limit 0 = all). Inner blocks of a found block are not repeated."""
    pos = 0
    found = []
    while True:
        starts = [p for p in (text.find("{", pos), text.find("[", pos)) if p >= 0]
        if not starts:
            break
        s = min(starts)
        e = find_balanced(text, s)
        if e > 0:
            value = _parse_block(remove_trailing_commas(text[s:e]), python_style)
            if value is not _FAIL:
                found.append(value)
                if limit and len(found) >= limit:
                    break
                pos = e
                continue
        pos = s + 1
    return found


def describe_value(value, number=1, total=1):
    """Pure function. A plain line about the JSON that was found."""
    if isinstance(value, dict):
        what = "an object with %d key%s" % (len(value), "" if len(value) == 1 else "s")
    else:
        what = "a list with %d item%s" % (len(value), "" if len(value) == 1 else "s")
    return "Found %s (block %d of %d)." % (what, number, total)


def json_from_reply_info(text, sorted_keys=False, raise_if_missing=True, which="first", pretty=False, python_style=False):
    """Pure function. Returns (json_text, found, info). which: first, last or largest of the JSON blocks in the reply."""
    if which not in WHICH:
        raise ValueError("which must be one of: %s, got %r" % (", ".join(WHICH), which))
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    blocks = extract_blocks(text, python_style, 1 if which == "first" else 0)
    if blocks:
        def dump(v):
            if pretty:
                return json.dumps(v, indent=2, sort_keys=bool(sorted_keys), ensure_ascii=False)
            return json.dumps(v, separators=(",", ":"), sort_keys=bool(sorted_keys), ensure_ascii=False)
        if which == "first":
            index = 0
        elif which == "last":
            index = len(blocks) - 1
        else:
            index = max(range(len(blocks)), key=lambda i: len(json.dumps(blocks[i])))
        # the true total is only known when we looked at all blocks
        total = len(blocks) if which != "first" else len(extract_blocks(text, python_style))
        return dump(blocks[index]), True, describe_value(blocks[index], index + 1, total)
    if raise_if_missing:
        raise ValueError("no valid JSON object or list found in the text. Check the reply, or turn off raise_if_missing.")
    return "", False, "No JSON found in the text."


def json_from_reply(text, sorted_keys=False, raise_if_missing=True, which="first", pretty=False, python_style=False):
    """Pure function. Returns (compact_json_text, found)."""
    out = json_from_reply_info(text, sorted_keys, raise_if_missing, which, pretty, python_style)
    return out[0], out[1]


class SYJSONFromReply:
    DESCRIPTION = ("Finds the JSON {...} or [...] in a chatty text reply, fixes trailing commas, and gives clean JSON. Pick the first, the last "
                   "or the biggest block, get it pretty-printed, and optionally repair Python-style replies (single quotes, True/None). "
                   "An info line says what was found.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("json_text", "found", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The reply that contains JSON somewhere inside it."}),
                "sorted_keys": ("BOOLEAN", {"default": False, "tooltip": "On: sort the keys of every object alphabetically."}),
                "raise_if_missing": ("BOOLEAN", {"default": True, "tooltip": "On: stop with an error if no JSON is found. Off: give empty text and found = false."}),
            },
            "optional": {
                "which": (list(WHICH), {"default": "first", "tooltip": "When the reply holds several JSON blocks: take the first, the last (often the final answer) or the biggest."}),
                "pretty": ("BOOLEAN", {"default": False, "tooltip": "On: give the JSON spread over several lines, easier to read. Off: one compact line."}),
                "python_style": ("BOOLEAN", {"default": False, "tooltip": "On: also accept replies written Python style, like {'a': True, 'b': None}."}),
            },
        }

    def run(self, text, sorted_keys=False, raise_if_missing=True, which="first", pretty=False, python_style=False):
        return json_from_reply_info(text, sorted_keys, raise_if_missing, which, pretty, python_style)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "JSONFromReply", SYJSONFromReply)
NODE_DISPLAY_NAME_MAPPINGS["SYJSONFromReply"] = "JSON From Reply SY"
