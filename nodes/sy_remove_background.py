"""Remove Background SY: cut the subject out of a picture in one node, with a model file from the background_removal folder."""
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FOLDER = "background_removal"
NO_MODEL = "(no model installed: use Model Downloader SY)"
BACKGROUNDS = ("transparent", "white", "black", "grey", "green screen")
MAX_PIXELS = 64
TOO_OLD = ("This ComfyUI is too old for Remove Background SY (it needs the built-in background removal). "
           "Update ComfyUI and try again.")

# Colours as floats 0..1 (red, green, blue). "transparent" has no colour.
COLOURS = {
    "white": (1.0, 1.0, 1.0),
    "black": (0.0, 0.0, 0.0),
    "grey": (0.5, 0.5, 0.5),
    "green screen": (0.0, 1.0, 0.0),
}
CUTOUT_FILL_WHEN_TRANSPARENT = "black"


def grow_amount_ok(value, what="grow"):
    """Pure function. A whole number of pixels from -64 to 64, else a plain refusal. Returns the number."""
    if isinstance(value, bool) or not isinstance(value, int):
        try:
            if isinstance(value, bool) or int(value) != value:
                raise ValueError
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("%s must be a whole number of pixels between -%d and %d, got %r" % (what, MAX_PIXELS, MAX_PIXELS, value))
    if value < -MAX_PIXELS or value > MAX_PIXELS:
        raise ValueError("%s must be between -%d and %d pixels, got %d" % (what, MAX_PIXELS, MAX_PIXELS, value))
    return value


def feather_ok(value):
    """Pure function. A whole number of pixels from 0 to 64."""
    v = grow_amount_ok(value, "feather")
    if v < 0:
        raise ValueError("feather must be between 0 and %d pixels, got %d" % (MAX_PIXELS, v))
    return v


def colour_for(name):
    """Pure function. (red, green, blue) floats for a background name, or None for 'transparent'."""
    if name == "transparent":
        return None
    if name not in COLOURS:
        raise ValueError("background must be one of: %s, got %r" % (", ".join(BACKGROUNDS), name))
    return COLOURS[name]


def blend_over(fg_rgb, alpha, bg_rgb):
    """Pure function. One pixel: the subject colour shown over the background colour with the given alpha (0..1)."""
    a = min(1.0, max(0.0, float(alpha)))
    return tuple(f * a + b * (1.0 - a) for f, b in zip(fg_rgb, bg_rgb))


def threshold_value(v, t):
    """Pure function. t = 0 keeps the soft value (clamped to 0..1). t > 0 makes a hard cut: 1.0 at or above t, else 0.0."""
    if t < 0.0 or t > 1.0:
        raise ValueError("threshold must be between 0 and 1, got %r" % (t,))
    v = min(1.0, max(0.0, float(v)))
    if t <= 0.0:
        return v
    return 1.0 if v >= t else 0.0


def check_plain_name(name):
    """Pure function. Refuses empty names, absolute paths, drive letters and '..' parts."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("pick a model file from the list")
    norm = name.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":") or ".." in norm.split("/"):
        raise ValueError("the model must be a plain file name from the list, not a path: %r" % name)
    return name


def model_choices(names):
    """Pure function. The list shown in the model drop-down."""
    names = sorted(n for n in names if isinstance(n, str) and n.strip())
    return names if names else [NO_MODEL]


def list_models():
    try:
        import folder_paths
        return model_choices(folder_paths.get_filename_list(FOLDER))
    except Exception:
        return [NO_MODEL]


def resolve_model_path(name):
    """Full path of the chosen model file. Plain refusals when none is installed or the file is gone."""
    if name == NO_MODEL:
        raise ValueError("No background removal model is installed. Put a model file into the ComfyUI folder "
                         "models/background_removal (or use Model Downloader SY), refresh the page and pick it.")
    check_plain_name(name)
    try:
        import folder_paths
    except Exception:
        raise ValueError("ComfyUI folders are not available, so %r cannot be found" % name)
    path = folder_paths.get_full_path(FOLDER, name)
    if not path or not os.path.isfile(path):
        raise ValueError("The model file %r was not found in models/background_removal. Refresh the page and pick another file." % name)
    return path


# ---------------------------------------------------------------- model (loaded once, kept in memory)
_CACHE = {"path": None, "stamp": None, "model": None}


def _get_model(path):
    stamp = os.path.getmtime(path)
    if _CACHE["model"] is not None and _CACHE["path"] == path and _CACHE["stamp"] == stamp:
        return _CACHE["model"]
    try:
        from comfy.bg_removal_model import load
    except Exception:
        raise ValueError(TOO_OLD)
    model = load(path)
    if model is None:
        raise ValueError("This file is not a background removal model that this ComfyUI understands: %s. Pick a different file." % os.path.basename(path))
    _CACHE.update(path=path, stamp=stamp, model=model)
    return model


def _release(model):
    """Move the model off the graphics card after the run. Never fails the node."""
    try:
        import comfy.model_management as mm
        mm.unload_model_and_clones(model.patcher)
    except Exception:
        pass


# ---------------------------------------------------------------- picture maths (torch is imported inside)
def _grow_shrink(mask, px):
    """mask [B,H,W]. px > 0 grows, px < 0 shrinks (square brush)."""
    if px == 0:
        return mask
    import torch.nn.functional as F
    r = abs(px)
    x = mask.unsqueeze(1)
    if px < 0:
        x = -x
    x = F.max_pool2d(x, (1, 2 * r + 1), stride=1, padding=(0, r))
    x = F.max_pool2d(x, (2 * r + 1, 1), stride=1, padding=(r, 0))
    if px < 0:
        x = -x
    return x.squeeze(1)


def _feather(mask, px):
    """mask [B,H,W]. Soft edge: two box blurs in each direction (close to a Gaussian)."""
    if px <= 0:
        return mask
    import torch.nn.functional as F
    x = mask.unsqueeze(1)
    for _ in range(2):
        x = F.avg_pool2d(x, (1, 2 * px + 1), stride=1, padding=(0, px), count_include_pad=False)
        x = F.avg_pool2d(x, (2 * px + 1, 1), stride=1, padding=(px, 0), count_include_pad=False)
    return x.squeeze(1)


def shape_mask(mask, threshold, grow, feather):
    """mask [B,H,W] floats. Threshold first, then grow or shrink, then feather. Returns floats 0..1."""
    m = mask.clamp(0.0, 1.0)
    if threshold > 0.0:
        m = (m >= threshold).to(m.dtype)
    m = _grow_shrink(m, grow)
    m = _feather(m, feather)
    return m.clamp(0.0, 1.0)


def compose(image, mask, background):
    """image [B,H,W,C>=3], mask [B,H,W] (already shaped). Returns (picture, cutout)."""
    import torch
    rgb = image[..., :3]
    m = mask.unsqueeze(-1).to(device=rgb.device, dtype=rgb.dtype)
    fill_name = CUTOUT_FILL_WHEN_TRANSPARENT if background == "transparent" else background
    fill = torch.tensor(colour_for(fill_name), dtype=rgb.dtype, device=rgb.device).view(1, 1, 1, 3)
    cutout = rgb * m + fill * (1.0 - m)
    if background == "transparent":
        return torch.cat([rgb, m], dim=-1), cutout
    return cutout, cutout


def process(image, mask, threshold, feather, grow, background):
    """Everything after the model: sizes, mask shaping and compositing. Returns (picture, mask, cutout)."""
    import torch
    if getattr(image, "ndim", 0) != 4 or image.shape[-1] < 3:
        raise ValueError("expected a picture batch shaped [batch, height, width, 3 or 4 channels]")
    if mask.ndim == 2:
        mask = mask.unsqueeze(0)
    if mask.ndim != 3:
        raise ValueError("the model returned a mask with an unexpected shape")
    b, h, w, _ = image.shape
    mask = mask.to(device=image.device, dtype=image.dtype)
    if mask.shape[1:] != (h, w):
        mask = torch.nn.functional.interpolate(mask.unsqueeze(1), size=(h, w), mode="bilinear", align_corners=False).squeeze(1)
    if mask.shape[0] != b:
        if mask.shape[0] == 1:
            mask = mask.expand(b, h, w)
        else:
            raise ValueError("the model returned %d masks for %d pictures" % (mask.shape[0], b))
    m = shape_mask(mask, threshold, grow, feather)
    picture, cutout = compose(image, m, background)
    return picture, m, cutout


class SYRemoveBackground:
    DESCRIPTION = ("Cuts the subject out of its background in one step. Pick a background-removal model file, and you get the picture "
                   "with a see-through or coloured background, the cut-out mask (1 = subject) and a flat-colour cut-out. "
                   "Threshold, grow and feather clean up the edge. Works on whole batches.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("image", "mask", "cutout")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture (or batch) to cut the subject out of."}),
                "model": (list_models(), {"tooltip": "Background removal model file from models/background_removal."}),
                "threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01,
                                        "tooltip": "0 keeps the soft edge. Above 0 makes a hard cut at that level."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": MAX_PIXELS, "tooltip": "Soft edge in pixels. 0 = off."}),
                "grow": ("INT", {"default": 0, "min": -MAX_PIXELS, "max": MAX_PIXELS,
                                 "tooltip": "Pixels to widen the subject. Negative numbers shrink it."}),
                "background": (list(BACKGROUNDS), {"default": BACKGROUNDS[0], "tooltip": "What goes behind the subject in the image output."}),
            }
        }

    def run(self, image, model, threshold=0.0, feather=0, grow=0, background="transparent"):
        threshold_value(0.0, float(threshold))
        feather = feather_ok(feather)
        grow = grow_amount_ok(grow)
        colour_for(background)
        if getattr(image, "ndim", 0) != 4 or image.shape[-1] < 3:
            raise ValueError("expected a picture batch shaped [batch, height, width, 3 or 4 channels]")
        path = resolve_model_path(model)
        bg_model = _get_model(path)
        try:
            import torch
            with torch.no_grad():
                mask = bg_model.encode_image(image[..., :3])
            mask = mask.detach()
        finally:
            _release(bg_model)
        picture, m, cutout = process(image, mask, float(threshold), feather, grow, background)
        return (picture, m, cutout)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RemoveBackground", SYRemoveBackground)
NODE_DISPLAY_NAME_MAPPINGS["SYRemoveBackground"] = "Remove Background SY"
