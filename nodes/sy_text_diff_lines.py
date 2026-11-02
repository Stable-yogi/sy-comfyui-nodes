"""Text Diff Lines SY: compares two texts line by line (only in A, only in B, in both)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def diff_lines(a, b, ignore_case=False, trim=True):
    """Pure function. Returns (only_a, only_b, both) as lists. Order kept, no duplicates, empty lines ignored."""
    def prep(text):
        out, seen = [], set()
        for line in str(text or "").splitlines():
            shown = line.strip() if trim else line
            if not shown.strip():
                continue
            key = shown.lower() if ignore_case else shown
            if key not in seen:
                seen.add(key)
                out.append((key, shown))
        return out

    la, lb = prep(a), prep(b)
    ka, kb = {k for k, _ in la}, {k for k, _ in lb}
    only_a = [s for k, s in la if k not in kb]
    only_b = [s for k, s in lb if k not in ka]
    both = [s for k, s in la if k in kb]
    return only_a, only_b, both


def summary_text(only_a, only_b, both):
    return "%d only in A, %d only in B, %d in both" % (len(only_a), len(only_b), len(both))


class SYTextDiffLines:
    DESCRIPTION = ("Compares two multi-line texts line by line. Shows the lines only in A, only in B and in both, "
                   "with a one-line summary.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("only_a", "only_b", "both", "summary")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_a": ("STRING", {"multiline": True, "default": "", "tooltip": "The first text. One item per line."}),
                "text_b": ("STRING", {"multiline": True, "default": "", "tooltip": "The second text. One item per line."}),
                "ignore_case": ("BOOLEAN", {"default": False, "tooltip": "On: Red and red count as the same line."}),
                "trim_spaces": ("BOOLEAN", {"default": True, "tooltip": "On: spaces at the start and end of a line are ignored."}),
            }
        }

    def run(self, text_a, text_b, ignore_case=False, trim_spaces=True):
        oa, ob, both = diff_lines(text_a, text_b, ignore_case, trim_spaces)
        return ("\n".join(oa), "\n".join(ob), "\n".join(both), summary_text(oa, ob, both))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextDiffLines", SYTextDiffLines)
NODE_DISPLAY_NAME_MAPPINGS["SYTextDiffLines"] = "Text Diff Lines SY"
