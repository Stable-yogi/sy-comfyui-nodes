"""Sort Dedupe Lines SY: sorts a list of lines and removes repeats and empty lines."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SORTS = ("none", "a-z", "z-a", "shortest first", "longest first")


def process_lines(lines, sort, dedupe, ignore_case, drop_empty, trim_lines=False):
    """Pure function. Returns the new list of lines. trim_lines removes spaces at both ends of every line first."""
    return process_lines_report(lines, sort, dedupe, ignore_case, drop_empty, trim_lines)[0]


def process_lines_report(lines, sort, dedupe, ignore_case, drop_empty, trim_lines=False):
    """Pure function. Returns (new_lines, stats) where stats counts input, empty, duplicate and padded lines."""
    if sort not in SORTS:
        raise ValueError("sort must be one of: %s, got %r" % (", ".join(SORTS), sort))
    stats = {"input": len(lines), "empty": 0, "duplicates": 0, "padded": 0}
    out = []
    for line in lines:
        if line.endswith("\r"):
            line = line[:-1]
        if line.strip() != line and line.strip() != "":
            stats["padded"] += 1
        if trim_lines:
            line = line.strip()
        if drop_empty and line.strip() == "":
            stats["empty"] += 1
            continue
        out.append(line)
    if dedupe:
        seen = set()
        kept = []
        for line in out:
            key = line.lower() if ignore_case else line
            if key in seen:
                stats["duplicates"] += 1
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
    return out, stats


def lines_info(stats, kept, trim_lines=False):
    """Pure function. One plain line: how many lines were kept and why others went."""
    line = "Kept %d of %d line(s)" % (kept, stats["input"])
    gone = []
    if stats["duplicates"]:
        gone.append("%d repeated" % stats["duplicates"])
    if stats["empty"]:
        gone.append("%d empty" % stats["empty"])
    if gone:
        line += "; removed " + " and ".join(gone)
    if stats["padded"] and not trim_lines:
        line += "; %d line(s) have spaces at the ends, so 'cat ' and 'cat' count as different (turn on trim_lines)" % stats["padded"]
    return line


class SYSortDedupeLines:
    DESCRIPTION = ("Cleans a list with one item per line: sorts it, removes repeated lines and drops empty ones. Can trim spaces first so "
                   "'cat ' and 'cat' match, and the info line says how many lines went and why.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The list, one item per line."}),
                "sort": (list(SORTS), {"default": "none", "tooltip": "How to order the lines. none keeps the original order."}),
                "remove_duplicates": ("BOOLEAN", {"default": True, "tooltip": "On keeps only the first copy of each line."}),
                "ignore_case": ("BOOLEAN", {"default": True, "tooltip": "On treats capital and small letters as the same when comparing and sorting."}),
                "drop_empty": ("BOOLEAN", {"default": True, "tooltip": "On removes lines that are empty or only spaces."}),
            },
            "optional": {
                "trim_lines": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces at the start and end of each line first, so repeats with stray spaces are found."}),
            },
        }

    def run(self, text, sort, remove_duplicates, ignore_case, drop_empty, trim_lines=False):
        if not isinstance(text, str):
            raise ValueError("text must be text, got %r" % (text,))
        lines, stats = process_lines_report(text.split("\n"), sort, remove_duplicates, ignore_case, drop_empty, trim_lines)
        return ("\n".join(lines), len(lines), lines_info(stats, len(lines), trim_lines))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SortDedupeLines", SYSortDedupeLines)
NODE_DISPLAY_NAME_MAPPINGS["SYSortDedupeLines"] = "Sort Dedupe Lines SY"
