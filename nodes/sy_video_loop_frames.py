"""Video Loop Frames SY: repeats or bounces a batch of frames until it reaches a target length."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_videoframes import LOOP_MODES, loop_indices
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_videoframes import LOOP_MODES, loop_indices


class SYVideoLoopFrames:
    DESCRIPTION = "Fills a target frame count by repeating the frames from the start, or by playing them forward and back."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to loop."}),
                "target_frames": ("INT", {"default": 81, "min": 1, "max": 100000, "tooltip": "How many frames the result should have."}),
                "mode": (LOOP_MODES, {"default": "repeat", "tooltip": "repeat starts over at the end. ping_pong plays back and forth."}),
            }
        }

    def run(self, images, target_frames, mode):
        check_shape(images.shape)
        ids = loop_indices(images.shape[0], target_frames, mode)
        return (images[ids], len(ids))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoLoopFrames", SYVideoLoopFrames)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoLoopFrames"] = "Video Loop Frames SY"
