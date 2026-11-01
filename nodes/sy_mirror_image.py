"""Mirror Image SY: copies one half (or one quarter) of a picture, flipped, onto the other side."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_d3_info import need_nonempty, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_d3_info import need_nonempty, size_text

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


SIDE_WORDS = {
    "left_to_right": "left half onto the right",
    "right_to_left": "right half onto the left",
    "top_to_bottom": "top half onto the bottom",
    "bottom_to_top": "bottom half onto the top",
    "four_way": "top-left quarter onto the other three",
}


def mirror_info(mode, width, height):
    """Pure function. Plain sentence: what was copied, plus a note about a middle line that stays when a side is odd."""
    check_mode(mode)
    rows_start, cols_start = mode_axes(mode)
    text = "Copied the %s of a %s picture." % (SIDE_WORDS[mode], size_text(width, height))
    notes = []
    if cols_start is not None and width % 2 == 1:
        notes.append("middle column %d" % (width // 2))
    if rows_start is not None and height % 2 == 1:
        notes.append("middle row %d" % (height // 2))
    if notes:
        text += " The side is an odd number of pixels, so the " + " and ".join(notes) + " stays as it is."
    if (cols_start is not None and width < 2) or (rows_start is not None and height < 2):
        text += " The picture is only 1 pixel wide in that direction, so nothing changed."
    return text


class SYMirrorImage:
    DESCRIPTION = "Copies one half of a picture, flipped, onto the other half so it becomes symmetric. Four way mirrors one quarter. The info output says which side was copied and what happens with an odd-sized picture."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

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
        need_nonempty(image.shape)
        rows_start, cols_start = mode_axes(mode)
        out = image
        if rows_start is not None:
            idx = torch.tensor(axis_indices(image.shape[1], rows_start), dtype=torch.long, device=image.device)
            out = out.index_select(1, idx)
        if cols_start is not None:
            idx = torch.tensor(axis_indices(image.shape[2], cols_start), dtype=torch.long, device=image.device)
            out = out.index_select(2, idx)
        return (out.contiguous(), mirror_info(mode, int(image.shape[2]), int(image.shape[1])))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MirrorImage", SYMirrorImage)
NODE_DISPLAY_NAME_MAPPINGS["SYMirrorImage"] = "Mirror Image SY"
