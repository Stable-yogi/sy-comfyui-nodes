"""Tilt Shift SY: miniature-model look. A sharp band, with blur growing away from it."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LEVELS = 5  # number of pre-blurred copies (the first is the sharp original)


def blur_amount(pos, focus_position, focus_width, max_blur):
    """Pure function. Blur radius for a row (or column) at `pos` (0..1 across the picture).
    Zero inside the sharp band, then growing in a straight line to max_blur at the farthest edge."""
    if not (0.0 <= focus_position <= 1.0):
        raise ValueError("focus_position must be between 0 and 1, got %s" % focus_position)
    if not (0.0 <= focus_width <= 1.0):
        raise ValueError("focus_width must be between 0 and 1, got %s" % focus_width)
    if max_blur < 0:
        raise ValueError("blur cannot be negative, got %s" % max_blur)
    outside = abs(pos - focus_position) - focus_width / 2.0
    if outside <= 0:
        return 0.0
    ramp = max(focus_position, 1.0 - focus_position) - focus_width / 2.0
    if ramp <= 1e-9:
        return float(max_blur)
    return float(max_blur) * min(1.0, outside / ramp)


def level_radii(max_blur, levels=LEVELS):
    """Pure function. Blur radius of each pre-blurred copy, from 0 up to max_blur."""
    return [max_blur * i / float(levels - 1) for i in range(levels)]


def mix_position(radius, max_blur, levels=LEVELS):
    """Pure function. (lower copy index, mix toward the next copy 0..1) for a wanted radius."""
    if max_blur <= 0:
        return 0, 0.0
    f = min(float(levels - 1), max(0.0, radius / max_blur * (levels - 1)))
    lo = min(levels - 2, int(f))
    return lo, f - lo


def gaussian_weights(radius):
    """Pure function. Normalised 1-D blur weights; sigma is half the radius."""
    r = int(radius)
    if r < 1:
        raise ValueError("radius must be at least 1, got %s" % radius)
    sigma = max(0.5, r / 2.0)
    w = [pow(2.718281828459045, -(i * i) / (2.0 * sigma * sigma)) for i in range(-r, r + 1)]
    total = sum(w)
    return [v / total for v in w]


def blur_nchw(x, radius):
    """Torch. Separable gaussian blur of [B,C,H,W] with edge-copy padding. Radius below 1 returns x."""
    import torch
    import torch.nn.functional as F

    r = int(round(radius))
    if r < 1:
        return x
    k = torch.tensor(gaussian_weights(r), dtype=x.dtype, device=x.device)
    c = x.shape[1]
    kh = k.view(1, 1, 1, -1).repeat(c, 1, 1, 1)
    kv = k.view(1, 1, -1, 1).repeat(c, 1, 1, 1)
    x = F.conv2d(F.pad(x, (r, r, 0, 0), mode="replicate"), kh, groups=c)
    return F.conv2d(F.pad(x, (0, 0, r, r), mode="replicate"), kv, groups=c)


def tilt_shift_tensor(image, focus_position, focus_width, blur, vertical):
    """Torch [B,H,W,C]. All channels are blurred together. vertical=True: the band runs top to bottom."""
    import torch

    blur_amount(0.5, focus_position, focus_width, blur)  # checks the values
    if blur <= 0:
        return image
    x = image.permute(0, 3, 1, 2).float()
    n = x.shape[3] if vertical else x.shape[2]
    copies = [blur_nchw(x, r) for r in level_radii(blur)]
    stack = torch.stack(copies, dim=0)  # [L,B,C,H,W]
    lo = []
    frac = []
    for i in range(n):
        a, b = mix_position(blur_amount((i + 0.5) / n, focus_position, focus_width, blur), blur)
        lo.append(a)
        frac.append(b)
    lo_t = torch.tensor(lo, device=x.device)
    frac_t = torch.tensor(frac, dtype=x.dtype, device=x.device)
    sel = lo_t.view(1, 1, 1, 1, n) if vertical else lo_t.view(1, 1, 1, n, 1)
    sel = sel.expand(1, x.shape[0], x.shape[1], x.shape[2], x.shape[3])
    lower = torch.gather(stack, 0, sel)[0]
    sel2 = (sel + 1).clamp(max=LEVELS - 1)
    upper = torch.gather(stack, 0, sel2)[0]
    f = frac_t.view(1, 1, 1, n) if vertical else frac_t.view(1, 1, n, 1)
    out = lower * (1.0 - f) + upper * f
    return out.permute(0, 2, 3, 1).to(image.dtype).contiguous()


class SYTiltShift:
    DESCRIPTION = ("Gives the miniature-model look: one band of the picture stays sharp and the rest gets blurrier "
                   "the farther it is from the band. Blur 0 leaves the picture as it is.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to turn into a miniature look."}),
            "focus_position": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the sharp band sits: 0 is the top (or left), 1 the bottom (or right)."}),
            "focus_width": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How wide the sharp band is, as a share of the picture."}),
            "blur": ("FLOAT", {"default": 12.0, "min": 0.0, "max": 40.0, "step": 0.5, "tooltip": "The biggest blur in pixels, reached at the far edge. 0 does nothing."}),
            "vertical": ("BOOLEAN", {"default": False, "tooltip": "Off: the band runs left to right. On: the band runs top to bottom."}),
        }}

    def run(self, image, focus_position, focus_width, blur, vertical):
        return (tilt_shift_tensor(image, focus_position, focus_width, blur, vertical),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TiltShift", SYTiltShift)
NODE_DISPLAY_NAME_MAPPINGS["SYTiltShift"] = "Tilt Shift SY"
