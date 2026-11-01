"""Folder Image Count SY: counts the pictures in a sub folder of the input or output folder."""
try:
    from ._sy_safe_paths import IMAGE_EXTENSIONS, list_files, root_folder, safe_join, parse_extensions
    from ._sy_common import category, register
    from ._sy_a1_folders import IF_MISSING, scan_folder, check_if_missing, ext_breakdown
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import IMAGE_EXTENSIONS, list_files, root_folder, safe_join, parse_extensions
    from _sy_common import category, register
    from _sy_a1_folders import IF_MISSING, scan_folder, check_if_missing, ext_breakdown


def count_info(folder, root, subfolder, extensions="", include_subfolders=False, if_missing="empty"):
    """Returns (count, last_index, info). folder is the already checked (safe_join) folder.

    extensions empty = the usual picture endings. include_subfolders also counts files in folders below it.
    if_missing 'error' refuses a folder that does not exist instead of answering 0.
    """
    exts = parse_extensions(extensions, IMAGE_EXTENSIONS)
    if not check_if_missing(folder, root, subfolder, if_missing):
        return 0, -1, "The folder %s%s does not exist, so the count is 0." % (root, ("/" + str(subfolder).strip()) if str(subfolder or "").strip() else "")
    if include_subfolders:
        names = [e[0] for e in scan_folder(folder, exts, True)]
    else:
        names = [e[0] for e in scan_folder(folder, exts, False)]
    count = len(names)
    where = "%s/%s" % (root, str(subfolder).strip()) if str(subfolder or "").strip() else root
    if count == 0:
        return 0, -1, "No files with the endings %s in %s%s." % (" ".join(exts), where, " (including subfolders)" if include_subfolders else "")
    return count, count - 1, "%d files in %s%s: %s. Valid index numbers are 0 to %d." % (
        count, where, " (including subfolders)" if include_subfolders else "", ext_breakdown(names), count - 1)


class SYFolderImageCount:
    DESCRIPTION = ("Counts the picture files (png, jpg, jpeg, webp, bmp, gif, tif) in a folder inside the input or output folder. "
                   "Optional extensions count other file types, include_subfolders looks deeper, and if_missing can stop with a "
                   "clear message for a folder that is not there. Also gives the last valid index and an info line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("count", "last_index", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root": (["input", "output"], {"default": "input", "tooltip": "Which ComfyUI folder to look in."}),
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside it. Empty means the folder itself."}),
            },
            "optional": {
                "extensions": ("STRING", {"default": "", "tooltip": "Optional endings to count, like 'png, webp'. Empty counts all picture types."}),
                "include_subfolders": ("BOOLEAN", {"default": False, "tooltip": "On: also count files in the folders below."}),
                "if_missing": (IF_MISSING, {"default": "empty", "tooltip": "empty answers 0 for a missing folder. error stops with a clear message."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, root, subfolder, **kw):
        return float("nan")

    def run(self, root, subfolder, extensions="", include_subfolders=False, if_missing="empty"):
        folder = safe_join(root_folder(root), subfolder)
        if not extensions.strip() and not include_subfolders and if_missing == "empty":
            count = len(list_files(folder, IMAGE_EXTENSIONS))
            return (count,) + count_info(folder, root, subfolder)[1:]
        return count_info(folder, root, subfolder, extensions, include_subfolders, if_missing)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FolderImageCount", SYFolderImageCount)
NODE_DISPLAY_NAME_MAPPINGS["SYFolderImageCount"] = "Folder Image Count SY"
