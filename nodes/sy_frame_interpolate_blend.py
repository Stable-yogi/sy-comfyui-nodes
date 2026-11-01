"""Frame Interpolate Blend SY: adds simple cross-fade frames between neighbours. It is a blend, not motion interpolation."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape

MAX_OUT = 8192


def blend_weights(between):
    """Pure function. Weights of the next frame for `between` inserted frames: 1/(n+1), 2/(n+1), ..."""
    between = int(between)
    if between < 1:
        raise ValueError("between must be at least 1, got %d" % between)
    return [k / (between + 1.0) for k in range(1, between + 1)]


def interp_plan(total, between, loop=False):
    """Pure function. List of (frame_a, frame_b, weight): output = a*(1-weight) + b*weight.
    Original frames have weight 0. With loop, the last frame also blends into the first (no repeated frame)."""
    total, between = int(total), int(between)
    if total < 2:
        raise ValueError("need at least 2 frames to blend between, got %d" % total)
    weights = blend_weights(between)
    count = (total if loop else total - 1) * (between + 1) + (0 if loop else 1)
    if count > MAX_OUT:
        raise ValueError("that would make %d frames, more than %d: lower between or use fewer frames" % (count, MAX_OUT))
    plan = []
    for i in range(total if loop else total - 1):
        j = (i + 1) % total
        plan.append((i, i, 0.0))
        for w in weights:
            plan.append((i, j, w))
    if not loop:
        plan.append((total - 1, total - 1, 0.0))
    return plan


def new_fps(fps, between):
    """Pure function. Frame rate that keeps the same speed after `between` frames were inserted. 0 stays 0 (unknown)."""
    if fps < 0:
        raise ValueError("fps cannot be negative, got %s" % fps)
    return float(fps) * (int(between) + 1)


def blend_info(total, between, loop, count, fps, width, height):
    """Pure function. One plain line: frames before and after, new frame rate, memory."""
    mb = count * width * height * 3 * 4 / 1048576.0
    text = "%d frames -> %d frames (%d blend frame(s) between each pair%s), %dx%d" % (
        total, count, between, ", last blends into first" if loop else "", width, height)
    if fps > 0:
        text += "; set the video frame rate to %g (was %g) to keep the same speed" % (new_fps(fps, between), fps)
    else:
        text += "; enter your frame rate in fps to get the matching new rate"
    text += "; about %.0f MB in memory" % mb
    if mb > 4096:
        text += " - that is a lot, lower between if the card runs out of memory"
    return text + "."


class SYFrameInterpolateBlend:
    DESCRIPTION = ("Inserts cross-fade frames between neighbouring frames. This is a plain blend, not motion interpolation, so fast "
                   "motion looks ghosted. Enter your fps to get the new frame rate that keeps the same speed.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("images", "count", "new_fps", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to add blend frames to. Needs at least 2."}),
                "between": ("INT", {"default": 1, "min": 1, "max": 32, "tooltip": "How many blend frames to insert between each pair of frames."}),
                "loop": ("BOOLEAN", {"default": False, "tooltip": "Also blend from the last frame back to the first, for a looping clip."}),
            },
            "optional": {
                "fps": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.1, "tooltip": "Frame rate of the original clip, for example 16. 0 means unknown."}),
            },
        }

    def run(self, images, between, loop, fps=0.0):
        import torch

        check_shape(images.shape)
        plan = interp_plan(images.shape[0], between, bool(loop))
        ia = torch.tensor([p[0] for p in plan], dtype=torch.long, device=images.device)
        ib = torch.tensor([p[1] for p in plan], dtype=torch.long, device=images.device)
        w = torch.tensor([p[2] for p in plan], dtype=images.dtype, device=images.device).view(-1, 1, 1, 1)
        out = images[ia] * (1.0 - w) + images[ib] * w
        info = blend_info(images.shape[0], int(between), bool(loop), int(out.shape[0]), float(fps), images.shape[2], images.shape[1])
        return (out, int(out.shape[0]), new_fps(float(fps), between), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameInterpolateBlend", SYFrameInterpolateBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameInterpolateBlend"] = "Frame Interpolate Blend SY"
