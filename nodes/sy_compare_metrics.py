"""Compare Metrics SY: mean absolute difference score and a difference image for two images."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_same_shape(shape_a, shape_b):
    """Pure function. Raises a clear ValueError when the two image shapes differ (no resizing is done)."""
    a = tuple(int(x) for x in shape_a)
    b = tuple(int(x) for x in shape_b)
    if a != b:
        raise ValueError(
            "image_a and image_b must have the same size and batch (got %s and %s); resize one first" % (a, b))
    return a


def mean_abs_diff(a_flat, b_flat):
    """Pure function on plain float sequences. Returns the mean of |a-b| (0.0 for empty input)."""
    if len(a_flat) != len(b_flat):
        raise ValueError("sequences must have the same length (%d vs %d)" % (len(a_flat), len(b_flat)))
    n = len(a_flat)
    if n == 0:
        return 0.0
    return sum(abs(float(x) - float(y)) for x, y in zip(a_flat, b_flat)) / n


def amplify_clamp(value, gain):
    """Pure function. abs-difference value times gain, clamped to 0..1."""
    return max(0.0, min(1.0, abs(float(value)) * float(gain)))


def psnr_from_mean_sq(mse):
    """Pure function. Peak signal-to-noise ratio in dB for pictures in 0..1 (99.0 when identical)."""
    import math
    if mse < 0:
        raise ValueError("mean squared difference cannot be negative")
    if mse <= 1e-12:
        return 99.0
    return min(99.0, 10.0 * math.log10(1.0 / mse))


def verdict(score):
    """Pure function. Plain words for a mean difference."""
    if score <= 0.0:
        return "identical"
    if score < 0.01:
        return "almost identical"
    if score < 0.05:
        return "small differences"
    if score < 0.15:
        return "clear differences"
    return "very different"


class SYCompareMetrics:
    DESCRIPTION = ("Compares two images of the same size. diff_score is the mean absolute difference "
                   "(0 = identical, 1 = opposite). diff_image shows the difference, brightened by gain. "
                   "Can compare only inside a mask, can resize image_b to fit, and also gives the biggest difference, a PSNR score and a plain verdict.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "IMAGE", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("diff_score", "diff_image", "max_diff", "psnr", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE", {"tooltip": "The first picture to compare, for example the original."}),
                "image_b": ("IMAGE", {"tooltip": "The second picture to compare. It must be the same size as the first."}),
                "gain": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 1000.0, "step": 0.1, "tooltip": "Makes small differences easier to see in the output. 1 = true size, 4 = four times brighter."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "Optional. Compare only where the mask is white. A different size is stretched to fit."}),
                "resize_b": ("BOOLEAN", {"default": False, "tooltip": "On: resize image_b to image_a's size first. Off: stop with a message when the sizes differ."}),
            },
        }

    def run(self, image_a, image_b, gain=4.0, mask=None, resize_b=False):
        import torch  # inside the function on purpose
        if resize_b:
            import torch.nn.functional as F
            ch = min(image_a.shape[-1], image_b.shape[-1])
            image_a, image_b = image_a[..., :ch], image_b[..., :ch]
            if image_b.shape[1:3] != image_a.shape[1:3]:
                image_b = F.interpolate(image_b.permute(0, 3, 1, 2).float(), size=tuple(image_a.shape[1:3]),
                                        mode="bilinear", align_corners=False).permute(0, 2, 3, 1)
            if image_b.shape[0] != image_a.shape[0] and image_b.shape[0] == 1:
                image_b = image_b.expand(image_a.shape[0], -1, -1, -1)
        check_same_shape(tuple(image_a.shape), tuple(image_b.shape))
        diff = torch.abs(image_a.float() - image_b.float())
        if mask is not None:
            import torch.nn.functional as F
            m = mask.float() if mask.dim() == 3 else mask.float().unsqueeze(0)
            if m.shape[0] not in (1, diff.shape[0]):
                raise ValueError("the mask holds %d masks but the pictures hold %d; use 1 mask or the same number" % (m.shape[0], diff.shape[0]))
            if tuple(m.shape[1:]) != tuple(diff.shape[1:3]):
                m = F.interpolate(m.unsqueeze(1), size=tuple(diff.shape[1:3]), mode="bilinear", align_corners=False).squeeze(1)
            m = m.clamp(0.0, 1.0).to(diff.device).unsqueeze(-1)
            weight = float((m.expand(diff.shape[0], -1, -1, -1).sum() * diff.shape[-1]).item())
            if weight <= 0.0:
                raise ValueError("the mask is empty (all black), so there is nothing to compare; paint something white")
            diff = diff * m
            score = float(diff.sum().item()) / weight
            mse = float((diff * diff).sum().item()) / weight
        else:
            score = float(diff.mean().item()) if diff.numel() else 0.0
            mse = float((diff * diff).mean().item()) if diff.numel() else 0.0
        top = float(diff.max().item()) if diff.numel() else 0.0
        out = torch.clamp(diff * float(gain), 0.0, 1.0)
        psnr = psnr_from_mean_sq(mse)
        info = "Difference %.4f (%s), biggest single difference %.3f, PSNR %.1f dB%s" % (
            score, verdict(score), top, psnr, ", inside the mask only" if mask is not None else "")
        return (score, out, top, psnr, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CompareMetrics", SYCompareMetrics)
NODE_DISPLAY_NAME_MAPPINGS["SYCompareMetrics"] = "Compare Metrics SY"
