"""Seamless Tile Blend SY: makes a texture repeat without visible seams by fading its edges into the opposite side."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

AXES = ("both", "horizontal", "vertical")


def check_settings(blend_width, axis):
    if not 0.05 <= float(blend_width) <= 0.5:
        raise ValueError("blend_width must be between 0.05 and 0.5, got %r" % (blend_width,))
    if axis not in AXES:
        raise ValueError("axis must be one of: %s, got %r" % (", ".join(AXES), axis))


def seam_weight(position, size, blend_width):
    """Pure function. 0 at the picture border, rising to 1 at the inner edge of the fade band, 1 in the middle."""
    if size < 2:
        raise ValueError("the picture must be at least 2 pixels wide and high, got %r" % (size,))
    if not 0.0 < blend_width <= 0.5:
        raise ValueError("blend_width must be above 0 and at most 0.5, got %r" % (blend_width,))
    if not 0 <= position < size:
        raise ValueError("position %r is outside the picture size %r" % (position, size))
    band = max(1e-6, blend_width * size)
    return max(0.0, min(1.0, min(position, size - 1 - position) / band))


def weights_1d(size, blend_width):
    """Pure function. The seam weight of every pixel position along one side."""
    return [seam_weight(p, size, blend_width) for p in range(size)]


def seamless_tensor(image, blend_width, axis):
    """Torch. image [B,H,W,C] float 0..1 -> new tensor of the same shape."""
    import torch

    check_settings(blend_width, axis)
    height, width = image.shape[1], image.shape[2]
    if height < 2 or width < 2:
        raise ValueError("the picture must be at least 2 pixels wide and high")
    img = image.float()
    colour = img[..., :3] if img.shape[3] == 4 else img
    weight = torch.ones(1, height, width, 1, device=img.device)
    shifted = colour
    if axis in ("both", "horizontal"):
        wx = torch.tensor(weights_1d(width, float(blend_width)), device=img.device).view(1, 1, width, 1)
        weight = weight * wx
        shifted = torch.roll(shifted, shifts=width // 2, dims=2)
    if axis in ("both", "vertical"):
        wy = torch.tensor(weights_1d(height, float(blend_width)), device=img.device).view(1, height, 1, 1)
        weight = weight * wy
        shifted = torch.roll(shifted, shifts=height // 2, dims=1)
    out = (weight * colour + (1.0 - weight) * shifted).clamp(0.0, 1.0)
    if img.shape[3] == 4:
        out = torch.cat([out, img[..., 3:4]], dim=3)
    return out.contiguous()


class SYSeamlessTileBlend:
    DESCRIPTION = ("Turns a texture into one that repeats without visible seams. The edges are faded into the opposite "
                   "side of the picture, so the left meets the right and the top meets the bottom.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The texture (or batch of textures) to make seamless."}),
            "blend_width": ("FLOAT", {"default": 0.25, "min": 0.05, "max": 0.5, "step": 0.01, "tooltip": "Share of the picture used for the fade at each edge. Bigger hides seams better."}),
            "axis": (list(AXES), {"default": "both", "tooltip": "Which edges to blend: left and right, top and bottom, or all four."}),
        }}

    def run(self, image, blend_width, axis):
        return (seamless_tensor(image, blend_width, axis),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SeamlessTileBlend", SYSeamlessTileBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYSeamlessTileBlend"] = "Seamless Tile Blend SY"
