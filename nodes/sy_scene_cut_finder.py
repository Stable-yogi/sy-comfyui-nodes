"""Scene Cut Finder SY: finds the frames where the picture suddenly changes (hard cuts) in a batch."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def pair_score(values_a, values_b):
    """Pure function. Mean absolute difference between two equal-length lists of pixel values (0..1)."""
    if len(values_a) != len(values_b):
        raise ValueError("the two small pictures have different sizes (%d and %d values)" % (len(values_a), len(values_b)))
    if not values_a:
        raise ValueError("the small pictures are empty: there is nothing to compare")
    return sum(abs(a - b) for a, b in zip(values_a, values_b)) / len(values_a)


def find_cuts(scores, sensitivity, min_gap=2):
    """Pure function. scores[i] is the change between frame i and frame i+1.
    Returns the frame numbers where a new scene starts: score above `sensitivity`
    and at least `min_gap` frames after the previous cut (frame 0 counts as the first start)."""
    sensitivity = float(sensitivity)
    min_gap = int(min_gap)
    if sensitivity <= 0.0:
        raise ValueError("sensitivity must be above 0, got %s" % sensitivity)
    if min_gap < 1:
        raise ValueError("min_gap must be at least 1, got %d" % min_gap)
    cuts = []
    last = 0
    for i, s in enumerate(scores):
        frame = i + 1
        if s > sensitivity and frame - last >= min_gap:
            cuts.append(frame)
            last = frame
    return cuts


def format_cuts(cuts):
    """Pure function. Scene start list as text, always beginning with frame 0."""
    return ",".join(str(c) for c in [0] + list(cuts))


def format_scores(scores):
    return ",".join("%.4f" % s for s in scores)


class SYSceneCutFinder:
    DESCRIPTION = ("Finds the frames where the picture suddenly changes (hard cuts) in a batch, so a long clip can be split or checked. "
                   "cut_indices lists where each scene starts (always begins with 0). cut_count is the number of cuts found.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("cut_indices", "cut_count", "scores")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "sensitivity": ("FLOAT", {"default": 0.25, "min": 0.01, "max": 1.0, "step": 0.01, "tooltip": "Average pixel change between two frames that counts as a cut. Lower finds more cuts."}),
                "downscale": ("INT", {"default": 4, "min": 1, "max": 16, "tooltip": "Shrinks frames before comparing. Bigger is faster and ignores fine noise."}),
            },
        }

    def run(self, images, sensitivity, downscale):
        import torch
        import torch.nn.functional as F
        n = images.shape[0]
        if n < 2:
            return (format_cuts([]), 0, "")
        x = images[..., :3].permute(0, 3, 1, 2).float()
        d = int(downscale)
        if d > 1:
            d = max(1, min(d, x.shape[2], x.shape[3]))
            x = F.avg_pool2d(x, d, ceil_mode=True)
        diff = (x[1:] - x[:-1]).abs().mean(dim=(1, 2, 3))
        scores = [float(v) for v in diff.tolist()]
        cuts = find_cuts(scores, sensitivity)
        return (format_cuts(cuts), len(cuts), format_scores(scores))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SceneCutFinder", SYSceneCutFinder)
NODE_DISPLAY_NAME_MAPPINGS["SYSceneCutFinder"] = "Scene Cut Finder SY"
