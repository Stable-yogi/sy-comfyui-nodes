"""Batch Pick SY: takes a slice of images from a batch, starting at an index, wrapping around the end."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def pick_indices(total, index, count, wrap=True):
    """Pure function. Returns `count` indices starting at `index`, wrapping with modulo over `total`."""
    total = int(total)
    count = int(count)
    if total <= 0:
        raise ValueError("batch is empty: total must be at least 1, got %d" % total)
    if count < 1:
        raise ValueError("count must be at least 1, got %d" % count)
    if not wrap:
        if int(index) + count > total:
            raise ValueError("cannot take %d pictures from number %d: the batch only holds %d (count from 0). "
                             "Lower index or count, or turn wrap on" % (count, int(index), total))
        return [int(index) + i for i in range(count)]
    start = int(index) % total
    return [(start + i) % total for i in range(count)]


def pick_info(total, ids):
    """Pure function. Plain sentence listing the picked positions (counted from 0)."""
    return "Took %s of %d (counting from 0)" % (", ".join(str(i) for i in ids), total)


class SYBatchPick:
    DESCRIPTION = ("Picks a slice of pictures from a batch. Starts at the index and wraps around to the first one, "
                   "or stops with a clear message when wrap is off. Tells you which positions it took.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to pick from."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "First picture to take, counting from 0. Too big a number wraps around."}),
                "count": ("INT", {"default": 1, "min": 1, "max": 64, "tooltip": "How many pictures to take. It wraps to the start when the batch ends."}),
            },
            "optional": {
                "wrap": ("BOOLEAN", {"default": True, "tooltip": "On: go round to the first picture at the end. Off: stop with an error if the slice does not fit."}),
            },
        }

    def run(self, images, index, count, wrap=True):
        ids = pick_indices(images.shape[0], index, count, wrap)
        return (images[ids], pick_info(images.shape[0], ids))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchPick", SYBatchPick)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchPick"] = "Batch Pick SY"
