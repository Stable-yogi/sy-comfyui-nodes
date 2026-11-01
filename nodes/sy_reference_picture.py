"""Reference Picture SY: loads a reference picture with a label, an on/off switch and an optional size limit."""
import os

try:
    from ._sy_common import category, register, safe_join
    from .sy_load_image_mini import list_image_files, normalize_filename
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join
    from sy_load_image_mini import list_image_files, normalize_filename

NONE = "(none)"
PLACEHOLDER = 64  # side of the blank picture given when the slot is off


def is_active(enabled, name):
    """Pure function. A slot is active only when it is switched on and a real file is picked."""
    return bool(enabled) and isinstance(name, str) and name.strip() != "" and name != NONE


def fit_size(width, height, max_side):
    """Pure function. Scales down so the longest side is at most max_side, keeping the shape. 0 keeps the size. Never scales up."""
    width, height, max_side = int(width), int(height), int(max_side)
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1, got %dx%d" % (width, height))
    if max_side <= 0 or max(width, height) <= max_side:
        return width, height
    scale = max_side / float(max(width, height))
    return max(1, round(width * scale)), max(1, round(height * scale))


def make_label(slot, description, active):
    """Pure function. 'Image 1: the hero' for an active slot, an empty text for an inactive one."""
    if not active:
        return ""
    num = int(slot)
    if num < 1:
        raise ValueError("slot must be 1 or more, got %d" % num)
    desc = " ".join(str(description or "").split())
    return ("Image %d: %s" % (num, desc)) if desc else ("Image %d" % num)


def _input_dir():
    import folder_paths
    return folder_paths.get_input_directory()


class SYReferencePicture:
    DESCRIPTION = ("Loads one reference picture and names it for your prompt (Image 1, Image 2 ...). "
                   "An on/off switch turns the slot off without bypassing, and a size limit saves memory.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("image", "mask", "width", "height", "active", "label")

    @classmethod
    def INPUT_TYPES(cls):
        try:
            files = list_image_files(os.listdir(_input_dir()))
        except Exception:
            files = []
        return {
            "required": {
                "image": (files + [NONE], {"image_upload": True, "tooltip": "The picture file in the ComfyUI input folder. You can also upload one."}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off: this slot gives a blank picture and active = false."}),
                "slot": ("INT", {"default": 1, "min": 1, "max": 99, "tooltip": "The number used in the label: Image 1, Image 2 and so on."}),
                "description": ("STRING", {"default": "", "tooltip": "A few words about the picture, e.g. the hero. Goes into the label."}),
                "max_side": ("INT", {"default": 0, "min": 0, "max": 16384, "tooltip": "Longest side in pixels. 0 keeps the original size."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, image, enabled, slot, description, max_side):
        if not is_active(enabled, image):
            return "off"
        try:
            return os.path.getmtime(safe_join(_input_dir(), normalize_filename(image)))
        except Exception:
            return float("nan")

    def run(self, image, enabled, slot, description, max_side):
        import numpy as np
        import torch
        from PIL import Image, ImageOps

        active = is_active(enabled, image)
        label = make_label(slot, description, active)
        if not active:
            blank = torch.zeros((1, PLACEHOLDER, PLACEHOLDER, 3), dtype=torch.float32)
            mask = torch.zeros((1, PLACEHOLDER, PLACEHOLDER), dtype=torch.float32)
            return (blank, mask, PLACEHOLDER, PLACEHOLDER, False, label)

        path = safe_join(_input_dir(), normalize_filename(image))  # refuses paths outside the input folder
        if not os.path.isfile(path):
            raise ValueError("picture not found in the input folder: %s" % image)
        with Image.open(path) as src:
            img = ImageOps.exif_transpose(src)
            has_alpha = "A" in img.getbands() or "transparency" in img.info
            rgba = img.convert("RGBA")
        new_w, new_h = fit_size(rgba.width, rgba.height, max_side)
        if (new_w, new_h) != (rgba.width, rgba.height):
            rgba = rgba.resize((new_w, new_h), Image.LANCZOS)
        arr = np.asarray(rgba).astype(np.float32) / 255.0
        rgb = torch.from_numpy(arr[:, :, :3].copy())[None, ...]
        if has_alpha:
            mask = 1.0 - torch.from_numpy(arr[:, :, 3].copy())
        else:
            mask = torch.zeros((arr.shape[0], arr.shape[1]), dtype=torch.float32)
        return (rgb, mask.unsqueeze(0), int(arr.shape[1]), int(arr.shape[0]), True, label)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ReferencePicture", SYReferencePicture)
NODE_DISPLAY_NAME_MAPPINGS["SYReferencePicture"] = "Reference Picture SY"
