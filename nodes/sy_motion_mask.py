"""Motion Mask SY: shows what moved between frames as a mask."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

COMPARE = ("previous frame", "first frame")


def check_args(threshold, grow, blur, compare):
    """Pure function. Raises ValueError with a plain message for bad settings."""
    if not 0.0 <= float(threshold) <= 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    if int(grow) < 0 or int(grow) > 50:
        raise ValueError("grow must be between 0 and 50 pixels, got %s" % grow)
    if int(blur) < 0 or int(blur) > 50:
        raise ValueError("blur must be between 0 and 50, got %s" % blur)
    if compare not in COMPARE:
        raise ValueError("compare must be one of %s, got %r" % (", ".join(COMPARE), compare))


def diff_to_mask(diff, threshold):
    """Pure function. List of differences -> list of 1.0 (moved) or 0.0 (still)."""
    return [1.0 if d >= threshold else 0.0 for d in diff]


def reference_index(i, compare):
    """Pure function. Which frame frame i is compared with (None = nothing to compare)."""
    if i == 0:
        return None
    return i - 1 if compare == "previous frame" else 0


def gauss_kernel(sigma):
    """Pure function. Normalised 1D gaussian weights, radius 3 sigma."""
    if sigma <= 0:
        return [1.0]
    r = max(1, int(math.ceil(3.0 * sigma)))
    w = [math.exp(-(i * i) / (2.0 * sigma * sigma)) for i in range(-r, r + 1)]
    s = sum(w)
    return [x / s for x in w]


def motion_mask(images, threshold, grow, blur, compare):
    """Torch function. images [N,H,W,C] -> mask [N,H,W]."""
    import torch
    import torch.nn.functional as F
    check_args(threshold, grow, blur, compare)
    n = images.shape[0]
    x = images[..., :3].float()
    out = torch.zeros(n, images.shape[1], images.shape[2], dtype=torch.float32)
    for i in range(n):
        ref = reference_index(i, compare)
        if ref is None:
            continue
        diff = (x[i] - x[ref]).abs().mean(dim=-1)
        out[i] = (diff >= float(threshold)).float()
    if int(grow) > 0 and n > 0:
        k = 2 * int(grow) + 1
        t = out.unsqueeze(1)
        t = F.max_pool2d(t, (k, 1), 1, (int(grow), 0))
        t = F.max_pool2d(t, (1, k), 1, (0, int(grow)))
        out = t.squeeze(1)
    if int(blur) > 0 and n > 0:
        ker = torch.tensor(gauss_kernel(float(blur)), dtype=torch.float32)
        r = (ker.numel() - 1) // 2
        t = out.unsqueeze(1)
        t = F.conv2d(F.pad(t, (0, 0, r, r), mode="replicate"), ker.view(1, 1, -1, 1))
        t = F.conv2d(F.pad(t, (r, r, 0, 0), mode="replicate"), ker.view(1, 1, 1, -1))
        out = t.squeeze(1)
    return out.clamp(0.0, 1.0).contiguous()


class SYMotionMask:
    DESCRIPTION = ("Shows what moved between frames as a mask. White where a frame differs from the frame before it "
                   "(or from the first frame), with optional grow and blur to make the shape easier to use.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "threshold": ("FLOAT", {"default": 0.08, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much a pixel must change to count as moved. Lower finds smaller changes."}),
                "grow": ("INT", {"default": 3, "min": 0, "max": 50, "tooltip": "Makes the white areas bigger by this many pixels, to close small gaps."}),
                "blur": ("INT", {"default": 2, "min": 0, "max": 50, "tooltip": "Softens the edge of the mask. 0 keeps it hard."}),
                "compare": (list(COMPARE), {"default": "previous frame", "tooltip": "Compare each frame with the one before it, or with the first frame of the clip."}),
            }
        }

    def run(self, images, threshold, grow, blur, compare):
        return (motion_mask(images, threshold, grow, blur, compare),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MotionMask", SYMotionMask)
NODE_DISPLAY_NAME_MAPPINGS["SYMotionMask"] = "Motion Mask SY"
