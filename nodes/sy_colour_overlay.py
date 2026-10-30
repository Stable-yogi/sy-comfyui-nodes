"""Colour Overlay SY: lays one flat colour over a picture, with a blend mode and an optional mask."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex
    from _sy_image_ops import need_image

MODES = ("normal", "multiply", "screen", "overlay")
DEFAULT_COLOUR = "#" + "d4a537"


def check_mode(mode):
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))


def check_opacity(opacity):
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("opacity must be between 0 and 1, got %s" % opacity)


def overlay_value(v, c, mode):
    """Pure function. Blended value of picture value v and colour value c (both 0..1), before opacity."""
    check_mode(mode)
    if mode == "normal":
        return c
    if mode == "multiply":
        return v * c
    if mode == "screen":
        return 1.0 - (1.0 - v) * (1.0 - c)
    if v < 0.5:
        return 2.0 * v * c
    return 1.0 - 2.0 * (1.0 - v) * (1.0 - c)


def overlay_pixel(rgb, colour, opacity, mode, mask=1.0):
    """Pure function. One pixel. mask 1 applies the overlay, 0 keeps the pixel."""
    check_opacity(opacity)
    w = opacity * mask
    return tuple(rgb[i] + (overlay_value(rgb[i], colour[i], mode) - rgb[i]) * w for i in range(3))


def check_mask_shape(mask_shape, image_shape):
    """mask_shape (B,H,W) or (H,W); image_shape (B,H,W,C). Raises when the size does not fit."""
    mask_shape = tuple(mask_shape)
    if len(mask_shape) == 2:
        mask_shape = (1,) + mask_shape
    if len(mask_shape) != 3:
        raise ValueError("mask must be shaped [batch, height, width], got %s" % (mask_shape,))
    if tuple(mask_shape[1:]) != tuple(image_shape[1:3]):
        raise ValueError("mask size %sx%s differs from the image size %sx%s; resize the mask first"
                         % (mask_shape[2], mask_shape[1], image_shape[2], image_shape[1]))
    if mask_shape[0] not in (1, image_shape[0]):
        raise ValueError("mask batch %s does not match image batch %s (use 1 or the same count)" % (mask_shape[0], image_shape[0]))


class SYColourOverlay:
    DESCRIPTION = "Lays a flat colour over a picture using a blend mode and opacity. An optional mask limits where it shows."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to colour."}),
                "colour": ("STRING", {"default": DEFAULT_COLOUR, "multiline": False, "tooltip": "The overlay colour, 3 or 6 hex digits like a web colour."}),
                "opacity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 leaves the picture alone, 1 applies the full blend."}),
                "mode": (list(MODES), {"default": "normal", "tooltip": "normal paints the colour; multiply darkens; screen lightens; overlay boosts contrast."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "White applies the colour, black keeps the picture. Must be the same size as the image."}),
            },
        }

    def run(self, image, colour, opacity, mode, mask=None):
        import torch

        need_image(image)
        check_mode(mode)
        check_opacity(opacity)
        c = parse_hex(colour, "colour")
        w = float(opacity)
        if mask is not None:
            check_mask_shape(tuple(mask.shape), tuple(image.shape))
            m = mask if mask.ndim == 3 else mask.unsqueeze(0)
            w = (m.to(torch.float32) * w).unsqueeze(-1).to(image.device)
        rgb = image[..., :3].to(torch.float32)
        cv = torch.tensor(c, dtype=torch.float32, device=image.device)
        if mode == "normal":
            blended = cv.expand_as(rgb)
        elif mode == "multiply":
            blended = rgb * cv
        elif mode == "screen":
            blended = 1.0 - (1.0 - rgb) * (1.0 - cv)
        else:
            blended = torch.where(rgb < 0.5, 2.0 * rgb * cv, 1.0 - 2.0 * (1.0 - rgb) * (1.0 - cv))
        res = (rgb + (blended - rgb) * w).clamp(0.0, 1.0)
        out = image.clone()
        out[..., :3] = res.to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourOverlay", SYColourOverlay)
NODE_DISPLAY_NAME_MAPPINGS["SYColourOverlay"] = "Colour Overlay SY"
