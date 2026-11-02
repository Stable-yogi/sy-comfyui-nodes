"""Shadows Highlights SY: open up dark areas and calm very bright areas without a mask."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae


def tone_gain(local_luma, shadows, highlights, width):
    """Pure function. Brightness multiplier for a spot whose surrounding brightness is local_luma (0..1).
    shadows > 0 brightens the dark side, highlights < 0 darkens the bright side. Both 0 gives exactly 1."""
    ae.check_range("local_luma", local_luma, 0.0, 1.0)
    ae.check_range("shadows", shadows, -1.0, 1.0)
    ae.check_range("highlights", highlights, -1.0, 1.0)
    ae.check_range("tonal_width", width, 0.1, 1.0)
    sw = 1.0 - ae.smoothstep(0.0, width, local_luma)
    hw = ae.smoothstep(1.0 - width, 1.0, local_luma)
    gs = 1.0 + (2.0 * shadows if shadows > 0 else shadows) * sw
    gh = 1.0 + (highlights if highlights > 0 else 0.8 * highlights) * hw
    return gs * gh


def shadows_highlights_tensor(image, shadows, highlights, width, radius, colour_keep):
    ae.check_range("shadows", shadows, -1.0, 1.0)
    ae.check_range("highlights", highlights, -1.0, 1.0)
    ae.check_range("tonal_width", width, 0.1, 1.0)
    ae.check_range("radius", radius, 1, 200)
    ae.check_range("colour_keep", colour_keep, 0.0, 1.0)
    x, was3 = ae.prep_image(image)
    if shadows == 0 and highlights == 0:
        return image.clone()
    rgb = x[..., :3]
    luma = ae.luma_of(rgb)
    local = ae.blur_nchw(luma.clamp(0.0, 1.0).permute(0, 3, 1, 2), max(0.5, int(radius) / 2.0)).permute(0, 2, 3, 1).clamp(0.0, 1.0)
    w = float(width)
    t = (local / w).clamp(0.0, 1.0)
    sw = 1.0 - t * t * (3.0 - 2.0 * t)
    t = ((local - (1.0 - w)) / w).clamp(0.0, 1.0)
    hw = t * t * (3.0 - 2.0 * t)
    s, h = float(shadows), float(highlights)
    gain = (1.0 + (2.0 * s if s > 0 else s) * sw) * (1.0 + (h if h > 0 else 0.8 * h) * hw)
    scaled = rgb * gain
    grey = luma * gain
    # the further the gain is from 1, the more colour is traded for plain brightness when colour_keep < 1
    eff = 1.0 - (1.0 - float(colour_keep)) * (gain - 1.0).abs().clamp(0.0, 1.0)
    out = x.clone()
    out[..., :3] = grey + (scaled - grey) * eff
    return ae.finish_image(out, image, was3)


class SYShadowsHighlights:
    DESCRIPTION = ("Opens up dark areas and calms very bright areas without a mask. "
                   "It looks at how bright each neighbourhood is, so edges stay free of bright rims. Shadows 0 and highlights 0 do nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to rebalance."}),
            "shadows": ("FLOAT", {"default": 0.3, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Above 0 brightens the dark areas, below 0 darkens them."}),
            "highlights": ("FLOAT", {"default": -0.2, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "Below 0 darkens the very bright areas, above 0 brightens them."}),
            "tonal_width": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.01, "tooltip": "How far into the mid-tones each of the two effects reaches."}),
            "radius": ("INT", {"default": 30, "min": 1, "max": 200, "tooltip": "Softness of the brightness map in pixels. Bigger avoids bright rims on edges."}),
            "colour_keep": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much of the original colour stays while brightness changes."}),
        }}

    def run(self, image, shadows, highlights, tonal_width, radius, colour_keep):
        return (shadows_highlights_tensor(image, float(shadows), float(highlights), float(tonal_width), int(radius), float(colour_keep)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ShadowsHighlights", SYShadowsHighlights)
NODE_DISPLAY_NAME_MAPPINGS["SYShadowsHighlights"] = "Shadows Highlights SY"
