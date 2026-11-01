"""Text Wrap SY: breaks long lines of text at a chosen width."""
import re
import textwrap

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def wrap_text(text, width, keep_paragraphs, keep_line_breaks=False):
    """Pure function. Returns (wrapped_text, line_count).
    keep_paragraphs True: each paragraph (blocks split by blank lines) is wrapped on its own and one blank line is kept between them.
    False: everything is joined into one paragraph first.
    keep_line_breaks True: every existing line is wrapped on its own and stays a line (poems, lyrics, subtitles); blank lines are kept."""
    if not isinstance(text, str):
        raise ValueError("text must be text, got %r" % (text,))
    if width < 4 or width > 1000:
        raise ValueError("width must be between 4 and 1000, got %s" % width)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if keep_line_breaks:
        lines = []
        for raw in text.split("\n"):
            flat = " ".join(raw.split())
            lines.extend(textwrap.wrap(flat, width=width, break_long_words=True, break_on_hyphens=False) if flat else [""])
        while lines and lines[0] == "":
            lines.pop(0)
        while lines and lines[-1] == "":
            lines.pop()
        return ("\n".join(lines), len(lines))
    if keep_paragraphs:
        blocks = [b for b in re.split(r"\n[ \t]*\n", text)]
    else:
        blocks = [text]
    out_blocks = []
    for block in blocks:
        flat = " ".join(block.split())
        if not flat:
            if keep_paragraphs and block == "" and len(blocks) > 1:
                continue
            out_blocks.append([])
            continue
        out_blocks.append(textwrap.wrap(flat, width=width, break_long_words=True, break_on_hyphens=False))
    lines = []
    for i, b in enumerate(out_blocks):
        if i > 0 and b:
            lines.append("")
        lines.extend(b)
    while lines and lines[0] == "":
        lines.pop(0)
    result = "\n".join(lines)
    return (result, len(lines))


def wrap_info(original, result, width):
    """Pure function. One plain line: the line count, the longest line, and how many long words had to be split."""
    lines = result.split("\n") if result else []
    longest = max((len(x) for x in lines), default=0)
    too_long = sum(1 for word in str(original).split() if len(word) > width)
    line = "%d line(s), longest line %d of %d characters" % (len(lines), longest, width)
    if too_long:
        line += "; %d word(s) were longer than the width and got split" % too_long
    return line


class SYTextWrap:
    DESCRIPTION = ("Breaks long lines of text at a chosen width. Long words are split, and paragraphs can be kept apart. "
                   "keep_line_breaks wraps each line on its own (poems, lyrics, subtitles). The info line shows the longest line.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "line_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to wrap."}),
                "width": ("INT", {"default": 40, "min": 4, "max": 1000, "step": 1, "tooltip": "Most characters allowed on one line."}),
                "keep_paragraphs": ("BOOLEAN", {"default": True, "tooltip": "On keeps a blank line between paragraphs. Off joins all the text into one block."}),
            },
            "optional": {
                "keep_line_breaks": ("BOOLEAN", {"default": False, "tooltip": "On: every line you typed stays its own line and is only wrapped if too long. Overrides keep_paragraphs."}),
            },
        }

    def run(self, text, width, keep_paragraphs, keep_line_breaks=False):
        out, count = wrap_text(text, width, keep_paragraphs, keep_line_breaks)
        return (out, count, wrap_info(text, out, width))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextWrap", SYTextWrap)
NODE_DISPLAY_NAME_MAPPINGS["SYTextWrap"] = "Text Wrap SY"
