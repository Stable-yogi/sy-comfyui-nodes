"""Shared pure helpers for the batch A1 folder nodes: scan with sizes and dates, sort, missing-folder message.

Paths are always built by the caller with safe_join. These helpers only read a folder that was already checked.
"""
import os

SORT_CHOICES = ["name", "newest", "oldest", "largest", "smallest"]
IF_MISSING = ["empty", "error"]


def scan_folder(folder, exts=None, recursive=False, limit=200000):
    """Files in `folder` as [(relative_name, mtime, size)]. Relative names use '/'. Missing folder gives [].

    exts = tuple of lower case endings like ('.png',) or None for every file. Symbolic links to folders are not followed.
    """
    if not os.path.isdir(folder):
        return []
    exts = tuple(e.lower() for e in exts) if exts else None
    out = []
    if recursive:
        for root, dirs, files in os.walk(folder, followlinks=False):
            dirs.sort()
            for n in files:
                _add(out, folder, os.path.join(root, n), exts)
                if len(out) > limit:
                    raise ValueError("the folder holds more than %d files; pick a smaller folder or an extension filter" % limit)
    else:
        for n in os.listdir(folder):
            _add(out, folder, os.path.join(folder, n), exts)
    return out


def _add(out, folder, path, exts):
    if not os.path.isfile(path):
        return
    if exts and os.path.splitext(path)[1].lower() not in exts:
        return
    try:
        st = os.stat(path)
    except OSError:
        return
    rel = os.path.relpath(path, folder).replace("\\", "/")
    out.append((rel, st.st_mtime, st.st_size))


def sort_entries(entries, sort_by):
    """Pure function. entries = [(name, mtime, size)] -> names in the asked order. Ties fall back to the name."""
    key_name = lambda e: (e[0].lower(), e[0])  # noqa: E731
    if sort_by == "name":
        ordered = sorted(entries, key=key_name)
    elif sort_by == "newest":
        ordered = sorted(entries, key=lambda e: (-e[1],) + key_name(e))
    elif sort_by == "oldest":
        ordered = sorted(entries, key=lambda e: (e[1],) + key_name(e))
    elif sort_by == "largest":
        ordered = sorted(entries, key=lambda e: (-e[2],) + key_name(e))
    elif sort_by == "smallest":
        ordered = sorted(entries, key=lambda e: (e[2],) + key_name(e))
    else:
        raise ValueError("sort_by must be one of: %s, got %r" % (", ".join(SORT_CHOICES), sort_by))
    return [e[0] for e in ordered]


def check_if_missing(folder, label, subfolder, if_missing):
    """Pure-ish. Returns True when the folder exists. For a missing folder: False, or a plain error if_missing is 'error'."""
    if if_missing not in IF_MISSING:
        raise ValueError("if_missing must be one of: %s, got %r" % (", ".join(IF_MISSING), if_missing))
    if os.path.isdir(folder):
        return True
    if if_missing == "error":
        where = ("%s/%s" % (label, subfolder)) if str(subfolder or "").strip() else label
        raise ValueError("The folder %r was not found inside the ComfyUI %s folder. Check the spelling or create the folder." % (where, label))
    return False


def ext_breakdown(names):
    """Pure function. ['a.png', 'b.PNG', 'c.jpg'] -> 'png 2, jpg 1' (biggest group first)."""
    counts = {}
    for n in names:
        e = os.path.splitext(n)[1].lower().lstrip(".") or "no ending"
        counts[e] = counts.get(e, 0) + 1
    return ", ".join("%s %d" % kv for kv in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def index_by_mode(total, index, mode):
    """Pure function. Which item to use: 'wrap' goes round, 'clamp' stays on the last, 'error' refuses a too-big number."""
    total, index = int(total), int(index)
    if total <= 0:
        raise ValueError("the folder has no matching files")
    if mode == "wrap":
        return index % total
    if mode == "clamp":
        return max(0, min(index, total - 1))
    if mode == "error":
        if not (0 <= index < total):
            raise ValueError("index %d does not exist: the folder has %d files (numbers 0 to %d). Lower the index or use wrap." % (index, total, total - 1))
        return index
    raise ValueError("index_mode must be wrap, clamp or error, got %r" % (mode,))
