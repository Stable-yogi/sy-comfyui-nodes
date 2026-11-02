"""Batch Shuffle SY: shuffles the order of a picture batch. Same seed gives the same order on every machine."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_MASK = (1 << 64) - 1


def _stream(seed):
    """Tiny deterministic generator (splitmix64). Own state, never touches the global random state."""
    state = int(seed) & _MASK
    while True:
        state = (state + 0x9E3779B97F4A7C15) & _MASK
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
        yield z ^ (z >> 31)


def shuffle_order(count, seed=0):
    """Pure function. Returns a list holding 0..count-1 in a shuffled order (Fisher-Yates)."""
    count = int(count)
    if count < 1:
        raise ValueError("batch is empty: count must be at least 1, got %d" % count)
    seed = int(seed)
    if seed < 0:
        raise ValueError("seed must be 0 or more, got %d" % seed)
    order = list(range(count))
    gen = _stream(seed)
    for i in range(count - 1, 0, -1):
        j = next(gen) % (i + 1)
        order[i], order[j] = order[j], order[i]
    return order


class SYBatchShuffle:
    DESCRIPTION = ("Shuffles the order of a batch of pictures. The same seed always gives the same order, "
                   "and the order is also given as text such as 3,0,2,1.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "order")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to shuffle."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Same number, same order. Change it for a different order."}),
            }
        }

    def run(self, images, seed):
        order = shuffle_order(images.shape[0], seed)
        return (images[order], ",".join(str(i) for i in order))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchShuffle", SYBatchShuffle)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchShuffle"] = "Batch Shuffle SY"
