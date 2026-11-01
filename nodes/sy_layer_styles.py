"""Drop Shadow SY, Outer Glow SY, Stroke SY: add a shadow, a glow or an outline around the shape of a picture (its mask or its transparent background)."""
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

# colour names -> red, green, blue as 0..1 numbers (no hex codes in node files)
COLOURS = {
    "black": (0.0, 0.0, 0.0),
    "white": (1.0, 1.0, 1.0),
    "gold": (0.83, 0.65, 0.22),
    "red": (0.90, 0.12, 0.12),
    "blue": (0.12, 0.32, 0.90),
    "green": (0.12, 0.70, 0.25),
    "grey": (0.5, 0.5, 0.5),
}
COLOUR_CHOICES = list(COLOURS) + ["custom"]
POSITIONS = ("outside", "inside", "centre")
NEED_SHAPE = "Give a mask, or a picture with a transparent background."


# ---------------------------------------------------------------- pure helpers

def gaussian_kernel(sigma, radius):
    """Pure function. 2*radius+1 weights of a Gaussian bell that add up to 1. sigma 0 or radius 0 gives [1.0]."""
    radius = int(radius)
    if radius < 0:
        raise ValueError("the blur radius cannot be negative, got %d" % radius)
    sigma = float(sigma)
    if radius == 0 or sigma <= 0.0:
        return [1.0]
    w = [math.exp(-(i * i) / (2.0 * sigma * sigma)) for i in range(-radius, radius + 1)]
    s = sum(w)
    return [v / s for v in w]


def blur_sigma(blur):
    """Pure function. The Gaussian sigma for a blur setting in pixels, and the kernel radius."""
    sigma = max(0.0, float(blur)) / 2.0
    return sigma, (int(math.ceil(3.0 * sigma)) if sigma > 0 else 0)


def over_alpha(top, bottom):
    """Pure function. Put the pixel `top` over the pixel `bottom`. Both are (r, g, b, a) with 0..1 numbers and normal (not premultiplied) colour.
    The sum is done in premultiplied space; the result is normal colour again."""
    tr, tg, tb, ta = top
    br, bg, bb, ba = bottom
    a = ta + ba * (1.0 - ta)
    if a <= 1e-9:
        return (0.0, 0.0, 0.0, 0.0)
    out = []
    for t, b in ((tr, br), (tg, bg), (tb, bb)):
        out.append((t * ta + b * ba * (1.0 - ta)) / a)
    return (out[0], out[1], out[2], a)


def colour_for(name, r=0, g=0, b=0):
    """Pure function. Red, green, blue (0..1) for a colour name. 'custom' uses r, g, b given as 0..255."""
    if name == "custom":
        for label, v in (("custom_r", r), ("custom_g", g), ("custom_b", b)):
            if not 0 <= int(v) <= 255:
                raise ValueError("%s must be between 0 and 255, got %s" % (label, v))
        return (int(r) / 255.0, int(g) / 255.0, int(b) / 255.0)
    if name not in COLOURS:
        raise ValueError("colour must be one of: %s, got %r" % (", ".join(COLOUR_CHOICES), name))
    return COLOURS[name]


def disc_rows(radius):
    """Pure function. For a round (disc) grow of `radius` pixels: a list of (row offset, half width) pairs."""
    r = int(radius)
    return [(dy, int(math.floor(math.sqrt(r * r - dy * dy) + 1e-9))) for dy in range(-r, r + 1)]


def check_int(name, v, lo, hi):
    if isinstance(v, bool) or int(v) != v or not lo <= int(v) <= hi:
        raise ValueError("%s must be a whole number between %d and %d, got %s" % (name, lo, hi, v))
    return int(v)


def check_float(name, v, lo, hi):
    if not lo <= float(v) <= hi:
        raise ValueError("%s must be between %s and %s, got %s" % (name, lo, hi, v))
    return float(v)


# ---------------------------------------------------------------- torch part

def _shift(m, dx, dy):
    """[B,1,H,W] mask moved by dx (right) and dy (down), empty where nothing comes in."""
    import torch
    if dx == 0 and dy == 0:
        return m
    h, w = m.shape[-2:]
    out = torch.zeros_like(m)
    if abs(dx) >= w or abs(dy) >= h:
        return out
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[..., yd, xd] = m[..., ys, xs]
    return out


def dilate(m, radius):
    """[B,1,H,W] mask grown by `radius` pixels with a round brush (max over a disc)."""
    import torch.nn.functional as F
    r = int(radius)
    if r <= 0:
        return m
    cache = {}
    out = None
    for dy, ext in disc_rows(r):
        if ext not in cache:
            cache[ext] = m if ext == 0 else F.max_pool2d(m, (1, 2 * ext + 1), stride=1, padding=(0, ext))
        row = _shift(cache[ext], 0, dy)
        out = row if out is None else out.maximum(row)
    return out


def erode(m, radius):
    """[B,1,H,W] mask shrunk by `radius` pixels. The picture border does not eat into the shape."""
    return 1.0 - dilate(1.0 - m, radius)


def spread_mask(m, amount):
    """Positive amount grows the shape, negative shrinks it."""
    return dilate(m, amount) if amount > 0 else (erode(m, -amount) if amount < 0 else m)


def blur_mask(m, blur):
    """[B,1,H,W] mask softened with a separable Gaussian (two 1-D passes)."""
    import torch
    import torch.nn.functional as F
    sigma, radius = blur_sigma(blur)
    if radius == 0:
        return m
    k = torch.tensor(gaussian_kernel(sigma, radius), dtype=m.dtype, device=m.device)
    kh = k.view(1, 1, 1, -1)
    kv = k.view(1, 1, -1, 1)
    x = F.pad(m, (radius, radius, 0, 0))
    x = F.conv2d(x, kh)
    x = F.pad(x, (0, 0, radius, radius))
    x = F.conv2d(x, kv)
    return x.clamp(0.0, 1.0)


def split_shape(image, mask):
    """Returns (rgb [B,H,W,3], original alpha [B,H,W], shape [B,1,H,W]). Plain refusals for a missing shape or a wrong mask."""
    need_image(image)
    b, h, w, c = image.shape
    if b < 1 or h < 1 or w < 1:
        raise ValueError("the picture is empty (no pictures or no pixels)")
    if c not in (3, 4):
        raise ValueError("the picture needs 3 (RGB) or 4 (RGBA) colour channels, got %d" % c)
    if mask is None and c != 4:
        raise ValueError(NEED_SHAPE)
    rgb = image[..., :3]
    alpha = image[..., 3] if c == 4 else None
    if mask is not None:
        if getattr(mask, "ndim", 0) == 2:
            mask = mask.unsqueeze(0)
        if getattr(mask, "ndim", 0) != 3:
            raise ValueError("the mask must be a mask batch shaped [batch, height, width]")
        mb, mh, mw = mask.shape
        if (mh, mw) != (h, w):
            raise ValueError("the mask is %dx%d but the picture is %dx%d. Give a mask of the same size" % (mw, mh, w, h))
        if mb not in (1, b):
            raise ValueError("the mask batch has %d masks but there are %d pictures. Use one mask or the same number" % (mb, b))
        m = mask.to(device=image.device, dtype=image.dtype).clamp(0.0, 1.0).expand(b, h, w)
        orig_a = m if alpha is None else alpha * m
        shape = m
    else:
        orig_a = alpha
        shape = alpha.clamp(0.0, 1.0)
    return rgb, orig_a, shape.unsqueeze(1)


def compose(rgb, orig_a, layer_a, colour, over):
    """Put the coloured effect layer under (over=False) or over (over=True) the original, in premultiplied space.
    rgb [B,H,W,3], orig_a [B,H,W], layer_a [B,H,W]. Returns [B,H,W,4] with normal (not premultiplied) colour."""
    import torch
    col = torch.tensor(colour, dtype=rgb.dtype, device=rgb.device).view(1, 1, 1, 3)
    p_orig = rgb * orig_a.unsqueeze(-1)
    p_layer = col * layer_a.unsqueeze(-1)
    if over:
        p_top, a_top, p_bot, a_bot = p_layer, layer_a, p_orig, orig_a
    else:
        p_top, a_top, p_bot, a_bot = p_orig, orig_a, p_layer, layer_a
    a = a_top + a_bot * (1.0 - a_top)
    p = p_top + p_bot * (1.0 - a_top.unsqueeze(-1))
    out_rgb = torch.where(a.unsqueeze(-1) > 1e-6, p / a.clamp_min(1e-6).unsqueeze(-1), rgb)
    return torch.cat([out_rgb.clamp(0.0, 1.0), a.clamp(0.0, 1.0).unsqueeze(-1)], dim=-1)


def drop_shadow_layer(shape, offset_x, offset_y, blur, spread, opacity):
    m = spread_mask(shape, spread)
    m = blur_mask(m, blur)
    return (_shift(m, offset_x, offset_y) * opacity).clamp(0.0, 1.0)


def glow_layer(shape, size, spread, opacity):
    r = int(round(size * spread))
    m = dilate(shape, r)
    m = blur_mask(m, max(size - r, 0))
    return (m * opacity).clamp(0.0, 1.0)


def stroke_layer(shape, width, position, opacity):
    if position == "outside":
        band = dilate(shape, width) - shape
    elif position == "inside":
        band = shape - erode(shape, width)
    else:
        band = dilate(shape, (width + 1) // 2) - erode(shape, width // 2)
    return (band.clamp(0.0, 1.0) * opacity).clamp(0.0, 1.0)


# ---------------------------------------------------------------- nodes

_COLOUR_TIP = "Colour of the effect. Choose 'custom' to use the three numbers below."


def _colour_inputs(default):
    return {"color": (COLOUR_CHOICES, {"default": default, "tooltip": _COLOUR_TIP})}


def _optional_inputs():
    return {
        "mask": ("MASK", {"tooltip": "The shape. Empty: the transparent background of the picture is used."}),
        "custom_r": ("INT", {"default": 0, "min": 0, "max": 255, "tooltip": "Red part of the custom colour, 0 to 255."}),
        "custom_g": ("INT", {"default": 0, "min": 0, "max": 255, "tooltip": "Green part of the custom colour, 0 to 255."}),
        "custom_b": ("INT", {"default": 0, "min": 0, "max": 255, "tooltip": "Blue part of the custom colour, 0 to 255."}),
    }


_SHAPE_NOTE = (" The shape is the mask, or the transparent background of the picture if no mask is given. With a mask, "
               "everything outside the mask becomes transparent. The result is a picture with transparency, plus the effect as a mask.")


class _LayerBase:
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "effect_mask")


class SYDropShadow(_LayerBase):
    DESCRIPTION = "Adds a soft shadow behind the shape, moved by offset_x and offset_y." + _SHAPE_NOTE

    @classmethod
    def INPUT_TYPES(cls):
        req = {
            "image": ("IMAGE", {"tooltip": "The picture (RGB or with transparency)."}),
            "offset_x": ("INT", {"default": 12, "min": -512, "max": 512, "tooltip": "Move the shadow right (plus) or left (minus), in pixels."}),
            "offset_y": ("INT", {"default": 12, "min": -512, "max": 512, "tooltip": "Move the shadow down (plus) or up (minus), in pixels."}),
            "blur": ("INT", {"default": 16, "min": 0, "max": 256, "tooltip": "How soft the shadow edge is, in pixels. 0 is hard."}),
            "spread": ("INT", {"default": 0, "min": -64, "max": 64, "tooltip": "Make the shadow bigger (plus) or smaller (minus) before it is blurred."}),
            "opacity": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the shadow is. 0 is invisible."}),
        }
        req.update(_colour_inputs("black"))
        return {"required": req, "optional": _optional_inputs()}

    def run(self, image, offset_x, offset_y, blur, spread, opacity, color, mask=None, custom_r=0, custom_g=0, custom_b=0):
        check_int("offset_x", offset_x, -512, 512)
        check_int("offset_y", offset_y, -512, 512)
        check_int("blur", blur, 0, 256)
        check_int("spread", spread, -64, 64)
        opacity = check_float("opacity", opacity, 0.0, 1.0)
        colour = colour_for(color, custom_r, custom_g, custom_b)
        rgb, orig_a, shape = split_shape(image, mask)
        layer = drop_shadow_layer(shape, int(offset_x), int(offset_y), blur, int(spread), opacity)
        out = compose(rgb, orig_a, layer[:, 0], colour, over=False)
        return (out, layer[:, 0].contiguous())


class SYOuterGlow(_LayerBase):
    DESCRIPTION = "Adds a soft glow around the outside of the shape." + _SHAPE_NOTE

    @classmethod
    def INPUT_TYPES(cls):
        req = {
            "image": ("IMAGE", {"tooltip": "The picture (RGB or with transparency)."}),
            "size": ("INT", {"default": 24, "min": 1, "max": 256, "tooltip": "How far the glow reaches, in pixels."}),
            "spread": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much of the glow is solid near the shape. 0 is all soft."}),
            "opacity": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the glow is. 0 is invisible."}),
        }
        req.update(_colour_inputs("gold"))
        return {"required": req, "optional": _optional_inputs()}

    def run(self, image, size, spread, opacity, color, mask=None, custom_r=0, custom_g=0, custom_b=0):
        check_int("size", size, 1, 256)
        spread = check_float("spread", spread, 0.0, 1.0)
        opacity = check_float("opacity", opacity, 0.0, 1.0)
        colour = colour_for(color, custom_r, custom_g, custom_b)
        rgb, orig_a, shape = split_shape(image, mask)
        layer = glow_layer(shape, int(size), spread, opacity)
        out = compose(rgb, orig_a, layer[:, 0], colour, over=False)
        return (out, layer[:, 0].contiguous())


class SYStroke(_LayerBase):
    DESCRIPTION = "Draws an outline along the edge of the shape: outside it, inside it, or centred on the edge." + _SHAPE_NOTE

    @classmethod
    def INPUT_TYPES(cls):
        req = {
            "image": ("IMAGE", {"tooltip": "The picture (RGB or with transparency)."}),
            "width": ("INT", {"default": 6, "min": 1, "max": 128, "tooltip": "Thickness of the outline, in pixels."}),
            "position": (list(POSITIONS), {"default": "outside", "tooltip": "Where the outline sits: outside the shape, inside it, or centred on the edge."}),
            "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the outline is. 0 is invisible."}),
        }
        req.update(_colour_inputs("white"))
        return {"required": req, "optional": _optional_inputs()}

    def run(self, image, width, position, opacity, color, mask=None, custom_r=0, custom_g=0, custom_b=0):
        check_int("width", width, 1, 128)
        if position not in POSITIONS:
            raise ValueError("position must be one of: %s, got %r" % (", ".join(POSITIONS), position))
        opacity = check_float("opacity", opacity, 0.0, 1.0)
        colour = colour_for(color, custom_r, custom_g, custom_b)
        rgb, orig_a, shape = split_shape(image, mask)
        layer = stroke_layer(shape, int(width), position, opacity)
        out = compose(rgb, orig_a, layer[:, 0], colour, over=(position != "outside"))
        return (out, layer[:, 0].contiguous())


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DropShadow", SYDropShadow)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "OuterGlow", SYOuterGlow)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Stroke", SYStroke)
NODE_DISPLAY_NAME_MAPPINGS["SYDropShadow"] = "Drop Shadow SY"
NODE_DISPLAY_NAME_MAPPINGS["SYOuterGlow"] = "Outer Glow SY"
