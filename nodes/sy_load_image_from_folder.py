"""Load Image From Folder SY: loads the Nth picture of a sub folder of the input folder, wrapping at the end."""
import os

try:
    from ._sy_safe_paths import IMAGE_EXTENSIONS, list_files, pick_index, root_folder, safe_join
    from ._sy_common import category, register
    from ._sy_a1_folders import index_by_mode
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import IMAGE_EXTENSIONS, list_files, pick_index, root_folder, safe_join
    from _sy_common import category, register
    from _sy_a1_folders import index_by_mode

SORTS = ["name", "date", "newest", "largest", "smallest"]
INDEX_MODES = ["wrap", "clamp", "error"]


def order_files(entries, sort_by):
    """Pure function. entries = [(name, mtime)] or [(name, mtime, size)]. name = A to Z ignoring case, date = oldest first,
    newest = newest first, largest / smallest need the size (third value)."""
    if sort_by == "name":
        return [e[0] for e in sorted(entries, key=lambda e: (e[0].lower(), e[0]))]
    if sort_by == "date":
        return [e[0] for e in sorted(entries, key=lambda e: (e[1], e[0].lower(), e[0]))]
    if sort_by == "newest":
        return [e[0] for e in sorted(entries, key=lambda e: (-e[1], e[0].lower(), e[0]))]
    if sort_by in ("largest", "smallest"):
        if any(len(e) < 3 for e in entries):
            raise ValueError("sort_by %s needs the file sizes" % sort_by)
        sign = -1 if sort_by == "largest" else 1
        return [e[0] for e in sorted(entries, key=lambda e: (sign * e[2], e[0].lower(), e[0]))]
    raise ValueError("sort_by must be one of: %s, got %r" % (", ".join(SORTS), sort_by))


def choose_file(entries, index, sort_by):
    """Pure function. The file at `index` after sorting. Too big or negative numbers wrap around."""
    ordered = order_files(entries, sort_by)
    return ordered[pick_index(len(ordered), index)]


def pick_file(entries, index, sort_by, index_mode="wrap"):
    """Pure function. Returns (name, index_used, count, info). index_mode: wrap goes round, clamp stays on the last
    picture, error refuses an index that does not exist."""
    if index_mode not in INDEX_MODES:
        raise ValueError("index_mode must be wrap, clamp or error, got %r" % (index_mode,))
    ordered = order_files(entries, sort_by)
    used = index_by_mode(len(ordered), index, index_mode)
    info = "Picture %d of %d (index %d, sorted by %s): %s." % (used + 1, len(ordered), used, sort_by, ordered[used])
    if used != int(index):
        info += " Index %d was %s to %d." % (int(index), "wrapped" if index_mode == "wrap" else "limited", used)
    return ordered[used], used, len(ordered), info


class SYLoadImageFromFolder:
    DESCRIPTION = ("Loads one picture from a folder inside the ComfyUI input folder. The index picks which one and wraps around. "
                   "Extra sort options (newest, largest, smallest) and an index_mode (wrap, clamp, error) are optional. "
                   "Also gives the index really used, the number of pictures and an info line. A damaged picture gets a plain message.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "filename", "index_used", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside the input folder. Empty means the input folder itself."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Which picture to load, from 0. Too big a number wraps to the start."}),
                "sort_by": (SORTS, {"default": "name", "tooltip": "Order of the pictures: by file name, date (oldest first), newest first, largest or smallest."}),
            },
            "optional": {
                "index_mode": (INDEX_MODES, {"default": "wrap", "tooltip": "wrap goes round at the end. clamp stays on the last picture. error stops."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, subfolder, index, sort_by, index_mode="wrap"):
        try:
            folder = safe_join(root_folder("input"), subfolder)
            return repr(sorted((n, os.path.getmtime(os.path.join(folder, n))) for n in list_files(folder, IMAGE_EXTENSIONS)))
        except Exception:
            return float("nan")

    def run(self, subfolder, index, sort_by, index_mode="wrap"):
        import numpy as np
        import torch
        from PIL import Image, ImageOps

        folder = safe_join(root_folder("input"), subfolder)
        names = list_files(folder, IMAGE_EXTENSIONS)
        if not names:
            raise ValueError("no pictures found in the input folder %r. Put picture files there." % subfolder)
        entries = []
        for n in names:
            st = os.stat(os.path.join(folder, n))
            entries.append((n, st.st_mtime, st.st_size))
        name, used, count, info = pick_file(entries, index, sort_by, index_mode)
        try:
            with Image.open(os.path.join(folder, name)) as src:
                img = ImageOps.exif_transpose(src)
                has_alpha = "A" in img.getbands() or "transparency" in img.info
                rgba = img.convert("RGBA")
        except (OSError, SyntaxError, ValueError, Image.DecompressionBombError):
            raise ValueError("The picture %r could not be read. The file may be damaged or not really a picture. Remove it or pick another index." % name)
        arr = np.asarray(rgba).astype(np.float32) / 255.0
        rgb = torch.from_numpy(arr[:, :, :3].copy())[None, ...]
        if has_alpha:
            mask = 1.0 - torch.from_numpy(arr[:, :, 3].copy())
        else:
            mask = torch.zeros((arr.shape[0], arr.shape[1]), dtype=torch.float32)
        return (rgb, mask.unsqueeze(0), name, used, count, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadImageFromFolder", SYLoadImageFromFolder)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadImageFromFolder"] = "Load Image From Folder SY"
