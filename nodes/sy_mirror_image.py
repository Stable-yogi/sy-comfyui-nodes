"""Mirror Image SY: copies one half (or one quarter) of a picture, flipped, onto the other side."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

MODES = ("left_to_right", "right_to_left", "top_to_bottom", "bottom_to_top", "four_way")


def check_mode(mode):
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))


def mirror_index(i, size, from_start):
    """Pure function. Source index for position i when one half is mirrored onto the other.
    from_start True: the first half is kept; False: the last half is kept. A middle cell of an odd size stays."""
    if size < 1:
        raise ValueError("size must be at least 1, got %s" % size)
    if not 0 <= i < size:
        raise ValueError("index %s is outside 0..%s" % (i, size - 1))
    mirrored = size - 1 - i
    if from_start:
        return i if i <= mirrored else mirrored
    return i if i >= mirrored else mirrored


def axis_indices(size, from_start):
    return [mirror_index(i, size, from_start) for i in range(size)]


def mode_axes(mode):
    """Pure function. (rows_from_start, cols_from_start); None means that axis is left alone."""
    check_mode(mode)
    return {
        "left_to_right": (None, True),
        "right_to_left": (None, False),
        "top_to_bottom": (True, None),
        "bottom_to_top": (False, None),
        "four_way": (True, True),
    }[mode]


class SYMirrorImage:
    DESCRIPTION = "Copies one half of a picture, flipped, onto the other half so it becomes symmetric. Four way mirrors one quarter."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to mirror."}),
                "mode": (list(MODES), {"default": "left_to_right", "tooltip": "Which side is kept and copied over the other. four_way copies the top-left quarter."}),
            }
        }

    def run(self, image, mode):
        import torch

        need_image(image)
        rows_start, cols_start = mode_axes(mode)
        out = image
        if rows_start is not None:
            idx = torch.tensor(axis_indices(image.shape[1], rows_start), dtype=torch.long, device=image.device)
            out = out.index_select(1, idx)
        if cols_start is not None:
            idx = torch.tensor(axis_indices(image.shape[2], cols_start), dtype=torch.long, device=image.device)
            out = out.index_select(2, idx)
        return (out.contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MirrorImage", SYMirrorImage)
NODE_DISPLAY_NAME_MAPPINGS["SYMirrorImage"] = "Mirror Image SY"
