"""Clarity SY: local contrast that crisps up mid-tone detail without glow halos."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae


def midtone_weight(luma):
    """Pure function. 1 in mid grey, falling to 0 in pure black and pure white."""
    ae.check_range("luma", luma, 0.0, 1.0)
    return 4.0 * luma * (1.0 - luma)


def clarity_tensor(image, radius, amount):
    ae.check_range("radius", radius, 2, 100)
    ae.check_range("amount", amount, -1.0, 2.0)
    x, was3 = ae.prep_image(image)
    if amount == 0:
        return image.clone()
    rgb = x[..., :3]
    luma = ae.luma_of(rgb)
    blur = ae.blur_nchw(luma.permute(0, 3, 1, 2), max(0.5, int(radius) / 2.0)).permute(0, 2, 3, 1)
    weight = 4.0 * luma.clamp(0.0, 1.0) * (1.0 - luma.clamp(0.0, 1.0))
    out = x.clone()
    out[..., :3] = rgb + (luma - blur) * (weight * float(amount))
    return ae.finish_image(out, image, was3)


class SYClarity:
    DESCRIPTION = ("Adds local contrast so mid-tone detail looks crisper, without the bright glow lines a plain sharpen makes. "
                   "Negative amounts soften the detail. 0 does nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to add crispness to."}),
            "radius": ("INT", {"default": 20, "min": 2, "max": 100, "tooltip": "How big the detail is, in pixels. Bigger works on broader shapes."}),
            "amount": ("FLOAT", {"default": 0.5, "min": -1.0, "max": 2.0, "step": 0.01, "tooltip": "How strong the effect is. Below 0 softens. 0 does nothing."}),
        }}

    def run(self, image, radius, amount):
        return (clarity_tensor(image, int(radius), float(amount)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Clarity", SYClarity)
NODE_DISPLAY_NAME_MAPPINGS["SYClarity"] = "Clarity SY"
