"""Load Image Mini SY: loads one picture from the ComfyUI input folder, with its mask and size."""
import os

try:
    from ._sy_common import category, register, safe_join
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join
    import _sy_d2_common as d2

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


def match_name(wanted, names):
    """Pure function. Finds the wanted file in a list of names. An exact match wins, then a match ignoring upper/lower case.
    Returns (name, suggestions): name is '' when not found, suggestions are up to 3 close names to show in the error."""
    wanted = normalize_filename(wanted)
    if wanted in names:
        return wanted, []
    low = wanted.lower()
    same = [n for n in names if n.lower() == low]
    if same:
        return sorted(same)[0], []
    stem = low.rsplit(".", 1)[0]
    close = [n for n in names if stem and (stem in n.lower() or n.lower().rsplit(".", 1)[0] in low)]
    return "", sorted(close)[:3]


def crop_to_multiple_box(width, height, multiple):
    """Pure function. (left, top, new_w, new_h): cuts the picture down to a multiple, taking equal amounts off both sides."""
    multiple = int(multiple)
    if multiple < 1:
        raise ValueError("crop_to_multiple must be at least 1, got %d" % multiple)
    if width < multiple or height < multiple:
        raise ValueError("the picture (%s) is smaller than crop_to_multiple %d; use a smaller number" % (d2.size_text(width, height), multiple))
    nw, nh = (width // multiple) * multiple, (height // multiple) * multiple
    return ((width - nw) // 2, (height - nh) // 2, nw, nh)


def max_mp_size(width, height, max_mp):
    """Pure function. New (width, height) so that the picture has at most max_mp megapixels (0 = off), same shape."""
    if max_mp < 0:
        raise ValueError("max_megapixels cannot be negative, got %s" % max_mp)
    area = width * height
    if max_mp == 0 or area <= max_mp * 1000000.0:
        return width, height
    s = (max_mp * 1000000.0 / area) ** 0.5
    return max(1, int(width * s)), max(1, int(height * s))


def load_info(name, orig_w, orig_h, out_w, out_h, has_alpha, steps):
    """Pure function. One plain line about what was loaded and what was changed."""
    text = "%s: %s" % (name, d2.size_text(orig_w, orig_h))
    if (orig_w, orig_h) != (out_w, out_h):
        text += " -> %s" % d2.size_text(out_w, out_h)
    text += ", " + ("has transparency (the mask is the transparent part)" if has_alpha else "no transparency (the mask is empty)")
    if steps:
        text += "; " + "; ".join(steps)
    return text + "."


def _input_dir():
    import folder_paths
    return folder_paths.get_input_directory()


class SYLoadImageMini:
    DESCRIPTION = ("Loads one picture from the ComfyUI input folder. Gives the image, its mask and its size. "
                   "Can trim it to a multiple of 8 or 64, or cap its megapixels. Finds the file even if the capital letters differ.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        try:
            files = list_image_files(os.listdir(_input_dir()))
        except Exception:
            files = []
        return {
            "required": {"image": (files, {"tooltip": "The picture file in the ComfyUI input folder."})},
            "optional": {
                "crop_to_multiple": ("INT", {"default": 1, "min": 1, "max": 512, "tooltip": "Trim the edges so width and height are multiples of this (8 or 64 suit most models). 1 is off."}),
                "max_megapixels": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 268.0, "step": 0.1, "tooltip": "Shrink a picture bigger than this many megapixels, keeping its shape. 0 is off."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, image, crop_to_multiple=1, max_megapixels=0.0):
        try:
            return os.path.getmtime(safe_join(_input_dir(), normalize_filename(image)))
        except Exception:
            return float("nan")

    def run(self, image, crop_to_multiple=1, max_megapixels=0.0):
        import numpy as np
        import torch
        from PIL import Image, ImageOps

        folder = _input_dir()
        path = safe_join(folder, normalize_filename(image))  # refuses paths outside the input folder
        if not os.path.isfile(path):
            try:
                found, close = match_name(image, list_image_files(os.listdir(folder)))
            except OSError:
                found, close = "", []
            if found:
                path = safe_join(folder, found)
            else:
                raise ValueError("picture not found in the input folder: %s%s" % (
                    image, " (did you mean: %s?)" % ", ".join(close) if close else ""))
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
        mask = mask.unsqueeze(0)
        orig_h, orig_w = int(arr.shape[0]), int(arr.shape[1])
        steps = []
        nw, nh = max_mp_size(orig_w, orig_h, max_megapixels)
        if (nw, nh) != (orig_w, orig_h):
            import torch.nn.functional as F
            rgb = F.interpolate(rgb.permute(0, 3, 1, 2), size=(nh, nw), mode="bilinear", align_corners=False, antialias=True).permute(0, 2, 3, 1).clamp(0.0, 1.0).contiguous()
            mask = F.interpolate(mask.unsqueeze(1), size=(nh, nw), mode="bilinear", align_corners=False, antialias=True).squeeze(1).clamp(0.0, 1.0).contiguous()
            steps.append("shrunk to stay under %g megapixels" % max_megapixels)
        if crop_to_multiple > 1:
            left, top, cw, ch = crop_to_multiple_box(rgb.shape[2], rgb.shape[1], crop_to_multiple)
            if (cw, ch) != (rgb.shape[2], rgb.shape[1]):
                rgb = rgb[:, top:top + ch, left:left + cw, :].contiguous()
                mask = mask[:, top:top + ch, left:left + cw].contiguous()
                steps.append("trimmed to a multiple of %d" % crop_to_multiple)
        out_w, out_h = int(rgb.shape[2]), int(rgb.shape[1])
        return (rgb, mask, out_w, out_h, load_info(os.path.basename(path), orig_w, orig_h, out_w, out_h, has_alpha, steps))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadImageMini", SYLoadImageMini)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadImageMini"] = "Load Image Mini SY"
