"""Ripple Warp SY: water-ripple / wave warp."""
import math

try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

EDGES = ("stretch", "black", "mirror")
_PAD_MODE = {"stretch": "border", "black": "zeros", "mirror": "reflection"}


def ripple_offset(coord, wavelength, phase_deg, strength):
    """Pure function. How far (in pixels) to move a pixel that sits at `coord` pixels along the wave."""
    if wavelength <= 0:
        raise ValueError("wavelength must be above 0 pixels, got %s" % wavelength)
    return strength * math.sin(2.0 * math.pi * coord / wavelength + math.radians(phase_deg))


def ripple_tensor(image, strength_x, strength_y, wavelength, phase, edge):
    import torch
    import torch.nn.functional as F

    ae.check_range("strength_x", strength_x, 0.0, 100.0)
    ae.check_range("strength_y", strength_y, 0.0, 100.0)
    ae.check_range("wavelength", wavelength, 4.0, 2000.0)
    ae.check_range("phase", phase, 0.0, 360.0)
    if edge not in EDGES:
        raise ValueError("edge must be one of %s, got %r" % (", ".join(EDGES), edge))
    x, was3 = ae.prep_image(image, need_colour=False)
    if strength_x == 0 and strength_y == 0:
        return image.clone()
    b, h, w, c = x.shape
    py = torch.arange(h, dtype=torch.float32, device=x.device) + 0.5   # pixel centres
    px = torch.arange(w, dtype=torch.float32, device=x.device) + 0.5
    gy, gx = torch.meshgrid(py, px, indexing="ij")
    ph = math.radians(phase)
    two_pi = 2.0 * math.pi
    # sideways push depends on the row, up/down push depends on the column
    src_x = gx + strength_x * torch.sin(two_pi * gy / wavelength + ph)
    src_y = gy + strength_y * torch.sin(two_pi * gx / wavelength + ph)
    grid = torch.stack((src_x / w * 2.0 - 1.0, src_y / h * 2.0 - 1.0), dim=-1).unsqueeze(0).expand(b, -1, -1, -1)
    out = F.grid_sample(x.permute(0, 3, 1, 2), grid, mode="bilinear",
                        padding_mode=_PAD_MODE[edge], align_corners=False)
    return ae.finish_image(out.permute(0, 2, 3, 1), image, was3)


class SYRippleWarp:
    DESCRIPTION = ("Warps the picture in waves, like looking through rippling water. Set how far the picture is pushed "
                   "sideways and up and down, and how long each wave is. Strength 0 does nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to ripple."}),
            "strength_x": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.5, "tooltip": "How far the picture is pushed sideways, in pixels."}),
            "strength_y": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.5, "tooltip": "How far the picture is pushed up and down, in pixels."}),
            "wavelength": ("FLOAT", {"default": 120.0, "min": 4.0, "max": 2000.0, "step": 1.0, "tooltip": "Distance between two wave crests, in pixels."}),
            "phase": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0, "tooltip": "Slides the waves along. Change it a little each frame to animate."}),
            "edge": (list(EDGES), {"default": "stretch", "tooltip": "What fills the border where the waves pull in space: stretch the edge, black, or mirror."}),
        }}

    def run(self, image, strength_x, strength_y, wavelength, phase, edge):
        return (ripple_tensor(image, float(strength_x), float(strength_y), float(wavelength), float(phase), edge),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RippleWarp", SYRippleWarp)
NODE_DISPLAY_NAME_MAPPINGS["SYRippleWarp"] = "Ripple Warp SY"
