"""Text Join SY: join up to four texts with a separator."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def join_texts(parts, separator, skip_empty, trim_parts=False, remove_repeats=False):
    """Pure function. Joins parts with separator. skip_empty drops parts that are empty or only spaces.
    trim_parts removes spaces around every part first. remove_repeats drops a part equal to an earlier one (case ignored)."""
    return join_texts_info(parts, separator, skip_empty, trim_parts, remove_repeats)[0]


def join_texts_info(parts, separator, skip_empty, trim_parts=False, remove_repeats=False):
    """Pure function. Returns (text, stats) where stats counts inputs, empty parts and repeated parts."""
    items = ["" if p is None else str(p) for p in parts]
    stats = {"inputs": len(items), "empty": 0, "repeated": 0}
    if trim_parts:
        items = [p.strip() for p in items]
    if skip_empty:
        kept = [p for p in items if p.strip() != ""]
        stats["empty"] = len(items) - len(kept)
        items = kept
    if remove_repeats:
        seen = set()
        kept = []
        for p in items:
            key = p.strip().lower()
            if key and key in seen:
                stats["repeated"] += 1
                continue
            seen.add(key)
            kept.append(p)
        items = kept
    return ("" if separator is None else str(separator)).join(items), stats


def join_info(text, stats):
    """Pure function. One plain line: how many parts were joined and how many were left out."""
    used = stats["inputs"] - stats["empty"] - stats["repeated"]
    line = "Joined %d of %d texts" % (used, stats["inputs"])
    gone = []
    if stats["empty"]:
        gone.append("%d empty skipped" % stats["empty"])
    if stats["repeated"]:
        gone.append("%d repeated removed" % stats["repeated"])
    if gone:
        line += " (" + ", ".join(gone) + ")"
    return line + "; %d characters" % len(text)


class SYTextJoin:
    DESCRIPTION = ("Joins up to six texts into one, with a separator between them. Empty texts can be skipped, spaces around each part can be trimmed, "
                   "and a part that repeats an earlier one can be dropped. The info line says how many were joined.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "separator": ("STRING", {"default": ", ", "tooltip": "What goes between the texts. A comma and space is common."}),
                "skip_empty": ("BOOLEAN", {"default": True, "tooltip": "On: empty texts are left out so you get no double separators."}),
            },
            "optional": {
                "text_a": ("STRING", {"default": "", "multiline": True, "tooltip": "The first text to join. Leave empty to skip it."}),
                "text_b": ("STRING", {"default": "", "multiline": True, "tooltip": "The second text to join. Leave empty to skip it."}),
                "text_c": ("STRING", {"default": "", "multiline": True, "tooltip": "The third text to join. Leave empty to skip it."}),
                "text_d": ("STRING", {"default": "", "multiline": True, "tooltip": "The fourth text to join. Leave empty to skip it."}),
                "text_e": ("STRING", {"default": "", "multiline": True, "tooltip": "The fifth text to join. Leave empty to skip it."}),
                "text_f": ("STRING", {"default": "", "multiline": True, "tooltip": "The sixth text to join. Leave empty to skip it."}),
                "trim_parts": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces and line breaks around each text before joining."}),
                "remove_repeats": ("BOOLEAN", {"default": False, "tooltip": "On: a text that is the same as an earlier one (capitals ignored) is left out."}),
            },
        }

    def run(self, separator=", ", skip_empty=True, text_a="", text_b="", text_c="", text_d="", text_e="", text_f="",
            trim_parts=False, remove_repeats=False):
        text, stats = join_texts_info([text_a, text_b, text_c, text_d, text_e, text_f], separator, skip_empty, trim_parts, remove_repeats)
        return (text, join_info(text, stats))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextJoin", SYTextJoin)
NODE_DISPLAY_NAME_MAPPINGS["SYTextJoin"] = "Text Join SY"
