"""Load Image From Folder SY: loads the Nth picture of a sub folder of the input folder, wrapping at the end."""
import os

try:
    from ._sy_safe_paths import IMAGE_EXTENSIONS, list_files, pick_index, root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import IMAGE_EXTENSIONS, list_files, pick_index, root_folder, safe_join
    from _sy_common import category, register

SORTS = ["name", "date"]


def order_files(entries, sort_by):
    """Pure function. entries = [(name, mtime)]. Sorted by name (ignoring case) or by date, oldest first."""
    if sort_by == "name":
        return [n for n, _ in sorted(entries, key=lambda e: (e[0].lower(), e[0]))]
    if sort_by == "date":
        return [n for n, _ in sorted(entries, key=lambda e: (e[1], e[0].lower(), e[0]))]
    raise ValueError("sort_by must be name or date, got %r" % (sort_by,))


def choose_file(entries, index, sort_by):
    """Pure function. The file at `index` after sorting. Too big or negative numbers wrap around."""
    ordered = order_files(entries, sort_by)
    return ordered[pick_index(len(ordered), index)]


class SYLoadImageFromFolder:
    DESCRIPTION = "Loads one picture from a folder inside the ComfyUI input folder. The index picks which one and wraps around."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "filename")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside the input folder. Empty means the input folder itself."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Which picture to load, from 0. Too big a number wraps to the start."}),
                "sort_by": (SORTS, {"default": "name", "tooltip": "Order of the pictures: by file name, or by date (oldest first)."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, subfolder, index, sort_by):
        try:
            folder = safe_join(root_folder("input"), subfolder)
            return repr(sorted((n, os.path.getmtime(os.path.join(folder, n))) for n in list_files(folder, IMAGE_EXTENSIONS)))
        except Exception:
            return float("nan")

    def run(self, subfolder, index, sort_by):
        import numpy as np
        import torch
        from PIL import Image, ImageOps

        folder = safe_join(root_folder("input"), subfolder)
        names = list_files(folder, IMAGE_EXTENSIONS)
        if not names:
            raise ValueError("no pictures found in the input folder %r. Put picture files there." % subfolder)
        entries = [(n, os.path.getmtime(os.path.join(folder, n))) for n in names]
        name = choose_file(entries, index, sort_by)
        with Image.open(os.path.join(folder, name)) as src:
            img = ImageOps.exif_transpose(src)
            has_alpha = "A" in img.getbands() or "transparency" in img.info
            rgba = img.convert("RGBA")
        arr = np.asarray(rgba).astype(np.float32) / 255.0
        rgb = torch.from_numpy(arr[:, :, :3].copy())[None, ...]
        if has_alpha:
            mask = 1.0 - torch.from_numpy(arr[:, :, 3].copy())
        else:
            mask = torch.zeros((arr.shape[0], arr.shape[1]), dtype=torch.float32)
        return (rgb, mask.unsqueeze(0), name)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadImageFromFolder", SYLoadImageFromFolder)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadImageFromFolder"] = "Load Image From Folder SY"
