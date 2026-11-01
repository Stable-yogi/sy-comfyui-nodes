"""Select By Index Text SY: picks one of up to 8 connected texts by number. Too-big numbers wrap around."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SLOTS = 8
OUT_OF_RANGE = ("wrap", "clamp", "error")


def select_text(index, texts, out_of_range="wrap", skip_empty=False):
    """Pure function. `texts` is a list of the connected texts in order (no gaps). Returns (text, slot_number_from_0).
    Index 0 is the first text. Numbers past the end wrap to the start. Negative numbers count from the end.
    out_of_range: wrap (default), clamp (stay on the first or last), error (stop with a message).
    skip_empty: texts that are empty or only spaces are left out before counting."""
    if out_of_range not in OUT_OF_RANGE:
        raise ValueError("out_of_range must be one of %s, got %r." % (", ".join(OUT_OF_RANGE), out_of_range))
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
    if skip_empty:
        texts = [t for t in texts if t.strip()]
        if not texts:
            raise ValueError("Every connected text is empty. Write something in at least one, or turn skip_empty off.")
    count = len(texts)
    if out_of_range == "error" and not 0 <= index < count:
        raise ValueError("Index %d is outside 0 to %d: only %d text%s connected. Lower the index or choose wrap." % (index, count - 1, count, " is" if count == 1 else "s are"))
    if out_of_range == "clamp":
        slot = min(max(index, 0), count - 1)
    else:
        slot = index % count
    return texts[slot], slot


def select_info(index, slot, count):
    """Pure function. A plain line saying which text came out."""
    note = "" if index == slot else " (index %d went round or was clamped)" % index
    return "Sent text %d of %d%s." % (slot + 1, count, note)


class SYSelectByIndexText:
    DESCRIPTION = "Picks one of up to 8 connected texts by number. 0 is the first connected text. Too big a number wraps to the start, stays on the last, or stops with a message. Empty texts can be skipped."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("text", "slot", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            "out_of_range": (list(OUT_OF_RANGE), {"default": "wrap", "tooltip": "wrap: go round. clamp: stay on the first or last. error: stop with a message."}),
            "skip_empty": ("BOOLEAN", {"default": False, "tooltip": "On ignores texts that are empty or only spaces, so an unused slot does not get picked."}),
        }
        for n in range(1, SLOTS + 1):
            optional["text_%d" % n] = ("STRING", {"forceInput": True, "tooltip": "Text number %d. Leave it unconnected to skip it." % n})
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": -2 ** 31, "max": 2 ** 31 - 1, "tooltip": "Which connected text to send, from 0. Past the last one wraps to the first."}),
            },
            "optional": optional,
        }

    def run(self, index, out_of_range="wrap", skip_empty=False, **texts):
        keys = ["text_%d" % n for n in range(1, SLOTS + 1) if texts.get("text_%d" % n) is not None]
        chosen = [texts[k] for k in keys]
        text, slot = select_text(index, chosen, out_of_range, skip_empty)
        count = len([t for t in chosen if t.strip()]) if skip_empty else len(chosen)
        return (text, slot, count, select_info(index, slot, count))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SelectByIndexText", SYSelectByIndexText)
NODE_DISPLAY_NAME_MAPPINGS["SYSelectByIndexText"] = "Select By Index Text SY"
