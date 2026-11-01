"""List Folder Files SY: lists the files of a sub folder of the input or output folder as text lines."""
try:
    from ._sy_safe_paths import list_files, parse_extensions, root_folder, safe_join
    from ._sy_common import category, register
    from ._sy_a1_files import split_words, format_bytes
    from ._sy_a1_folders import SORT_CHOICES, IF_MISSING, scan_folder, sort_entries, check_if_missing, ext_breakdown
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import list_files, parse_extensions, root_folder, safe_join
    from _sy_common import category, register
    from _sy_a1_files import split_words, format_bytes
    from _sy_a1_folders import SORT_CHOICES, IF_MISSING, scan_folder, sort_entries, check_if_missing, ext_breakdown

MAX_LINES = 5000


def list_text(names, limit=MAX_LINES):
    """Pure function. (text with one name per line, count). Refuses lists that are too long."""
    if len(names) > limit:
        raise ValueError("folder has %d matching files, more than the limit of %d: use an extension filter" % (len(names), limit))
    return "\n".join(names), len(names)


TOO_MANY = ["error", "truncate"]


def plan_listing(entries, sort_by="name", contains="", limit=MAX_LINES, if_too_many="error", prefix=""):
    """Pure function. entries = [(name, mtime, size)]. Returns (names, matched_total, info).

    contains = words that must ALL be in the name (case does not matter). prefix is put in front of every name.
    if_too_many error refuses more than `limit` names; truncate keeps the first `limit` and says so in info.
    """
    if if_too_many not in TOO_MANY:
        raise ValueError("if_too_many must be error or truncate, got %r" % (if_too_many,))
    words = split_words(contains)
    kept = [e for e in entries if all(w in e[0].lower() for w in words)]
    names = sort_entries(kept, sort_by)
    total = len(names)
    notes = []
    if total > limit:
        if if_too_many == "error":
            raise ValueError("folder has %d matching files, more than the limit of %d: use an extension filter, the contains box, or set if_too_many to truncate" % (total, limit))
        names = names[:limit]
        notes.append("Showing the first %d of %d files (if_too_many is truncate)." % (limit, total))
    sizes = {e[0]: e[2] for e in kept}
    listed_bytes = sum(sizes[n] for n in names)
    head = "%d files" % len(names) if not notes else "%d of %d files" % (len(names), total)
    text = "%s, %s, sorted by %s." % (head, format_bytes(listed_bytes), sort_by)
    if words:
        text += " Filter: %s (%d of %d files in the folder matched)." % (" ".join(words), total, len(entries))
    if names:
        text += " Types: %s." % ext_breakdown(names)
    text = " ".join([text] + notes)
    if prefix:
        names = [prefix.rstrip("/") + "/" + n for n in names]
    return names, total, text


class SYListFolderFiles:
    DESCRIPTION = ("Lists the files in a folder inside the input or output folder, one per line, with a count. "
                   "Optional sort_by (name, newest, oldest, largest, smallest), include_subfolders, a contains filter, "
                   "with_subfolder to put the folder in front of each name, if_missing to stop on a wrong folder and "
                   "if_too_many to cut a long list instead of failing. Also gives an info line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("files", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root": (["input", "output"], {"default": "input", "tooltip": "Which ComfyUI folder to look in."}),
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside it. Empty means the folder itself."}),
                "extensions": ("STRING", {"default": "", "tooltip": "File endings to keep, like png, jpg or txt. Empty lists every file."}),
            },
            "optional": {
                "sort_by": (SORT_CHOICES, {"default": "name", "tooltip": "Order of the list: by name, newest or oldest first, largest or smallest first."}),
                "include_subfolders": ("BOOLEAN", {"default": False, "tooltip": "On: also list files in the folders below (names show the folder)."}),
                "contains": ("STRING", {"default": "", "tooltip": "Optional words that must all be in the file name, like 'hero blue'."}),
                "with_subfolder": ("BOOLEAN", {"default": False, "tooltip": "On: put the subfolder in front of each name (handy for loaders)."}),
                "if_missing": (IF_MISSING, {"default": "empty", "tooltip": "empty gives an empty list for a missing folder. error stops with a clear message."}),
                "if_too_many": (TOO_MANY, {"default": "error", "tooltip": "error refuses more than 5000 files. truncate keeps the first 5000."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, root, subfolder, extensions, **kw):
        return float("nan")

    def run(self, root, subfolder, extensions, sort_by="name", include_subfolders=False, contains="", with_subfolder=False,
            if_missing="empty", if_too_many="error"):
        folder = safe_join(root_folder(root), subfolder)
        exts = parse_extensions(extensions, default=()) or None
        if not check_if_missing(folder, root, subfolder, if_missing):
            return ("", 0, "The folder %s/%s does not exist, so the list is empty." % (root, str(subfolder).strip()))
        entries = scan_folder(folder, exts, include_subfolders, limit=200000)
        prefix = str(subfolder or "").strip().replace("\\", "/").strip("/") if with_subfolder else ""
        names, _total, info = plan_listing(entries, sort_by, contains, MAX_LINES, if_too_many, prefix)
        return ("\n".join(names), len(names), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ListFolderFiles", SYListFolderFiles)
NODE_DISPLAY_NAME_MAPPINGS["SYListFolderFiles"] = "List Folder Files SY"
