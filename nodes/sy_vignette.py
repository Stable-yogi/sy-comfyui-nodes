"""Vignette SY: darkens the corners of a picture with a smooth fade."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, smoothstep
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, smoothstep


def vignette_factor(x, y, width, height, strength, softness):
    """Pure function. Light multiplier 0..1 for pixel (x, y). 1 at the centre, 1 - strength at the far corner."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1")
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)
    if not 0.0 < softness <= 1.0:
        raise ValueError("softness must be above 0 and at most 1, got %s" % softness)
    nx = (x + 0.5) / width * 2.0 - 1.0
    ny = (y + 0.5) / height * 2.0 - 1.0
    d = (nx * nx + ny * ny) ** 0.5 / (2.0 ** 0.5)  # 0 at centre, 1 at corner
    inner = 1.0 - softness
    t = smoothstep((d - inner) / softness)
    return 1.0 - strength * t


class SYVignette:
    DESCRIPTION = "Darkens the edges and corners of a picture. Strength sets how dark, softness sets how far in the fade reaches."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to darken at the edges."}),
                "strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How dark the corners get. 0 changes nothing, 1 is black."}),
                "softness": ("FLOAT", {"default": 0.5, "min": 0.05, "max": 1.0, "step": 0.01, "tooltip": "How wide the fade is. Small is a tight dark rim, 1 fades from the centre."}),
            }
        }

    def run(self, image, strength, softness):
        import torch

        need_image(image)
        if not 0.0 <= strength <= 1.0 or not 0.0 < softness <= 1.0:
            vignette_factor(0, 0, 1, 1, strength, softness)  # raises the plain message
        _, h, w, c = image.shape
        ys = (torch.arange(h, dtype=torch.float32) + 0.5) / h * 2.0 - 1.0
        xs = (torch.arange(w, dtype=torch.float32) + 0.5) / w * 2.0 - 1.0
        d = torch.sqrt(ys[:, None] ** 2 + xs[None, :] ** 2) / (2.0 ** 0.5)
        t = ((d - (1.0 - softness)) / softness).clamp(0.0, 1.0)
        t = t * t * (3.0 - 2.0 * t)
        factor = (1.0 - strength * t).to(image.device, image.dtype)[None, :, :, None]
        out = image.clone()
        rgb = min(c, 3)
        out[..., :rgb] = image[..., :rgb] * factor
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Vignette", SYVignette)
NODE_DISPLAY_NAME_MAPPINGS["SYVignette"] = "Vignette SY"
