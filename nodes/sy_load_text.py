"""Load Text SY: reads a .txt file from the ComfyUI input folder."""
import difflib
import os

try:
    from ._sy_safe_paths import root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder, safe_join
    from _sy_common import category, register

IF_MISSING = ["error", "empty"]

MAX_BYTES = 2_000_000


def read_text_file(base, relative):
    """Read a .txt file under `base`. Refuses other extensions, paths outside `base` and big files."""
    rel = str(relative).strip()
    if not rel:
        raise ValueError("file is empty: type the name of a .txt file in the input folder")
    if not rel.lower().endswith(".txt"):
        raise ValueError("only .txt files can be loaded, got %r" % rel)
    path = safe_join(base, rel)
    if not os.path.isfile(path):
        raise ValueError(missing_message(base, rel))
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError("text file is too big (%d bytes, max %d)" % (size, MAX_BYTES))
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:  # utf-8-sig drops a leading byte order mark
        return f.read()


def missing_message(base, rel):
    """Pure-ish. The 'file not found' text, with close .txt names from the same folder when there are any."""
    msg = "text file not found in the input folder: %s" % rel
    try:
        parent_rel, _, leaf = str(rel).replace("\\", "/").rpartition("/")
        parent = safe_join(base, parent_rel)
        names = [n for n in os.listdir(parent) if n.lower().endswith(".txt") and os.path.isfile(os.path.join(parent, n))] if os.path.isdir(parent) else []
        close = difflib.get_close_matches(leaf, names, n=3, cutoff=0.5)
        if close:
            msg += ". Close names in that folder: %s" % ", ".join(close)
        elif not os.path.isdir(parent):
            msg += ". The folder %r does not exist" % parent_rel
        elif names:
            msg += ". .txt files there: %s" % ", ".join(sorted(names)[:5])
    except (ValueError, OSError):
        pass
    return msg


def shape_text(text, line=0, strip=False, skip_comments=False):
    """Pure function. Returns (text, line_count, info).

    With all options off the text comes back exactly as read. skip_comments drops lines that start with #.
    strip trims each line and removes empty lines at the start and end. line N (1 = first) returns only that line
    of what is left; 0 returns everything.
    """
    text = str(text)
    line = int(line)
    if line < 0:
        raise ValueError("line cannot be negative, got %d" % line)
    if not (line or strip or skip_comments):
        return text, len(text.splitlines()), "%d lines, %d characters." % (len(text.splitlines()), len(text))
    lines = text.splitlines()
    notes = []
    if skip_comments:
        kept = [x for x in lines if not x.lstrip().startswith("#")]
        if len(kept) != len(lines):
            notes.append("%d comment lines skipped." % (len(lines) - len(kept)))
        lines = kept
    if strip:
        lines = [x.strip() for x in lines]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
    count = len(lines)
    if line:
        if line > count:
            raise ValueError("line %d does not exist: the text has %d lines. Lower line or use 0 for all." % (line, count))
        out = lines[line - 1]
        notes.insert(0, "Line %d of %d." % (line, count))
    else:
        out = "\n".join(lines)
        notes.insert(0, "%d lines, %d characters." % (count, len(out)))
    return out, count, " ".join(notes)


def load_text(base, relative, line=0, strip=False, skip_comments=False, if_missing="error"):
    """Returns (text, line_count, info). if_missing 'empty' answers '' for a file that is not there."""
    if if_missing not in IF_MISSING:
        raise ValueError("if_missing must be error or empty, got %r" % (if_missing,))
    try:
        raw = read_text_file(base, relative)
    except ValueError as e:
        if if_missing == "empty" and "not found" in str(e):
            return "", 0, str(e) + ". Returning empty text."
        raise
    return shape_text(raw, line, strip, skip_comments)


class SYLoadText:
    DESCRIPTION = ("Loads the text of a .txt file from the ComfyUI input folder. Other file types are refused. "
                   "Optional line picks one line (1 = first), strip trims lines, skip_comments ignores lines starting with #, "
                   "and if_missing can answer empty text for a file that is not there. Also gives the line count and an info line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "line_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"file": ("STRING", {"default": "notes.txt", "tooltip": "Path of a .txt file inside the input folder, like notes.txt or a/b.txt."})},
            "optional": {
                "line": ("INT", {"default": 0, "min": 0, "max": 1000000, "tooltip": "0 = the whole text. 1 = only the first line, 2 = the second, and so on."}),
                "strip": ("BOOLEAN", {"default": False, "tooltip": "On: trim spaces around each line and empty lines at the start and end."}),
                "skip_comments": ("BOOLEAN", {"default": False, "tooltip": "On: ignore lines that start with #."}),
                "if_missing": (IF_MISSING, {"default": "error", "tooltip": "error stops with a clear message. empty gives empty text."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, file, **kw):
        try:
            return os.path.getmtime(safe_join(root_folder("input"), file))
        except Exception:
            return float("nan")

    def run(self, file, line=0, strip=False, skip_comments=False, if_missing="error"):
        return load_text(root_folder("input"), file, line, strip, skip_comments, if_missing)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadText", SYLoadText)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadText"] = "Load Text SY"
