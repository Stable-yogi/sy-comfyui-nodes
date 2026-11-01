"""Image Exists SY: checks whether a file is present in the input, output or temp folder."""
import difflib
import os
import re

try:
    from ._sy_common import category, register, safe_join
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join

FOLDERS = ("input", "output", "temp")


def check_exists(base_dir, name, folder_label="input"):
    """Pure function. Returns (exists, clean_name). Only a regular file inside base_dir counts."""
    text = "" if name is None else str(name).strip()
    if text == "":
        return False, ""
    msg = "filename must stay inside the %s folder; remove '..' or the full path" % folder_label
    if "\x00" in text:
        raise ValueError(msg)
    clean = text.replace("\\", "/")
    if clean.startswith("/") or re.match(r"^[A-Za-z]:", clean):
        raise ValueError(msg)
    if ".." in clean.split("/"):
        raise ValueError(msg)
    try:
        target = safe_join(base_dir, *[p for p in clean.split("/") if p])
    except ValueError:
        raise ValueError(msg)
    return os.path.isfile(target), clean


TRY_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff")
MAX_SCAN = 5000


def _human_size(n):
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" % (n, unit)) if unit == "bytes" else ("%.1f %s" % (n, unit))
        n /= 1024.0


def find_file(base_dir, name, folder_label="input", ignore_case=False, try_extensions=False):
    """Pure function. Returns (exists, clean_name, found_name, info).

    found_name is the real file name (inside base_dir, with / ) when something matched, else "".
    ignore_case also matches Photo.PNG for photo.png. try_extensions also tries picture endings when `name` has none
    or does not exist. Without either option the answer is exactly the old one. When nothing matches, info lists the
    closest names in the same folder.
    """
    exists, clean = check_exists(base_dir, name, folder_label)
    if not clean:
        return False, "", "", "No file name given, so nothing to look for."
    found = clean if exists else ""
    parent_rel, _, leaf = clean.rpartition("/")
    parent = safe_join(base_dir, *[p for p in parent_rel.split("/") if p]) if parent_rel else os.path.realpath(base_dir)
    names = []
    if os.path.isdir(parent):
        try:
            names = [n for n in os.listdir(parent) if os.path.isfile(os.path.join(parent, n))][:MAX_SCAN]
        except OSError:
            names = []
    if not found and (ignore_case or try_extensions):
        wanted = [leaf]
        if try_extensions:
            wanted += [leaf + e for e in TRY_EXTENSIONS]
        for w in wanted:
            hit = next((n for n in sorted(names) if (n.lower() == w.lower() if ignore_case else n == w)), "")
            if hit:
                found = (parent_rel + "/" + hit) if parent_rel else hit
                break
    if found:
        full = safe_join(base_dir, *[p for p in found.split("/") if p])
        try:
            size = _human_size(os.path.getsize(full))
        except OSError:
            size = "unknown size"
        how = "" if found == clean else " (matched %r)" % found
        return True, clean, found, "Found %s in the %s folder%s, %s." % (clean, folder_label, how, size)
    close = difflib.get_close_matches(leaf, names, n=3, cutoff=0.5)
    if close:
        hint = " Close names in that folder: %s." % ", ".join(close)
    elif not os.path.isdir(parent):
        hint = " The folder %r does not exist." % (parent_rel or folder_label)
    else:
        hint = " No similar file names in that folder (%d files there)." % len(names)
    return False, clean, "", "Not found: %s in the %s folder.%s" % (clean, folder_label, hint)


class SYImageExists:
    DESCRIPTION = ("Tells you if a file is there. Looks only inside the input, output or temp folder. "
                   "Optional ignore_case and try_extensions find a file when the capital letters or the ending do not match. "
                   "Also gives the real file name found and an info line with the size, or close names when it is missing.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("exists", "full_name", "found_name", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": (list(FOLDERS), {"default": "input", "tooltip": "Which ComfyUI folder to look in."}),
                "filename": ("STRING", {"default": "", "multiline": False, "tooltip": "File name inside that folder, for example refs/hero.png."}),
            },
            "optional": {
                "ignore_case": ("BOOLEAN", {"default": False, "tooltip": "On: Hero.PNG matches hero.png."}),
                "try_extensions": ("BOOLEAN", {"default": False, "tooltip": "On: also try picture endings (png, jpg, webp ...) when the name has none."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, folder, filename, **kw):
        return float("nan")

    def run(self, folder, filename, ignore_case=False, try_extensions=False):
        import folder_paths
        if folder == "output":
            base = folder_paths.get_output_directory()
        elif folder == "temp":
            base = folder_paths.get_temp_directory()
        else:
            base = folder_paths.get_input_directory()
        exists, clean, found, info = find_file(base, filename, folder, ignore_case, try_extensions)
        return (exists, clean, found, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageExists", SYImageExists)
