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


class SYFrameInterpolateBlend:
    DESCRIPTION = "Inserts cross-fade frames between neighbouring frames. This is a plain blend, not motion interpolation, so fast motion looks ghosted."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to add blend frames to. Needs at least 2."}),
                "between": ("INT", {"default": 1, "min": 1, "max": 32, "tooltip": "How many blend frames to insert between each pair of frames."}),
                "loop": ("BOOLEAN", {"default": False, "tooltip": "Also blend from the last frame back to the first, for a looping clip."}),
            }
        }

    def run(self, images, between, loop):
        import torch

        check_shape(images.shape)
        plan = interp_plan(images.shape[0], between, bool(loop))
        ia = torch.tensor([p[0] for p in plan], dtype=torch.long, device=images.device)
        ib = torch.tensor([p[1] for p in plan], dtype=torch.long, device=images.device)
        w = torch.tensor([p[2] for p in plan], dtype=images.dtype, device=images.device).view(-1, 1, 1, 1)
        out = images[ia] * (1.0 - w) + images[ib] * w
        return (out, int(out.shape[0]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameInterpolateBlend", SYFrameInterpolateBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameInterpolateBlend"] = "Frame Interpolate Blend SY"
