"""Vignette SY: darkens the corners of a picture with a smooth fade."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, smoothstep
    from ._sy_d3_info import need_nonempty
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, smoothstep
    from _sy_d3_info import need_nonempty


def vignette_factor(x, y, width, height, strength, softness, centre_x=0.5, centre_y=0.5):
    """Pure function. Light multiplier 0..1 for pixel (x, y). 1 at the centre, 1 - strength at the far corner.
    centre_x / centre_y (0..1, 0.5 is the middle) move the bright spot, for example onto a face."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1")
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)
    if not 0.0 < softness <= 1.0:
        raise ValueError("softness must be above 0 and at most 1, got %s" % softness)
    if not 0.0 <= centre_x <= 1.0 or not 0.0 <= centre_y <= 1.0:
        raise ValueError("centre_x and centre_y must be between 0 and 1, got %s and %s" % (centre_x, centre_y))
    nx = ((x + 0.5) / width - centre_x) * 2.0
    ny = ((y + 0.5) / height - centre_y) * 2.0
    d = (nx * nx + ny * ny) ** 0.5 / (2.0 ** 0.5)  # 0 at centre, 1 at corner
    inner = 1.0 - softness
    t = smoothstep((d - inner) / softness)
    return 1.0 - strength * t


def vignette_info(strength, softness, centre_x=0.5, centre_y=0.5):
    """Pure function. Plain sentence: how dark the edges get and where the bright centre sits."""
    vignette_factor(0, 0, 1, 1, strength, softness, centre_x, centre_y)  # plain refusal messages
    if strength == 0:
        return "Strength is 0: the picture is not darkened."
    where = "in the middle" if (centre_x, centre_y) == (0.5, 0.5) else "at %d%% across, %d%% down" % (round(centre_x * 100), round(centre_y * 100))
    text = "Edges darkened by up to %d%% (fade width %.2f), bright centre %s." % (round(strength * 100), softness, where)
    if strength >= 1.0:
        text += " The far corner goes fully black."
    return text


class SYVignette:
    DESCRIPTION = "Darkens the edges and corners of a picture. Strength sets how dark, softness sets how far in the fade reaches. Move the bright centre onto your subject with centre_x and centre_y. The info output says what was done."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to darken at the edges."}),
                "strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How dark the corners get. 0 changes nothing, 1 is black."}),
                "softness": ("FLOAT", {"default": 0.5, "min": 0.05, "max": 1.0, "step": 0.01, "tooltip": "How wide the fade is. Small is a tight dark rim, 1 fades from the centre."}),
            },
            "optional": {
                "centre_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the bright centre sits across the picture. 0 is left, 0.5 the middle, 1 right."}),
                "centre_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the bright centre sits down the picture. 0 is top, 0.5 the middle, 1 bottom."}),
            },
        }

    def run(self, image, strength, softness, centre_x=0.5, centre_y=0.5):
        import torch

        need_image(image)
        need_nonempty(image.shape)
        info = vignette_info(strength, softness, centre_x, centre_y)  # raises the plain message when a value is out of range
        _, h, w, c = image.shape
        ys = ((torch.arange(h, dtype=torch.float32) + 0.5) / h - centre_y) * 2.0
        xs = ((torch.arange(w, dtype=torch.float32) + 0.5) / w - centre_x) * 2.0
        d = torch.sqrt(ys[:, None] ** 2 + xs[None, :] ** 2) / (2.0 ** 0.5)
        t = ((d - (1.0 - softness)) / softness).clamp(0.0, 1.0)
        t = t * t * (3.0 - 2.0 * t)
        factor = (1.0 - strength * t).to(image.device, image.dtype)[None, :, :, None]
        out = image.clone()
        rgb = min(c, 3)
        out[..., :rgb] = image[..., :rgb] * factor
        return (out, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Vignette", SYVignette)
NODE_DISPLAY_NAME_MAPPINGS["SYVignette"] = "Vignette SY"
