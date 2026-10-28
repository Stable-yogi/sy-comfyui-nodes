"""Load Image Mini SY: loads one picture from the ComfyUI input folder, with its mask and size."""
import os

try:
    from ._sy_common import category, register, safe_join
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join

EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
TAG = " [input]"


def list_image_files(names):
    """Pure function. Keeps names with an allowed picture extension, sorted ignoring case."""
    keep = [n for n in names if isinstance(n, str) and n.lower().endswith(EXTENSIONS)]
    return sorted(keep, key=lambda s: (s.lower(), s))


def normalize_filename(name):
    """Pure function. Trims spaces, uses forward slashes, drops a leading ./ and an input tag."""
    text = str(name).strip().replace("\\", "/")
    if text.endswith(TAG):
        text = text[:-len(TAG)].rstrip()
    while text.startswith("./"):
        text = text[2:]
    if not text:
        raise ValueError("file name is empty")
    return text


def _input_dir():
    import folder_paths
    return folder_paths.get_input_directory()


class SYLoadImageMini:
    DESCRIPTION = "Loads one picture from the ComfyUI input folder. Gives the image, its mask and its size."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        try:
            files = list_image_files(os.listdir(_input_dir()))
        except Exception:
            files = []
        return {"required": {"image": (files, {"tooltip": "The picture file in the ComfyUI input folder."})}}

    @classmethod
    def IS_CHANGED(cls, image):
        try:
            return os.path.getmtime(safe_join(_input_dir(), normalize_filename(image)))
        except Exception:
            return float("nan")

    def run(self, image):
        import numpy as np
        import torch
        from PIL import Image, ImageOps

        path = safe_join(_input_dir(), normalize_filename(image))  # refuses paths outside the input folder
        if not os.path.isfile(path):
            raise ValueError("picture not found in the input folder: %s" % image)
        with Image.open(path) as src:
            img = ImageOps.exif_transpose(src)
            has_alpha = "A" in img.getbands() or "transparency" in img.info
            rgba = img.convert("RGBA")
        arr = np.asarray(rgba).astype(np.float32) / 255.0
        rgb = torch.from_numpy(arr[:, :, :3].copy())[None, ...]
        if has_alpha:
            mask = 1.0 - torch.from_numpy(arr[:, :, 3].copy())
        else:
            mask = torch.zeros((arr.shape[0], arr.shape[1]), dtype=torch.float32)
        return (rgb, mask.unsqueeze(0), int(arr.shape[1]), int(arr.shape[0]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadImageMini", SYLoadImageMini)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadImageMini"] = "Load Image Mini SY"
