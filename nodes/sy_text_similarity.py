"""Text Similarity SY: tells how alike two texts are (0 to 1)."""
import difflib

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

COMPARE_BY = ["words", "characters"]


def similarity_ratio(a, b, compare_by="words", ignore_case=True):
    """Pure function. Matching-blocks ratio, 2 * matches / total length, from 0.0 to 1.0. Two empty texts give 1.0."""
    if not isinstance(a, str) or not isinstance(b, str):
        raise ValueError("both texts must be text")
    if compare_by not in COMPARE_BY:
        raise ValueError("compare_by must be words or characters (got %r)" % (compare_by,))
    if ignore_case:
        a, b = a.lower(), b.lower()
    if compare_by == "words":
        a, b = a.split(), b.split()
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


class SYTextSimilarity:
    DESCRIPTION = ("Tells how alike two texts are, from 0 (nothing in common) to 1 (the same). "
                   "Use it to see if a prompt changed much or a caption repeats.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "BOOLEAN")
    RETURN_NAMES = ("similarity", "is_close")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_a": ("STRING", {"multiline": True, "default": "", "tooltip": "The first text."}),
                "text_b": ("STRING", {"multiline": True, "default": "", "tooltip": "The second text."}),
                "compare_by": (COMPARE_BY, {"default": "words", "tooltip": "Compare whole words, or single letters."}),
                "ignore_case": ("BOOLEAN", {"default": True, "tooltip": "On: capital and small letters count as the same."}),
                "threshold": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "is_close is true when the similarity is at least this."}),
            },
        }

    def run(self, text_a, text_b, compare_by="words", ignore_case=True, threshold=0.8):
        r = similarity_ratio(text_a, text_b, compare_by, ignore_case)
        return (r, r >= float(threshold))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextSimilarity", SYTextSimilarity)
NODE_DISPLAY_NAME_MAPPINGS["SYTextSimilarity"] = "Text Similarity SY"
