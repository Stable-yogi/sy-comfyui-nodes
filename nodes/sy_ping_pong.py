"""Ping Pong SY: plays a batch forward and then backward, for a smooth back-and-forth loop."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_d3_info import plural
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_d3_info import plural


def pingpong_info(total, repeat_ends=False):
    """Pure function. Plain sentence: frames in, frames out, and whether a loop will be smooth."""
    order = pingpong_order(total, repeat_ends)
    text = "%s became %s (forward, then back" % (plural(total, "frame"), plural(len(order), "frame"))
    text += "; first and last frame shown twice)." if repeat_ends else "; no frame doubled, so a loop is smooth)."
    if total == 1:
        text += " Only 1 frame: there is nothing to play backwards."
    elif total == 2 and not repeat_ends:
        text += " With 2 frames and no repeated ends the result is the same as the input."
    return text


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
    DESCRIPTION = "Adds the frames played backwards after the forward ones, so a clip goes there and back and loops smoothly. The info output tells how many frames came out."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("images", "count", "info")

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
        return (images[ids], len(ids), pingpong_info(images.shape[0], bool(repeat_ends)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PingPong", SYPingPong)
NODE_DISPLAY_NAME_MAPPINGS["SYPingPong"] = "Ping Pong SY"
