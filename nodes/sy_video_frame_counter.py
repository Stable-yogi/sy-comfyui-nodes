"""Video Frame Counter SY: works out frames, seconds or fps from the other two values."""
try:
    from ._sy_common import category, register
    from ._sy_videoframes import COUNT_MODES, count_video
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_videoframes import COUNT_MODES, count_video


class SYVideoFrameCounter:
    DESCRIPTION = "Works out the missing one of frames, seconds and frames per second. Gives the numbers and a text line."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("frames", "seconds", "fps", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (COUNT_MODES, {"default": "frames_to_seconds", "tooltip": "Which value to work out. The other two are used."}),
                "frames": ("INT", {"default": 81, "min": 1, "max": 1000000, "tooltip": "Number of frames. Used unless the mode works out the frames."}),
                "seconds": ("FLOAT", {"default": 5.0, "min": 0.01, "max": 100000.0, "step": 0.1, "tooltip": "Length in seconds. Used unless the mode works out the seconds."}),
                "fps": ("FLOAT", {"default": 16.0, "min": 0.1, "max": 1000.0, "step": 1.0, "tooltip": "Frames per second. Used unless the mode works out the fps."}),
            }
        }

    def run(self, mode, frames, seconds, fps):
        return count_video(mode, frames, seconds, fps)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoFrameCounter", SYVideoFrameCounter)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoFrameCounter"] = "Video Frame Counter SY"
