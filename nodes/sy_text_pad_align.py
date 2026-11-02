"""Text Pad Align SY: makes every line the same width by padding it with a fill character."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ALIGNS = ["left", "right", "centre"]


def pad_lines(lines, align="left", width=0, fill=" ", truncate=False):
    """Pure function. Returns (new_lines, width_used). Counts characters, not bytes.
    align says where the TEXT sits: left pads on the right, right pads on the left,
    centre splits the padding with the extra space on the right.
    width 0 = the longest line. Longer lines are kept whole unless truncate is on."""
    if align not in ALIGNS:
        raise ValueError("align must be one of: %s (got %r)" % (", ".join(ALIGNS), align))
    if not isinstance(fill, str) or len(fill) != 1 or fill in ("\n", "\r"):
        raise ValueError("fill must be exactly one character (not a line break), got %r" % (fill,))
    width = int(width)
    if width < 0:
        raise ValueError("width must be 0 or more, got %d" % width)
    lines = list(lines)
    target = width if width > 0 else max((len(s) for s in lines), default=0)
    out = []
    for s in lines:
        if len(s) > target:
            out.append(s[:target] if truncate else s)
            continue
        pad = target - len(s)
        if align == "left":
            out.append(s + fill * pad)
        elif align == "right":
            out.append(fill * pad + s)
        else:
            left = pad // 2
            out.append(fill * left + s + fill * (pad - left))
    return out, max((len(s) for s in out), default=0)


class SYTextPadAlign:
    DESCRIPTION = ("Makes all lines of a text the same width by padding them with a fill character. "
                   "Align the text left, right or centre. Optionally cut lines that are too long.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "width_used")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to pad. Each line is padded on its own."}),
                "align": (ALIGNS, {"default": "left", "tooltip": "Where the words sit inside the width. Centre puts the extra space on the right."}),
                "width": ("INT", {"default": 0, "min": 0, "max": 500, "tooltip": "Characters per line. 0 uses the longest line."}),
                "fill": ("STRING", {"default": " ", "tooltip": "The one character used for padding. A space by default."}),
                "truncate": ("BOOLEAN", {"default": False, "tooltip": "On: cut lines longer than the width. Off: keep them whole."}),
            }
        }

    def run(self, text, align, width, fill, truncate):
        body = text.replace("\r\n", "\n").replace("\r", "\n")
        if body.endswith("\n"):
            body = body[:-1]
        out, used = pad_lines(body.split("\n"), align, width, fill, truncate)
        return ("\n".join(out), used)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextPadAlign", SYTextPadAlign)
NODE_DISPLAY_NAME_MAPPINGS["SYTextPadAlign"] = "Text Pad Align SY"
