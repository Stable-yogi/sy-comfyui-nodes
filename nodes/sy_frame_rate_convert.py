"""Frame Rate Convert SY: changes the frame rate of a batch by picking the nearest frames."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_videoframes import rate_convert_indices
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_videoframes import rate_convert_indices


class SYFrameRateConvert:
    DESCRIPTION = "Changes the frame rate of a clip, keeping its length. It drops or repeats the nearest frames, no blending."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT")
    RETURN_NAMES = ("images", "count", "fps")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip."}),
                "source_fps": ("FLOAT", {"default": 24.0, "min": 0.1, "max": 1000.0, "step": 1.0, "tooltip": "The frame rate the clip has now."}),
                "target_fps": ("FLOAT", {"default": 16.0, "min": 0.1, "max": 1000.0, "step": 1.0, "tooltip": "The frame rate you want."}),
            }
        }

    def run(self, images, source_fps, target_fps):
        check_shape(images.shape)
        ids = rate_convert_indices(images.shape[0], source_fps, target_fps)
        return (images[ids], len(ids), float(target_fps))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameRateConvert", SYFrameRateConvert)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameRateConvert"] = "Frame Rate Convert SY"
