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


class SYNote:
    DESCRIPTION = "A note card for your workflow. Pick a style and the card gets a colour. The text can also go out as a prompt."
    CATEGORY = category("Notes")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "Write your note here. Plain text."}),
                "style": (list(STYLES), {"default": "info", "tooltip": "Info is blue, tip is green, warning is red, step is gold, model is purple."}),
            }
        }

    def run(self, text, style="info"):
        return (clean_note(text, style)[0],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Note", SYNote)
