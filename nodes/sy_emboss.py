"""Emboss SY: turns a picture into a grey relief that looks pressed into metal or paper."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import clamp01, need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import clamp01, need_image

ANGLES = ("top_left", "top", "top_right", "left", "right", "bottom_left", "bottom", "bottom_right")
# The eight outer cells of the 3x3 kernel, clockwise from the top left corner.
_RING_CELLS = ((0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0))
_RING_VALUES = (-2, -1, 0, 1, 2, 1, 0, -1)
# Where the dark side of the ring starts for each direction (clockwise steps from top_left).
_ANGLE_STEPS = {
    "top_left": 0, "top": 1, "top_right": 2, "right": 3,
    "bottom_right": 4, "bottom": 5, "bottom_left": 6, "left": 7,
}


def check_angle(angle):
    if angle not in ANGLES:
        raise ValueError("angle must be one of: %s, got %r" % (", ".join(ANGLES), angle))


def check_strength(strength):
    if not 0.0 <= strength <= 10.0:
        raise ValueError("strength must be between 0 and 10, got %s" % strength)


def emboss_kernel(angle):
    """Pure function. Returns the 3x3 kernel (nested lists) for one direction. It always sums to 1."""
    check_angle(angle)
    step = _ANGLE_STEPS[angle]
    k = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    for i, (row, col) in enumerate(_RING_CELLS):
        k[row][col] = _RING_VALUES[(i - step) % 8]
    return k


def emboss_plane(plane, strength, angle):
    """Pure function. plane is a list of rows of luma values 0..1. Replicate padding at the edges."""
    check_strength(strength)
    k = emboss_kernel(angle)
    h = len(plane)
    if h < 1 or len(plane[0]) < 1:
        raise ValueError("picture size must be at least 1x1")
    w = len(plane[0])
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            conv = 0.0
            for dy in range(3):
                yy = min(h - 1, max(0, y + dy - 1))
                for dx in range(3):
                    xx = min(w - 1, max(0, x + dx - 1))
                    conv += k[dy][dx] * plane[yy][xx]
            row.append(clamp01(0.5 + strength * (conv - plane[y][x])))
        out.append(row)
    return out


class SYEmboss:
    DESCRIPTION = "Turns a picture into a grey relief, as if pressed into metal. The angle sets where the light comes from."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1, "tooltip": "How deep the relief looks. 0 gives flat grey."}),
                "angle": (list(ANGLES), {"default": "top_left", "tooltip": "The side the light comes from."}),
            }
        }

    def run(self, image, strength, angle):
        import torch
        import torch.nn.functional as F

        need_image(image)
        check_strength(strength)
        k = torch.tensor(emboss_kernel(angle), dtype=torch.float32, device=image.device).view(1, 1, 3, 3)
        rgb = image[..., :3].to(torch.float32)
        luma = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).unsqueeze(1)
        padded = F.pad(luma, (1, 1, 1, 1), mode="replicate")
        conv = F.conv2d(padded, k)
        res = (0.5 + float(strength) * (conv - luma)).clamp(0.0, 1.0).squeeze(1).unsqueeze(-1)
        out = image.clone()
        out[..., :3] = res.expand(-1, -1, -1, 3).to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Emboss", SYEmboss)
