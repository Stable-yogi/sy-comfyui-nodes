"""Escape Text SY: makes text safe to paste into another place, or reverses it."""
import html
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ["json string", "url", "single line", "html"]
DIRECTIONS = ["escape", "unescape"]
_SAFE = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_HEX = frozenset("0123456789abcdefABCDEF")


def _url_escape(text):
    out = []
    for b in text.encode("utf-8"):
        c = chr(b)
        out.append(c if c in _SAFE else "%%%02X" % b)
    return "".join(out)


def _url_unescape(text):
    raw = bytearray()
    i = 0
    while i < len(text):
        c = text[i]
        if c == "%":
            pair = text[i + 1:i + 3]
            if len(pair) != 2 or any(h not in _HEX for h in pair):
                raise ValueError("the text has a %% at position %d that is not followed by two hex digits: "
                                 "fix it or turn it into %%25" % i)
            raw.append(int(pair, 16))
            i += 3
        else:
            raw.extend(c.encode("utf-8"))
            i += 1
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("the % codes do not spell valid text: check the codes for a cut-off letter")


def _line_escape(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def _line_unescape(text):
    out = []
    i = 0
    while i < len(text):
        c = text[i]
        nxt = text[i + 1:i + 2]
        if c == "\\" and nxt == "n":
            out.append("\n")
            i += 2
        elif c == "\\" and nxt == "\\":
            out.append("\\")
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def escape_text(text, mode="json string", direction="escape"):
    """Pure function. Escapes or unescapes text for the chosen target."""
    if not isinstance(text, str):
        raise ValueError("text must be text, got %r" % (text,))
    if mode not in MODES:
        raise ValueError("mode must be one of: %s (got %r)" % (", ".join(MODES), mode))
    if direction not in DIRECTIONS:
        raise ValueError("direction must be escape or unescape (got %r)" % (direction,))
    esc = direction == "escape"
    if mode == "json string":
        if esc:
            return json.dumps(text, ensure_ascii=False)[1:-1]
        try:
            return json.loads('"' + text + '"', strict=False)
        except ValueError:
            raise ValueError("this is not a valid JSON string body: a quote mark needs a backslash in front "
                             "(\\\"), and a backslash must be followed by n, t, \\, \" or u and four digits")
    if mode == "url":
        return _url_escape(text) if esc else _url_unescape(text)
    if mode == "single line":
        return _line_escape(text) if esc else _line_unescape(text)
    return html.escape(text, quote=True) if esc else html.unescape(text)


class SYEscapeText:
    DESCRIPTION = ("Makes text safe to paste somewhere else (a JSON string, a web address, one line, or web page text), "
                   "or turns it back. Broken text to unescape stops with a plain message.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to change."}),
                "mode": (MODES, {"default": "json string", "tooltip": "Where the text will be pasted. Single line shows line breaks as \\n."}),
                "direction": (DIRECTIONS, {"default": "escape", "tooltip": "Escape makes it safe. Unescape turns it back to normal text."}),
            },
        }

    def run(self, text, mode="json string", direction="escape"):
        return (escape_text(text, mode, direction),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EscapeText", SYEscapeText)
NODE_DISPLAY_NAME_MAPPINGS["SYEscapeText"] = "Escape Text SY"
