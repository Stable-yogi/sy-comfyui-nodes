"""Sharpest Frame Pick SY: keeps the N least blurry frames of a batch."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ORDERS = ["original order", "best first"]


def sharpness_score(rows):
    """Pure function. `rows` is a grid (list of lists) of grey values.
    Score = variance of the second-difference (Laplacian) values over the inside of the grid.
    Higher = sharper. A flat grid scores 0."""
    if not rows or not rows[0]:
        raise ValueError("the grey picture is empty: it needs at least 3 rows and 3 columns")
    h = len(rows)
    w = len(rows[0])
    for r in rows:
        if len(r) != w:
            raise ValueError("the grey rows have different lengths: every row must have %d values" % w)
    if h < 3 or w < 3:
        raise ValueError("the picture is too small to measure sharpness: it needs at least 3 x 3 pixels, got %d x %d" % (w, h))
    vals = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            vals.append(4.0 * rows[y][x] - rows[y - 1][x] - rows[y + 1][x] - rows[y][x - 1] - rows[y][x + 1])
    mean = sum(vals) / len(vals)
    return sum((v - mean) ** 2 for v in vals) / len(vals)


def pick_sharpest(scores, keep, order="original order"):
    """Pure function. Returns the frame numbers of the `keep` highest scores
    (ties go to the earlier frame), in the chosen order. keep above the batch size keeps everything."""
    keep = int(keep)
    if len(scores) < 1:
        raise ValueError("the batch is empty: there are no frames to pick from")
    if keep < 1:
        raise ValueError("keep must be at least 1, got %d" % keep)
    if order not in ORDERS:
        raise ValueError("keep_order must be one of: %s" % ", ".join(ORDERS))
    ranked = sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:keep]
    if order == "original order":
        ranked.sort()
    return ranked


class SYSharpestFramePick:
    DESCRIPTION = ("From a batch (a burst of renders or video frames) keeps the frames that are least blurry. "
                   "Also gives a sharpness number for every input frame. Higher means sharper.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "scores")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of frames to look through."}),
                "keep": ("INT", {"default": 1, "min": 1, "max": 64, "tooltip": "How many of the sharpest frames to keep. More than the batch keeps all."}),
                "keep_order": (ORDERS, {"default": "original order", "tooltip": "Keep the kept frames in clip order, or put the sharpest first."}),
            },
        }

    def run(self, images, keep, keep_order="original order"):
        h, w = images.shape[1], images.shape[2]
        if h < 3 or w < 3:
            raise ValueError("the pictures are too small to measure sharpness: they need at least 3 x 3 pixels, got %d x %d" % (w, h))
        c = images.shape[-1]
        rgb = images[..., :3] if c >= 3 else images[..., :1].expand(-1, -1, -1, 3)
        grey = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
        lap = (4.0 * grey[:, 1:-1, 1:-1] - grey[:, :-2, 1:-1] - grey[:, 2:, 1:-1]
               - grey[:, 1:-1, :-2] - grey[:, 1:-1, 2:])
        flat = lap.reshape(lap.shape[0], -1).double()
        scores = [float(v) for v in flat.var(dim=1, unbiased=False).tolist()]
        ids = pick_sharpest(scores, keep, keep_order)
        return (images[ids], ",".join("%.6f" % s for s in scores))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SharpestFramePick", SYSharpestFramePick)
NODE_DISPLAY_NAME_MAPPINGS["SYSharpestFramePick"] = "Sharpest Frame Pick SY"
