"""Note SY: a coloured note card for your workflow. The colour shows what kind of note it is."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ("info", "tip", "warning", "step", "model")


def clean_note(text, style="info"):
    """Pure function. Returns (text, style). Unknown style becomes info."""
    if text is None:
        text = ""
    style = style if style in STYLES else "info"
    return str(text), style


def note_output(text, style="info", add_style_label=False, trim=False):
    """Pure function. The text that leaves the node. trim cuts spaces and blank lines at both ends.
    add_style_label puts the style in front, for example 'WARNING: ...' (nothing is added to an empty note)."""
    text, style = clean_note(text, style)
    if trim:
        text = text.strip()
    if add_style_label and text.strip():
        text = "%s: %s" % (style.upper(), text)
    return text


def note_info(text, style="info"):
    """Pure function. A plain line: style, lines, words and characters. Warns when the note is empty."""
    text, style = clean_note(text, style)
    if not text.strip():
        return "Empty %s note: nothing to send as a prompt." % style
    lines = len([line for line in text.splitlines() if line.strip()])
    words = len(text.split())
    return "%s note: %d line%s, %d word%s, %d character%s." % (
        style.capitalize(), lines, "" if lines == 1 else "s", words, "" if words == 1 else "s", len(text), "" if len(text) == 1 else "s")


class SYNote:
    DESCRIPTION = "A note card for your workflow. Pick a style and the card gets a colour. The text can also go out as a prompt, with the style in front if you like, and an info line counts the words."
    CATEGORY = category("Notes")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "Write your note here. Plain text."}),
                "style": (list(STYLES), {"default": "info", "tooltip": "Info is blue, tip is green, warning is red, step is gold, model is purple."}),
            },
            "optional": {
                "add_style_label": ("BOOLEAN", {"default": False, "tooltip": "On puts the style in front of the sent text, for example WARNING: check the seed."}),
                "trim": ("BOOLEAN", {"default": False, "tooltip": "On cuts spaces and blank lines from the start and end of the sent text."}),
            },
        }

    def run(self, text, style="info", add_style_label=False, trim=False):
        return (note_output(text, style, add_style_label, trim), note_info(text, style))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Note", SYNote)
