"""Prompt Conflict Check SY: warns when a prompt holds opposite words (day and night, indoor and outdoor ...)."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

BUILTIN_PAIRS = [
    ("day", "night"), ("daytime", "nighttime"), ("sunrise", "sunset"), ("indoor", "outdoor"),
    ("indoors", "outdoors"), ("black and white", "colour"), ("black and white", "color"),
    ("monochrome", "colorful"), ("close-up", "wide shot"), ("close-up", "full body"),
    ("portrait", "landscape"), ("sunny", "rainy"), ("sunny", "overcast"), ("summer", "winter"),
    ("young", "old"), ("male", "female"), ("man", "woman"), ("boy", "girl"),
    ("bright", "dark"), ("light", "dark"), ("happy", "sad"), ("smiling", "frowning"),
    ("realistic", "cartoon"), ("photo", "painting"), ("tall", "short"),
    ("fat", "thin"), ("big", "small"), ("clean", "dirty"), ("empty", "crowded"),
    ("standing", "sitting"), ("eyes open", "eyes closed"), ("hot", "cold"), ("fast", "slow"),
    ("low angle", "high angle"), ("sharp", "blurry"), ("sharp focus", "out of focus"),
]


def parse_pairs(raw):
    """Pure function. Reads 'a | b' lines. A line without exactly one bar raises ValueError."""
    pairs = []
    for n, line in enumerate(str(raw or "").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("extra_pairs line %d must look like 'a | b' (two words with one bar between), got: %s" % (n, line))
        pairs.append((parts[0], parts[1]))
    return pairs


def _has(text, word):
    return re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text, re.IGNORECASE) is not None


def find_conflicts(text, pairs=None):
    """Pure function. Returns the list of (a, b) pairs where both words appear as whole words."""
    text = str(text or "")
    found, seen = [], set()
    for a, b in list(BUILTIN_PAIRS) + list(pairs or []):
        key = (a.lower(), b.lower())
        if key in seen:
            continue
        seen.add(key)
        if _has(text, a) and _has(text, b):
            found.append((a, b))
    return found


def format_report(conflicts):
    if not conflicts:
        return "No conflicts found"
    return "\n".join("%s <-> %s" % (a, b) for a, b in conflicts)


class SYPromptConflictCheck:
    DESCRIPTION = ("Warns when a prompt holds opposite words like day and night or indoor and outdoor. "
                   "The text passes through unchanged. You can add your own pairs.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("text", "report", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt to check."}),
            },
            "optional": {
                "extra_pairs": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own opposite pairs, one per line, like: cat | dog"}),
            },
        }

    def run(self, text, extra_pairs=""):
        conflicts = find_conflicts(text, parse_pairs(extra_pairs))
        return (text, format_report(conflicts), len(conflicts))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptConflictCheck", SYPromptConflictCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptConflictCheck"] = "Prompt Conflict Check SY"
