"""Ping Pong SY: plays a batch forward and then backward, for a smooth back-and-forth loop."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape


def pingpong_order(total, repeat_ends=False):
    """Pure function. 0..n-1 then back down. By default the end frames are not shown twice (best for loops)."""
    total = int(total)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 frame, got %d" % total)
    forward = list(range(total))
    if repeat_ends:
        back = list(range(total - 1, -1, -1))
    else:
        back = list(range(total - 2, 0, -1))
    return forward + back


class SYPingPong:
    DESCRIPTION = "Adds the frames played backwards after the forward ones, so a clip goes there and back and loops smoothly."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to play forward and then backward."}),
                "repeat_ends": ("BOOLEAN", {"default": False, "tooltip": "On: show the first and last frame twice. Off: no doubled frames, best for loops."}),
            }
        }

    def run(self, images, repeat_ends):
        check_shape(images.shape)
        ids = pingpong_order(images.shape[0], bool(repeat_ends))
        return (images[ids], len(ids))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PingPong", SYPingPong)
NODE_DISPLAY_NAME_MAPPINGS["SYPingPong"] = "Ping Pong SY"
