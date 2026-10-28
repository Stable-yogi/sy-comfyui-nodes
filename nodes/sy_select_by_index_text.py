"""Select By Index Text SY: picks one of up to 8 connected texts by number. Too-big numbers wrap around."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SLOTS = 8


def select_text(index, texts):
    """Pure function. `texts` is a list of the connected texts in order (no gaps). Returns (text, slot_number_from_0).
    Index 0 is the first text. Numbers past the end wrap to the start. Negative numbers count from the end."""
    if isinstance(index, bool) or not isinstance(index, int):
        raise ValueError("index must be a whole number, got %r." % (index,))
    texts = list(texts)
    if not texts:
        raise ValueError("No text is connected. Connect at least one text input.")
    if len(texts) > SLOTS:
        raise ValueError("At most %d texts are allowed, got %d." % (SLOTS, len(texts)))
    for i, t in enumerate(texts):
        if not isinstance(t, str):
            raise ValueError("Text %d must be text, got %r." % (i + 1, t))
    slot = index % len(texts)
    return texts[slot], slot


class SYSelectByIndexText:
    DESCRIPTION = "Picks one of up to 8 connected texts by number. 0 is the first connected text. Too big a number wraps to the start."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "slot")

    @classmethod
    def INPUT_TYPES(cls):
        optional = {}
        for n in range(1, SLOTS + 1):
            optional["text_%d" % n] = ("STRING", {"forceInput": True, "tooltip": "Text number %d. Leave it unconnected to skip it." % n})
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": -2 ** 31, "max": 2 ** 31 - 1, "tooltip": "Which connected text to send, from 0. Past the last one wraps to the first."}),
            },
            "optional": optional,
        }

    def run(self, index, **texts):
        keys = ["text_%d" % n for n in range(1, SLOTS + 1) if texts.get("text_%d" % n) is not None]
        return select_text(index, [texts[k] for k in keys])


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SelectByIndexText", SYSelectByIndexText)
NODE_DISPLAY_NAME_MAPPINGS["SYSelectByIndexText"] = "Select By Index Text SY"
