"""Aspect Bucket SY: finds the training bucket (size) that best fits a picture shape."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DEFAULT_BUCKETS = "1:1, 4:3, 3:2, 16:9"


def parse_buckets(text, include_flips=True):
    """Pure function. '1:1, 4:3' -> [(1, 1), (4, 3), (3, 4)]. Flips (3:4 for 4:3) are added when asked. Order is kept, no repeats."""
    out = []
    for item in (text or "").replace("\n", ",").split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.replace("/", ":").split(":")
        try:
            if len(parts) != 2:
                raise ValueError
            a, b = int(parts[0]), int(parts[1])
            if a < 1 or b < 1:
                raise ValueError
        except ValueError:
            raise ValueError('bucket "%s" is not a ratio; write it like 16:9 with whole numbers above 0' % item)
        for pair in ((a, b), (b, a)) if include_flips else ((a, b),):
            if pair not in out:
                out.append(pair)
    if not out:
        raise ValueError("the bucket list is empty; write ratios like 1:1, 4:3, 16:9")
    return out


def bucket_size(ratio_w, ratio_h, target, multiple=64):
    """Pure function. Width and height for this ratio with about target*target pixels, each a multiple of `multiple` (at least one step)."""
    r = ratio_w / float(ratio_h)
    w = target * math.sqrt(r)
    h = target / math.sqrt(r)
    snap = lambda v: max(multiple, int(math.floor(v / multiple + 0.5)) * multiple)
    return snap(w), snap(h)


def pick_bucket(width, height, buckets_text=DEFAULT_BUCKETS, target=1024, multiple=64, include_flips=True):
    """Pure function. Returns (bucket_width, bucket_height, label). The nearest ratio is chosen on a log scale, so 2:1 and 1:2 are equally far from 1:1."""
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1 (got %sx%s)" % (width, height))
    if multiple < 1:
        raise ValueError("multiple must be at least 1 (got %s)" % multiple)
    if target < multiple:
        raise ValueError("target resolution (%s) must be at least the multiple (%s)" % (target, multiple))
    buckets = parse_buckets(buckets_text, include_flips)
    here = math.log(width / float(height))
    best = min(buckets, key=lambda ab: abs(math.log(ab[0] / float(ab[1])) - here))
    bw, bh = bucket_size(best[0], best[1], target, multiple)
    return bw, bh, "%d:%d" % best


class SYAspectBucket:
    DESCRIPTION = "Picks the training size whose shape is closest to your picture, for example 1344x768 for a wide picture."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("bucket_width", "bucket_height", "ratio")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": 65536, "tooltip": "Width of your picture in pixels."}),
                "height": ("INT", {"default": 1024, "min": 1, "max": 65536, "tooltip": "Height of your picture in pixels."}),
                "buckets": ("STRING", {"default": DEFAULT_BUCKETS, "tooltip": "Allowed shapes as ratios, separated by commas, for example 1:1, 4:3, 16:9."}),
                "include_flips": ("BOOLEAN", {"default": True, "tooltip": "On: also allow the upright version of each shape, so 4:3 gives 3:4 too."}),
                "target_resolution": ("INT", {"default": 1024, "min": 64, "max": 8192, "tooltip": "Side of the square the bucket area is based on. 1024 gives about one megapixel."}),
                "multiple_of": ("INT", {"default": 64, "min": 1, "max": 512, "tooltip": "Bucket width and height are rounded to a multiple of this number."}),
            }
        }

    def run(self, width, height, buckets, include_flips, target_resolution, multiple_of):
        return pick_bucket(width, height, buckets, target_resolution, multiple_of, include_flips)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AspectBucket", SYAspectBucket)
NODE_DISPLAY_NAME_MAPPINGS["SYAspectBucket"] = "Aspect Bucket SY"
