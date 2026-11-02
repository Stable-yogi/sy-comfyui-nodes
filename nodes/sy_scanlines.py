"""Scanlines SY: old monitor look. Every Nth row is darkened, with an optional soft wave."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_args(line_gap, darkness, wobble, offset):
    if line_gap < 2:
        raise ValueError("line_gap must be at least 2, got %s" % line_gap)
    if not 0.0 <= darkness <= 1.0:
        raise ValueError("darkness must be between 0 and 1, got %s" % darkness)
    if wobble < 0:
        raise ValueError("wobble must be 0 or more, got %s" % wobble)
    if offset < 0:
        raise ValueError("offset must be 0 or more, got %s" % offset)


def line_factor(row, line_gap, darkness, offset=0):
    """Pure function. Brightness multiplier for a row: 1 - darkness at the middle of a dark line, 1 between lines (smooth sine profile)."""
    check_args(line_gap, darkness, 0.0, offset)
    phase = ((row - offset) % line_gap) / float(line_gap)
    dip = 0.5 + 0.5 * math.cos(2.0 * math.pi * phase)   # 1 on the line, 0 halfway between lines
    return 1.0 - darkness * dip


class SYScanlines:
    DESCRIPTION = "Gives a picture an old monitor look by darkening every few rows with a smooth profile. An optional wave makes the lines slightly curved."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch to add scanlines to."}),
                "line_gap": ("INT", {"default": 3, "min": 2, "max": 16, "step": 1, "tooltip": "Distance in pixels from one dark line to the next."}),
                "darkness": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How dark the lines get. 0 leaves the picture unchanged."}),
                "wobble": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 4.0, "step": 0.1, "tooltip": "Waviness of the lines in pixels. 0 keeps them straight."}),
                "offset": ("INT", {"default": 0, "min": 0, "max": 15, "step": 1, "tooltip": "Moves the lines down by this many pixels."}),
            }
        }

    def run(self, image, line_gap, darkness, wobble, offset):
        import torch

        check_args(line_gap, darkness, wobble, offset)
        h, w = image.shape[1], image.shape[2]
        rows = torch.arange(h, dtype=torch.float32)[:, None]
        if wobble > 0:
            cols = torch.arange(w, dtype=torch.float32)[None, :]
            rows = rows + wobble * torch.sin(cols * (2.0 * math.pi / 96.0))
        else:
            rows = rows.expand(h, w)
        phase = torch.remainder(rows - offset, float(line_gap)) / float(line_gap)
        dip = 0.5 + 0.5 * torch.cos(2.0 * math.pi * phase)
        factor = (1.0 - darkness * dip).to(image.dtype).to(image.device)[None, :, :, None]
        out = image.clone()
        ch = min(3, image.shape[3])
        out[..., :ch] = image[..., :ch] * factor
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Scanlines", SYScanlines)
