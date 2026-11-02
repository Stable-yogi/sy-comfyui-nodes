"""Fade Mask Batch SY: makes a batch of masks that fade over time, evenly or as a soft edge sweeping across the frame."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CURVES = ("linear", "ease_in", "ease_out", "ease_in_out")
DIRECTIONS = ("whole", "left_to_right", "right_to_left", "top_to_bottom", "bottom_to_top")
SOFT_EDGE = 0.25  # width of the moving edge, as a share of the frame


def curve_value(t, curve="linear"):
    """Pure function. Maps time t (0..1) through a curve. 0 stays 0, 1 stays 1."""
    if curve not in CURVES:
        raise ValueError("curve must be one of: %s, got %r" % (", ".join(CURVES), curve))
    t = min(1.0, max(0.0, float(t)))
    if curve == "linear":
        return t
    if curve == "ease_in":
        return t * t
    if curve == "ease_out":
        return 1.0 - (1.0 - t) * (1.0 - t)
    return t * t * (3.0 - 2.0 * t)


def check_args(width, height, frames, start_value, end_value, direction):
    if int(width) < 1 or int(height) < 1:
        raise ValueError("width and height must be at least 1, got %dx%d" % (int(width), int(height)))
    if int(frames) < 1:
        raise ValueError("frames must be at least 1, got %d" % int(frames))
    for name, v in (("start_value", start_value), ("end_value", end_value)):
        if not 0.0 <= float(v) <= 1.0:
            raise ValueError("%s must be between 0 and 1, got %s" % (name, v))
    if direction not in DIRECTIONS:
        raise ValueError("direction must be one of: %s, got %r" % (", ".join(DIRECTIONS), direction))


def frame_progress(frames, curve="linear"):
    """Pure function. Curved progress 0..1 for every frame. The last frame is always 1 (a single frame is 1)."""
    frames = int(frames)
    if frames < 1:
        raise ValueError("frames must be at least 1, got %d" % frames)
    if frames == 1:
        return [1.0]
    return [curve_value(i / float(frames - 1), curve) for i in range(frames)]


def frame_values(frames, start_value, end_value, curve="linear"):
    """Pure function. Plain list: the whole-mask value of every frame."""
    return [float(start_value) + (float(end_value) - float(start_value)) * p for p in frame_progress(frames, curve)]


def sweep_factor(pos, progress, soft=SOFT_EDGE):
    """Pure function. How far a pixel at position pos (0..1 along the sweep) has faded (0 = start, 1 = end)."""
    front = progress * (1.0 + soft)
    return min(1.0, max(0.0, (front - pos) / soft))


def sweep_row(length, progress, soft=SOFT_EDGE, reverse=False):
    """Pure function. sweep_factor for each of `length` pixels along one line (reverse flips the direction)."""
    length = int(length)
    out = []
    for i in range(length):
        pos = i / float(length - 1) if length > 1 else 0.0
        out.append(sweep_factor(1.0 - pos if reverse else pos, progress, soft))
    return out


def mask_info(frames, width, height, start_value, end_value, curve, direction):
    return "Fade Mask Batch: %d masks of %dx%d, %s -> %s, %s, %s" % (frames, width, height, start_value, end_value, curve, direction)


class SYFadeMaskBatch:
    DESCRIPTION = ("Makes a batch of masks that fade from one value to another. Direction whole fades the entire mask evenly. "
                   "The other directions sweep a soft edge across the frame over time. Good for wipes and reveals.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("masks", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 1, "max": 16384, "tooltip": "Mask width in pixels."}),
                "height": ("INT", {"default": 512, "min": 1, "max": 16384, "tooltip": "Mask height in pixels."}),
                "frames": ("INT", {"default": 16, "min": 1, "max": 4096, "tooltip": "How many masks to make."}),
                "start_value": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Mask value in the first frame (0 black, 1 white)."}),
                "end_value": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Mask value in the last frame (0 black, 1 white)."}),
                "curve": (list(CURVES), {"default": "linear", "tooltip": "How the fade speeds up or slows down over time."}),
                "direction": (list(DIRECTIONS), {"default": "whole", "tooltip": "whole fades evenly; the others sweep a soft edge across the frame."}),
            },
        }

    def run(self, width, height, frames, start_value, end_value, curve, direction):
        import torch

        check_args(width, height, frames, start_value, end_value, direction)
        prog = frame_progress(frames, curve)
        s, e = float(start_value), float(end_value)
        if direction == "whole":
            vals = torch.tensor([s + (e - s) * p for p in prog], dtype=torch.float32)
            out = vals.view(-1, 1, 1).expand(int(frames), int(height), int(width)).contiguous()
        else:
            horizontal = direction in ("left_to_right", "right_to_left")
            reverse = direction in ("right_to_left", "bottom_to_top")
            length = int(width) if horizontal else int(height)
            rows = torch.tensor([sweep_row(length, p, SOFT_EDGE, reverse) for p in prog], dtype=torch.float32)  # [F, length]
            fac = rows.view(int(frames), 1, length) if horizontal else rows.view(int(frames), length, 1)
            out = (s + (e - s) * fac).expand(int(frames), int(height), int(width)).contiguous()
        return (out, mask_info(int(frames), int(width), int(height), s, e, curve, direction))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FadeMaskBatch", SYFadeMaskBatch)
NODE_DISPLAY_NAME_MAPPINGS["SYFadeMaskBatch"] = "Fade Mask Batch SY"
