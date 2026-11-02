"""Zoom Punch SY: a quick pulse zoom on chosen frames (for beats and hits)."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_frames(text, count):
    """Pure function. '12, 30, 48' -> [12, 30, 48]. Empty text -> []. Frame numbers count from 0."""
    count = int(count)
    out = []
    for tok in re.split(r"[,;\s]+", (text or "").strip()):
        if tok == "":
            continue
        if not re.fullmatch(r"[+-]?\d+", tok):
            raise ValueError("frames must be whole numbers separated by commas, but %r is not a number" % tok)
        k = int(tok)
        if k < 0:
            raise ValueError("frame numbers cannot be negative, got %d" % k)
        if k >= count:
            raise ValueError("frame %d does not exist: the clip has %d frames (numbered 0 to %d)" % (k, count, count - 1))
        if k not in out:
            out.append(k)
    return sorted(out)


def pulse(t, length):
    """Pure function. 1 on the hit frame (t=0), easing out to 0 after `length` frames. 0 before the hit."""
    length = int(length)
    if length < 1:
        raise ValueError("length must be at least 1 frame, got %d" % length)
    if t < 0 or t >= length:
        return 0.0
    r = 1.0 - t / float(length)
    return r * r


def zoom_factors(count, hits, strength, length):
    """Pure function. One zoom factor per frame (1.0 = no zoom). Overlapping pulses take the biggest."""
    if not 0.0 <= float(strength) <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)
    out = []
    for i in range(int(count)):
        best = 0.0
        for h in hits:
            best = max(best, pulse(i - h, length))
        out.append(1.0 + float(strength) * best)
    return out


def punch(images, frames, strength, length, centre_x, centre_y):
    """Torch function. images [N,H,W,C] -> new images, same size."""
    import torch
    import torch.nn.functional as F
    n, h, w, c = images.shape
    hits = parse_frames(frames, n)
    factors = zoom_factors(n, hits, strength, length)
    out = images.clone()
    cx = 2.0 * float(centre_x) - 1.0
    cy = 2.0 * float(centre_y) - 1.0
    ys = (torch.arange(h, dtype=torch.float32) + 0.5) / h * 2.0 - 1.0
    xs = (torch.arange(w, dtype=torch.float32) + 0.5) / w * 2.0 - 1.0
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    for i, z in enumerate(factors):
        if z <= 1.0 + 1e-6:
            continue
        grid = torch.stack([cx + (gx - cx) / z, cy + (gy - cy) / z], dim=-1).unsqueeze(0)
        src = images[i:i + 1].float().permute(0, 3, 1, 2)
        res = F.grid_sample(src, grid.to(src.dtype), mode="bilinear", padding_mode="border", align_corners=False)
        out[i] = res.permute(0, 2, 3, 1)[0].clamp(0.0, 1.0).to(images.dtype)
    return out


class SYZoomPunch:
    DESCRIPTION = ("A quick pulse zoom on the frames you choose, for beats and hits. The zoom jumps in on the chosen frame "
                   "and eases back out. Frames without a hit stay as they are.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "frames": ("STRING", {"default": "", "multiline": False, "tooltip": "Frame numbers to punch on, counted from 0, like 12, 30, 48. Empty means none."}),
                "strength": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Extra zoom at the peak. 0.15 means 15 percent bigger on the hit frame."}),
                "length": ("INT", {"default": 8, "min": 2, "max": 60, "tooltip": "How many frames the zoom takes to ease back to normal."}),
                "centre_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Horizontal point the zoom grows from. 0 is the left edge, 1 the right."}),
                "centre_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Vertical point the zoom grows from. 0 is the top edge, 1 the bottom."}),
            }
        }

    def run(self, images, frames, strength, length, centre_x, centre_y):
        return (punch(images, frames, strength, length, centre_x, centre_y),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ZoomPunch", SYZoomPunch)
NODE_DISPLAY_NAME_MAPPINGS["SYZoomPunch"] = "Zoom Punch SY"
