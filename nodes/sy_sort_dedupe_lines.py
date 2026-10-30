"""Sort Dedupe Lines SY: sorts a list of lines and removes repeats and empty lines."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SORTS = ("none", "a-z", "z-a", "shortest first", "longest first")


def process_lines(lines, sort, dedupe, ignore_case, drop_empty):
    """Pure function. Returns the new list of lines."""
    if sort not in SORTS:
        raise ValueError("sort must be one of: %s, got %r" % (", ".join(SORTS), sort))
    out = []
    for line in lines:
        if line.endswith("\r"):
            line = line[:-1]
        if drop_empty and line.strip() == "":
            continue
        out.append(line)
    if dedupe:
        seen = set()
        kept = []
        for line in out:
            key = line.lower() if ignore_case else line
            if key in seen:
                continue
            seen.add(key)
            kept.append(line)
        out = kept
    if sort in ("a-z", "z-a"):
        out = sorted(out, key=(lambda s: s.lower()) if ignore_case else (lambda s: s), reverse=(sort == "z-a"))
    elif sort == "shortest first":
        out = sorted(out, key=len)
    elif sort == "longest first":
        out = sorted(out, key=len, reverse=True)
    return out


class SYSortDedupeLines:
    DESCRIPTION = "Cleans a list with one item per line: sorts it, removes repeated lines and drops empty ones."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The list, one item per line."}),
                "sort": (list(SORTS), {"default": "none", "tooltip": "How to order the lines. none keeps the original order."}),
                "remove_duplicates": ("BOOLEAN", {"default": True, "tooltip": "On keeps only the first copy of each line."}),
                "ignore_case": ("BOOLEAN", {"default": True, "tooltip": "On treats capital and small letters as the same when comparing and sorting."}),
                "drop_empty": ("BOOLEAN", {"default": True, "tooltip": "On removes lines that are empty or only spaces."}),
            }
        }

    def run(self, text, sort, remove_duplicates, ignore_case, drop_empty):
        if not isinstance(text, str):
            raise ValueError("text must be text, got %r" % (text,))
        lines = process_lines(text.split("\n"), sort, remove_duplicates, ignore_case, drop_empty)
        return ("\n".join(lines), len(lines))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SortDedupeLines", SYSortDedupeLines)
NODE_DISPLAY_NAME_MAPPINGS["SYSortDedupeLines"] = "Sort Dedupe Lines SY"
