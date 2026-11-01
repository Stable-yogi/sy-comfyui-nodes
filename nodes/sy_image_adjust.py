"""Image Adjust SY: one finishing node for a picture. Tone, colour, sharpen, vignette and grain, each group with its own switch."""
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, blur_tensor
    from . import _sy_d1_finish as fin
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, blur_tensor
    import _sy_d1_finish as fin

LUMA = (0.2126, 0.7152, 0.0722)
MAX_DEGREES = 180.0
GROUPS = ("tone", "colour", "sharpen", "vignette", "grain")


def _clamp(v):
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def check_settings(brightness, contrast, gamma, saturation, hue, warmth, tint, sharpen, sharpen_radius, vignette, vignette_size, grain, grain_size):
    """Pure function. Plain refusals before any work starts."""
    if gamma <= 0:
        raise ValueError("gamma must be above 0, got %s" % gamma)
    if contrast < 0 or saturation < 0:
        raise ValueError("contrast and saturation cannot be negative")
    if abs(hue) > MAX_DEGREES:
        raise ValueError("hue must be between -180 and 180 degrees, got %s" % hue)
    if not (-1.0 <= warmth <= 1.0 and -1.0 <= tint <= 1.0):
        raise ValueError("warmth and tint must be between -1 and 1, got %s and %s" % (warmth, tint))
    if sharpen < 0 or sharpen_radius <= 0:
        raise ValueError("sharpen must be 0 or more and sharpen_radius above 0, got %s and %s" % (sharpen, sharpen_radius))
    if not (0.0 <= vignette <= 1.0) or not (0.1 <= vignette_size <= 2.0):
        raise ValueError("vignette must be between 0 and 1 and vignette_size between 0.1 and 2")
    if not (0.0 <= grain <= 1.0) or grain_size < 1:
        raise ValueError("grain must be between 0 and 1 and grain_size at least 1")


def _inverse3(a):
    """Pure function. Inverse of a 3x3 matrix given as three rows."""
    (p, q, r), (s, t, u), (v, w, x) = a
    det = p * (t * x - u * w) - q * (s * x - u * v) + r * (s * w - t * v)
    return (((t * x - u * w) / det, (r * w - q * x) / det, (q * u - r * t) / det),
            ((u * v - s * x) / det, (p * x - r * v) / det, (r * s - p * u) / det),
            ((s * w - t * v) / det, (q * v - p * w) / det, (p * t - q * s) / det))


def hue_matrix(degrees):
    """Pure function. 3x3 matrix (nine numbers, row by row) that turns the colours round the colour wheel.
    Works in a luma-keeping colour space, so brightness stays the same. 0 degrees is the identity."""
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    # RGB -> YIQ, rotate I/Q, back to RGB
    to_yiq = ((0.299, 0.587, 0.114), (0.596, -0.274, -0.322), (0.211, -0.523, 0.312))
    rot = ((1, 0, 0), (0, c, -s), (0, s, c))
    from_yiq = _inverse3(to_yiq)  # exact inverse, so 0 degrees is exactly the identity

    def mul(x, y):
        return tuple(tuple(sum(x[i][k] * y[k][j] for k in range(3)) for j in range(3)) for i in range(3))

    m = mul(from_yiq, mul(rot, to_yiq))
    return tuple(v for row in m for v in row)


def warmth_gains(warmth, tint):
    """Pure function. (red, green, blue) multipliers. Warmth + is orange, - is blue. Tint + is magenta, - is green."""
    r = 1.0 + 0.20 * warmth + 0.075 * tint
    g = 1.0 - 0.15 * tint
    b = 1.0 - 0.20 * warmth + 0.075 * tint
    return (r, g, b)


def vignette_factor(nx, ny, strength, size):
    """Pure function. Light left at a spot. nx, ny run from -1 (left/top) to 1 (right/bottom).
    1 in the middle, down to 1 - strength in the corners. A bigger size pushes the dark edge outward."""
    d = math.sqrt(nx * nx + ny * ny) / (math.sqrt(2.0) * size)
    t = _clamp((d - 0.35) / 0.65)
    t = t * t * (3.0 - 2.0 * t)
    return 1.0 - strength * t


def adjust_pixel(rgb, brightness=0.0, contrast=1.0, gamma=1.0, saturation=1.0, hue=0.0, warmth=0.0, tint=0.0, use_tone=True, use_colour=True):
    """Pure function. Tone then colour for one pixel (three numbers 0..1). Neutral settings change nothing."""
    v = [_clamp(c) for c in rgb]
    if use_tone:
        v = [_clamp((c ** (1.0 / gamma) - 0.5) * contrast + 0.5 + brightness) for c in v]
    if use_colour:
        lum = sum(w * c for w, c in zip(LUMA, v))
        v = [_clamp(lum + (c - lum) * saturation) for c in v]
        if hue:
            m = hue_matrix(hue)
            v = [_clamp(m[3 * i] * v[0] + m[3 * i + 1] * v[1] + m[3 * i + 2] * v[2]) for i in range(3)]
        g = warmth_gains(warmth, tint)
        v = [_clamp(c * k) for c, k in zip(v, g)]
    return v


def active_groups(use_tone, use_colour, use_sharpen, use_vignette, use_grain, brightness, contrast, gamma, saturation, hue, warmth, tint,
                  sharpen, vignette, grain):
    """Pure function. Which groups really change the picture (switched on AND not at the neutral value)."""
    out = []
    if use_tone and (brightness != 0.0 or contrast != 1.0 or gamma != 1.0):
        out.append("tone")
    if use_colour and (saturation != 1.0 or hue != 0.0 or warmth != 0.0 or tint != 0.0):
        out.append("colour")
    if use_sharpen and sharpen > 0.0:
        out.append("sharpen")
    if use_vignette and vignette > 0.0:
        out.append("vignette")
    if use_grain and grain > 0.0:
        out.append("grain")
    return out


def adjust_info(groups, switched_off, enabled, mix, masked):
    """Pure function. One plain sentence."""
    if not enabled:
        return "Image Adjust: switched off, picture passed through unchanged"
    if not groups:
        why = " (%s switched off)" % ", ".join(switched_off) if switched_off else ""
        return "Image Adjust: every setting is neutral%s, the picture was not changed" % why
    return fin.info_line("Image Adjust", True, mix, masked, "applied " + ", ".join(groups))


def _tone_colour(rgb, brightness, contrast, gamma, saturation, hue, warmth, tint, use_tone, use_colour):
    import torch
    v = rgb.clamp(0.0, 1.0)
    if use_tone:
        v = ((v ** (1.0 / gamma) - 0.5) * contrast + 0.5 + brightness).clamp(0.0, 1.0)
    if use_colour:
        w = torch.tensor(LUMA, dtype=v.dtype, device=v.device)
        lum = (v * w).sum(dim=-1, keepdim=True)
        v = (lum + (v - lum) * saturation).clamp(0.0, 1.0)
        if hue:
            m = torch.tensor(hue_matrix(hue), dtype=v.dtype, device=v.device).view(3, 3)
            v = (v @ m.T).clamp(0.0, 1.0)
        g = torch.tensor(warmth_gains(warmth, tint), dtype=v.dtype, device=v.device)
        v = (v * g).clamp(0.0, 1.0)
    return v


def _vignette(v, strength, size):
    import torch
    h, w = v.shape[1], v.shape[2]
    ys = torch.linspace(-1.0, 1.0, h, device=v.device, dtype=v.dtype).view(h, 1).expand(h, w)
    xs = torch.linspace(-1.0, 1.0, w, device=v.device, dtype=v.dtype).view(1, w).expand(h, w)
    d = torch.sqrt(xs * xs + ys * ys) / (math.sqrt(2.0) * size)
    t = ((d - 0.35) / 0.65).clamp(0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)
    return (v * (1.0 - strength * t).view(1, h, w, 1)).clamp(0.0, 1.0)


def _grain(v, amount, size, seed):
    import torch
    import torch.nn.functional as F
    b, h, w = v.shape[0], v.shape[1], v.shape[2]
    gen = torch.Generator(device="cpu")
    gen.manual_seed(int(seed))
    gh, gw = max(1, h // int(size)), max(1, w // int(size))
    noise = torch.randn((b, 1, gh, gw), generator=gen)
    if size > 1:
        noise = F.interpolate(noise, size=(h, w), mode="bilinear", align_corners=False)
    noise = noise.permute(0, 2, 3, 1).to(device=v.device, dtype=v.dtype)
    lum = (v * torch.tensor(LUMA, dtype=v.dtype, device=v.device)).sum(dim=-1, keepdim=True)
    weight = 1.0 - (2.0 * lum - 1.0).abs() * 0.5  # a little less grain in pure black and pure white
    return (v + noise * (0.12 * amount) * weight).clamp(0.0, 1.0)


class SYImageAdjust:
    DESCRIPTION = ("One finishing node instead of five: tone (brightness, contrast, gamma), colour (saturation, hue, warmth, tint), "
                   "sharpen, vignette and film grain. Each group has its own switch, plus a mask, a mix slider and an overall on/off. "
                   "Every setting starts neutral, so nothing changes until you move one. The info line lists what was applied.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to finish."}),
            },
            "optional": {
                "brightness": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Adds light. Below 0 darkens, above 0 brightens. Try 0.05."}),
                "contrast": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Spread between dark and light. 1 is unchanged, 1.15 is a gentle boost."}),
                "gamma": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.01, "tooltip": "Middle tones. Above 1 lifts the shadows, below 1 deepens them."}),
                "saturation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01, "tooltip": "Colour strength. 1 is unchanged, 0 is black and white."}),
                "hue": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "tooltip": "Turns all colours round the colour wheel, in degrees. Brightness stays."}),
                "warmth": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Above 0 makes the picture warmer (orange), below 0 cooler (blue). Try 0.1."}),
                "tint": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Above 0 adds magenta, below 0 adds green. Fixes a colour cast."}),
                "sharpen": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3.0, "step": 0.05, "tooltip": "Edge sharpening amount. 0 is off, 0.5 is gentle, 1.5 is strong."}),
                "sharpen_radius": ("FLOAT", {"default": 1.5, "min": 0.3, "max": 10.0, "step": 0.1, "tooltip": "Size of the detail to sharpen, in pixels. Small = fine detail."}),
                "vignette": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Darkens the corners. 0 is off, 0.3 is subtle, 1 is black corners."}),
                "vignette_size": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.05, "tooltip": "How far the light reaches. Bigger = the dark edge moves outward."}),
                "grain": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Film grain amount. 0 is off, 0.2 is subtle."}),
                "grain_size": ("INT", {"default": 1, "min": 1, "max": 8, "tooltip": "Grain clump size in pixels. 1 is fine, 3 is coarse."}),
                "grain_seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "tooltip": "Same seed = the same grain pattern. Change it for a different pattern."}),
                "use_tone": ("BOOLEAN", {"default": True, "tooltip": "Switch the tone group (brightness, contrast, gamma) on or off."}),
                "use_colour": ("BOOLEAN", {"default": True, "tooltip": "Switch the colour group (saturation, hue, warmth, tint) on or off."}),
                "use_sharpen": ("BOOLEAN", {"default": True, "tooltip": "Switch the sharpen step on or off."}),
                "use_vignette": ("BOOLEAN", {"default": True, "tooltip": "Switch the vignette on or off."}),
                "use_grain": ("BOOLEAN", {"default": True, "tooltip": "Switch the film grain on or off."}),
                "mix": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": fin.MIX_TIP}),
                "mask": ("MASK", {"tooltip": fin.MASK_TIP}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": fin.ENABLED_TIP}),
            },
        }

    def run(self, image, brightness=0.0, contrast=1.0, gamma=1.0, saturation=1.0, hue=0.0, warmth=0.0, tint=0.0, sharpen=0.0,
            sharpen_radius=1.5, vignette=0.0, vignette_size=1.0, grain=0.0, grain_size=1, grain_seed=0, use_tone=True, use_colour=True,
            use_sharpen=True, use_vignette=True, use_grain=True, mix=1.0, mask=None, enabled=True):
        need_image(image)
        if image.shape[3] < 3:
            raise ValueError("this node needs a colour picture with 3 channels, got %d" % image.shape[3])
        check_settings(brightness, contrast, gamma, saturation, hue, warmth, tint, sharpen, sharpen_radius, vignette, vignette_size, grain, grain_size)
        fin.check_mix(mix)
        groups = active_groups(use_tone, use_colour, use_sharpen, use_vignette, use_grain, brightness, contrast, gamma, saturation, hue,
                               warmth, tint, sharpen, vignette, grain)
        switched = []
        for name, flag in zip(GROUPS, (use_tone, use_colour, use_sharpen, use_vignette, use_grain)):
            if not flag:
                switched.append(name)
        if not enabled or not groups:
            return (image, adjust_info(groups, switched, enabled, mix, mask is not None))
        v = image[..., :3]
        if "tone" in groups or "colour" in groups:
            v = _tone_colour(v, brightness, contrast, gamma, saturation, hue, warmth, tint, "tone" in groups, "colour" in groups)
        if "sharpen" in groups:
            soft = blur_tensor(v, sharpen_radius)
            v = (v + (v - soft) * sharpen).clamp(0.0, 1.0)
        if "vignette" in groups:
            v = _vignette(v, vignette, vignette_size)
        if "grain" in groups:
            v = _grain(v, grain, grain_size, grain_seed)
        out = fin.finish_rgb(image, v, mask, mix, True)
        return (out, adjust_info(groups, switched, True, mix, mask is not None))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageAdjust", SYImageAdjust)
NODE_DISPLAY_NAME_MAPPINGS["SYImageAdjust"] = "Image Adjust SY"
