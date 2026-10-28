"""Batch Repeat SY: repeats every picture N times in a row, or the whole batch N times."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape

MODES = ("each_picture", "whole_batch")
MAX_OUT = 4096


def repeat_indices(total, times, mode):
    """Pure function. each_picture: 0,0,1,1,2,2 (times=2). whole_batch: 0,1,2,0,1,2."""
    total, times = int(total), int(times)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 picture, got %d" % total)
    if times < 1:
        raise ValueError("times must be at least 1, got %d" % times)
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    if total * times > MAX_OUT:
        raise ValueError("that would make %d pictures, more than %d: lower times" % (total * times, MAX_OUT))
    if mode == "each_picture":
        return [i for i in range(total) for _ in range(times)]
    return list(range(total)) * times


class SYBatchRepeat:
    DESCRIPTION = "Repeats each picture N times in a row, or repeats the whole batch N times."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to repeat."}),
                "times": ("INT", {"default": 2, "min": 1, "max": 256, "tooltip": "How many copies of each picture, or of the whole batch."}),
                "mode": (list(MODES), {"default": "each_picture", "tooltip": "each_picture gives 1,1,2,2. whole_batch gives 1,2,1,2."}),
            }
        }

    def run(self, images, times, mode):
        check_shape(images.shape)
        ids = repeat_indices(images.shape[0], times, mode)
        return (images[ids], len(ids))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchRepeat", SYBatchRepeat)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchRepeat"] = "Batch Repeat SY"
