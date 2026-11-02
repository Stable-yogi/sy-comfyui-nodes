"""Batch Interleave SY: weaves two picture batches together: A1 B1 A2 B2 ..."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ["stop at shorter", "keep the rest"]


def interleave_plan(len_a, len_b, when_uneven="keep the rest"):
    """Pure function. Returns a list of ("a"|"b", index) in weaving order."""
    len_a, len_b = int(len_a), int(len_b)
    if len_a < 1 or len_b < 1:
        raise ValueError("both batches need at least one picture (A has %d, B has %d)" % (len_a, len_b))
    if when_uneven not in MODES:
        raise ValueError("when_uneven must be one of: %s (got %r)" % (", ".join(MODES), when_uneven))
    plan = []
    for i in range(min(len_a, len_b)):
        plan.append(("a", i))
        plan.append(("b", i))
    if when_uneven == "keep the rest":
        longer, size = ("a", len_a) if len_a > len_b else ("b", len_b)
        for i in range(min(len_a, len_b), size):
            plan.append((longer, i))
    return plan


class SYBatchInterleave:
    DESCRIPTION = ("Weaves two batches of pictures into one: first of A, first of B, second of A, and so on. "
                   "If one batch is longer you can keep its extra pictures or stop at the shorter one.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_a": ("IMAGE", {"tooltip": "The first batch. Its pictures go first in each pair."}),
                "images_b": ("IMAGE", {"tooltip": "The second batch. Its pictures go second in each pair."}),
                "when_uneven": (MODES, {"default": "keep the rest", "tooltip": "If the batches differ in length: keep the extra pictures or stop."}),
                "resize_b": ("BOOLEAN", {"default": True, "tooltip": "On: resize B to the size of A if they differ. Off: stop with an error."}),
            }
        }

    def run(self, images_a, images_b, when_uneven, resize_b):
        import torch
        import torch.nn.functional as F

        plan = interleave_plan(images_a.shape[0], images_b.shape[0], when_uneven)
        if images_a.shape[-1] != images_b.shape[-1]:
            raise ValueError("the pictures have different colour channels (A has %d, B has %d). "
                             "Convert one batch first" % (images_a.shape[-1], images_b.shape[-1]))
        if images_a.shape[1:3] != images_b.shape[1:3]:
            if not resize_b:
                raise ValueError("size differs: A is %dx%d, B is %dx%d. Turn resize_b on or resize one batch first"
                                 % (images_a.shape[2], images_a.shape[1], images_b.shape[2], images_b.shape[1]))
            moved = images_b.movedim(-1, 1)
            moved = F.interpolate(moved, size=(images_a.shape[1], images_a.shape[2]), mode="bilinear", align_corners=False)
            images_b = moved.movedim(1, -1)
        both = torch.cat([images_a, images_b.to(images_a.dtype)], dim=0)
        offset = images_a.shape[0]
        ids = [i if src == "a" else offset + i for src, i in plan]
        return (both[ids],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchInterleave", SYBatchInterleave)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchInterleave"] = "Batch Interleave SY"
