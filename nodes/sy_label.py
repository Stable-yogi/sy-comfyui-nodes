"""Label SY: a big floating text label for your workflow, like a sticker for a title or a step name.
The text is drawn in the browser (js/sy_label.js). This file holds the node shell and the plain rules, so they can be tested."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

COLOURS = ("gold", "white", "grey", "blue", "green", "red", "purple")
ALIGNS = ("left", "centre", "right")
MIN_SIZE, MAX_SIZE = 10, 200
MAX_TEXT = 2000


def clean_label(text, size=36, colour="gold", align="left"):
    """Pure function. Returns (text, size, colour, align) with safe values.
    Text is cut at MAX_TEXT characters, size is kept between MIN_SIZE and MAX_SIZE, an unknown colour becomes gold and an unknown align becomes left."""
    text = "" if text is None else str(text)[:MAX_TEXT]
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 36
    size = max(MIN_SIZE, min(MAX_SIZE, size))
    colour = colour if colour in COLOURS else "gold"
    align = align if align in ALIGNS else "left"
    return text, size, colour, align


def label_lines(text):
    """Pure function. The lines of a label, without the empty lines at both ends. An empty label has no lines."""
    lines = str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


class SYLabel:
    DESCRIPTION = ("A big text label that floats in your workflow, like a sticker for a title or a step name. Pick the size, colour and side. "
                   "It runs nothing and has no wires.")
    CATEGORY = category("Notes")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Label", "multiline": True, "tooltip": "The words to show. Use Enter for a new line."}),
                "size": ("INT", {"default": 36, "min": MIN_SIZE, "max": MAX_SIZE, "tooltip": "Height of the letters in pixels."}),
                "colour": (list(COLOURS), {"default": "gold", "tooltip": "Colour of the letters."}),
                "align": (list(ALIGNS), {"default": "left", "tooltip": "Where the words sit inside the label."}),
            }
        }

    def run(self, text="Label", size=36, colour="gold", align="left"):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Label", SYLabel)
