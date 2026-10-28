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


class SYCompareMetrics:
    DESCRIPTION = ("Compares two images of the same size. diff_score is the mean absolute difference "
                   "(0 = identical, 1 = opposite). diff_image shows the difference, brightened by gain.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "IMAGE")
    RETURN_NAMES = ("diff_score", "diff_image")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "gain": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 1000.0, "step": 0.1}),
            }
        }

    def run(self, image_a, image_b, gain=4.0):
        import torch  # inside the function on purpose
        check_same_shape(tuple(image_a.shape), tuple(image_b.shape))
        diff = torch.abs(image_a.float() - image_b.float())
        score = float(diff.mean().item()) if diff.numel() else 0.0
        out = torch.clamp(diff * float(gain), 0.0, 1.0)
        return (score, out)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CompareMetrics", SYCompareMetrics)
NODE_DISPLAY_NAME_MAPPINGS["SYCompareMetrics"] = "Compare Metrics SY"
