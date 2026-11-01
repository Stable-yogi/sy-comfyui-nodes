"""Video Loop Frames SY: repeats or bounces a batch of frames until it reaches a target length."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_videoframes import LOOP_MODES, loop_indices
    from ._sy_a2_video import snap_frames
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_videoframes import LOOP_MODES, loop_indices
    from _sy_a2_video import snap_frames


def loop_info(total, target, mode):
    """Pure function. One plain line telling how the frames were filled."""
    total, target = int(total), int(target)
    if total == 1:
        return "1 frame held for %d frames (a still)." % target
    if target < total:
        return "%d frames cut to the first %d (the target is shorter than the input)." % (total, target)
    if target == total:
        return "%d frames kept as they are (the target equals the input)." % total
    if mode == "ping_pong":
        return "%d frames played forward and back to fill %d frames." % (total, target)
    loops, rest = divmod(target, total)
    tail = "the last loop stops after %d of %d frames, so the end may jump" % (rest, total) if rest else "the loops fit exactly"
    return "%d frames repeated to fill %d frames: %d full loop%s, %s." % (total, target, loops, "" if loops == 1 else "s", tail)


class SYVideoLoopFrames:
    DESCRIPTION = ("Fills a target frame count by repeating the frames from the start, or by playing them forward and back. "
                   "Can move the target to a count a video model accepts (4n+1). The info output says how the frames were filled "
                   "and warns when the last loop is cut short.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("images", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to loop."}),
                "target_frames": ("INT", {"default": 81, "min": 1, "max": 100000, "tooltip": "How many frames the result should have."}),
                "mode": (LOOP_MODES, {"default": "repeat", "tooltip": "repeat starts over at the end. ping_pong plays back and forth."}),
            },
            "optional": {
                "snap_to_rule": ("BOOLEAN", {"default": False, "tooltip": "On: move the target to the nearest count that fits the Kn+1 rule, for example 80 becomes 81."}),
                "frame_step": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "The n in the Kn+1 rule: 4 for Wan and most models, 8 for LTX. Used with snap_to_rule."}),
            },
        }

    def run(self, images, target_frames, mode, snap_to_rule=False, frame_step=4):
        check_shape(images.shape)
        target = snap_frames(target_frames, frame_step) if snap_to_rule else int(target_frames)
        ids = loop_indices(images.shape[0], target, mode)
        info = loop_info(images.shape[0], target, mode)
        if target != int(target_frames):
            info += " The target %d was moved to %d to fit the %dn+1 rule." % (int(target_frames), target, int(frame_step))
        return (images[ids], len(ids), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoLoopFrames", SYVideoLoopFrames)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoLoopFrames"] = "Video Loop Frames SY"
