"""Hue Shift SY: turns all colours around the colour wheel."""
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

YIQ = [[0.299, 0.587, 0.114], [0.596, -0.274, -0.322], [0.211, -0.523, 0.312]]


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mat_inv(m):
    """Pure function. Inverse of a 3x3 matrix (list of rows)."""
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        raise ValueError("matrix cannot be inverted")
    return [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]


def check_settings(degrees, strength):
    if not -180.0 <= degrees <= 180.0:
        raise ValueError("degrees must be between -180 and 180, got %s" % degrees)
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)


def hue_matrix(degrees):
    """Pure function. 3x3 matrix (list of rows) that turns RGB around the grey axis by `degrees` (via YIQ)."""
    a = math.radians(degrees)
    ca, sa = math.cos(a), math.sin(a)
    rot = [[1.0, 0.0, 0.0], [0.0, ca, -sa], [0.0, sa, ca]]
    return mat_mul(mat_inv(YIQ), mat_mul(rot, YIQ))


def shift_pixel(rgb, degrees, strength):
    """Pure function. One (r, g, b) in 0..1 shifted and blended with the original."""
    check_settings(degrees, strength)
    m = hue_matrix(degrees)
    out = []
    for i in range(3):
        v = m[i][0] * rgb[0] + m[i][1] * rgb[1] + m[i][2] * rgb[2]
        v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
        out.append(rgb[i] + (v - rgb[i]) * strength)
    return tuple(out)


class SYHueShift:
    DESCRIPTION = "Rotates all colours around the colour wheel. Greys stay grey."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to recolour."}),
                "degrees": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0, "tooltip": "How far to turn the colours. 180 swaps each colour for roughly its opposite."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much of the shifted colour to use. 0 keeps the original."}),
            }
        }

    def run(self, image, degrees, strength):
        import torch

        need_image(image)
        check_settings(degrees, strength)
        out = image.clone()
        rgb = image[..., :3].to(torch.float32)
        m = torch.tensor(hue_matrix(degrees), dtype=torch.float32, device=image.device)
        shifted = torch.einsum("ij,bhwj->bhwi", m, rgb).clamp(0.0, 1.0)
        out[..., :3] = (rgb + (shifted - rgb) * float(strength)).to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HueShift", SYHueShift)
NODE_DISPLAY_NAME_MAPPINGS["SYHueShift"] = "Hue Shift SY"
