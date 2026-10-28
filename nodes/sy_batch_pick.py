"""Batch Pick SY: takes a slice of images from a batch, starting at an index, wrapping around the end."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def pick_indices(total, index, count):
    """Pure function. Returns `count` indices starting at `index`, wrapping with modulo over `total`."""
    total = int(total)
    count = int(count)
    if total <= 0:
        raise ValueError("batch is empty: total must be at least 1, got %d" % total)
    if count < 1:
        raise ValueError("count must be at least 1, got %d" % count)
    start = int(index) % total
    return [(start + i) % total for i in range(count)]


class SYBatchPick:
    DESCRIPTION = "Picks a slice of pictures from a batch. Starts at the index and wraps around to the first one."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to pick from."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "First picture to take, counting from 0. Too big a number wraps around."}),
                "count": ("INT", {"default": 1, "min": 1, "max": 64, "tooltip": "How many pictures to take. It wraps to the start when the batch ends."}),
            }
        }

    def run(self, images, index, count):
        ids = pick_indices(images.shape[0], index, count)
        return (images[ids],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchPick", SYBatchPick)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchPick"] = "Batch Pick SY"
