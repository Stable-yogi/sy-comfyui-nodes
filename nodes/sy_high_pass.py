"""High Pass SY: keeps only the fine detail of a picture and flattens the rest to mid grey."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OUTPUTS = ("grey detail", "added to original")


def check_settings(radius, strength, output):
    if not 1 <= int(radius) <= 100:
        raise ValueError("radius must be between 1 and 100, got %r" % (radius,))
    if not 0.0 <= float(strength) <= 4.0:
        raise ValueError("strength must be between 0 and 4, got %r" % (strength,))
    if output not in OUTPUTS:
        raise ValueError("output must be one of: %s, got %r" % (", ".join(OUTPUTS), output))


def high_pass_value(original, blurred, strength):
    """Pure function. clamp(0.5 + (original - blurred) * strength, 0, 1)."""
    return max(0.0, min(1.0, 0.5 + (original - blurred) * strength))


def added_value(original, blurred, strength):
    """Pure function. The picture with its fine detail boosted (original + detail * strength), clamped."""
    return max(0.0, min(1.0, original + (original - blurred) * strength))


def gaussian_kernel(radius):
    """Pure function. Normalised 1-D blur weights for a radius in pixels (sigma = radius / 2)."""
    if radius < 1:
        raise ValueError("radius must be at least 1, got %r" % (radius,))
    sigma = radius / 2.0
    half = int(math.ceil(sigma * 3.0))
    weights = [math.exp(-(k * k) / (2.0 * sigma * sigma)) for k in range(-half, half + 1)]
    total = sum(weights)
    return [w / total for w in weights]


def blur_tensor(x, radius):
    """Torch. Separable gaussian blur of x [B,C,H,W]; pixels past the edge repeat the edge pixel."""
    import torch
    import torch.nn.functional as F

    k = torch.tensor(gaussian_kernel(radius), dtype=x.dtype, device=x.device)
    half = (k.shape[0] - 1) // 2
    ch = x.shape[1]
    h, w = x.shape[2], x.shape[3]
    xi = torch.arange(-half, w + half, device=x.device).clamp(0, w - 1)
    yi = torch.arange(-half, h + half, device=x.device).clamp(0, h - 1)
    kh = k.view(1, 1, 1, -1).repeat(ch, 1, 1, 1)
    kv = k.view(1, 1, -1, 1).repeat(ch, 1, 1, 1)
    x = F.conv2d(x.index_select(3, xi), kh, groups=ch)
    return F.conv2d(x.index_select(2, yi), kv, groups=ch)


def high_pass_tensor(image, radius, strength, output):
    """Torch. image [B,H,W,C] float 0..1 -> new tensor of the same shape. Alpha is passed through."""
    import torch

    check_settings(radius, strength, output)
    img = image.float()
    colour = img[..., :3] if img.shape[3] == 4 else img
    blurred = blur_tensor(colour.permute(0, 3, 1, 2), int(radius)).permute(0, 2, 3, 1)
    detail = (colour - blurred) * float(strength)
    out = (0.5 + detail) if output == "grey detail" else (colour + detail)
    out = out.clamp(0.0, 1.0)
    if img.shape[3] == 4:
        out = torch.cat([out, img[..., 3:4]], dim=3)
    return out.contiguous()


class SYHighPass:
    DESCRIPTION = ("Keeps only the fine detail of a picture and turns everything else mid grey. Use it to see texture, "
                   "or choose 'added to original' to sharpen the picture.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture (or batch of pictures) to filter."}),
            "radius": ("INT", {"default": 6, "min": 1, "max": 100, "tooltip": "Detail bigger than this many pixels is removed. Small keeps only fine texture."}),
            "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 4.0, "step": 0.05, "tooltip": "How strongly the detail shows. 0 gives flat grey (or the original)."}),
            "output": (list(OUTPUTS), {"default": "grey detail", "tooltip": "Show the detail on grey, or add the detail back onto the original to sharpen."}),
        }}

    def run(self, image, radius, strength, output):
        return (high_pass_tensor(image, radius, strength, output),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HighPass", SYHighPass)
NODE_DISPLAY_NAME_MAPPINGS["SYHighPass"] = "High Pass SY"
