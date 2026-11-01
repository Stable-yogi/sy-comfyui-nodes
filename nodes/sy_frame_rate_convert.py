"""Frame Rate Convert SY: changes the frame rate of a batch by picking the nearest frames."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_videoframes import rate_convert_indices
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_videoframes import rate_convert_indices


def convert_info(in_count, ids, source_fps, target_fps):
    """Pure function. Returns (seconds, info) for a conversion that picked frames `ids` out of `in_count`."""
    source_fps, target_fps = float(source_fps), float(target_fps)
    out_count = len(ids)
    seconds = round(out_count / target_fps, 3)
    kept = len(set(ids))
    dropped = in_count - kept
    repeated = out_count - kept
    parts = ["%d frames at %g fps (%.3g s) became %d frames at %g fps (%.3g s)." % (in_count, source_fps, in_count / source_fps, out_count, target_fps, seconds)]
    if dropped > 0:
        parts.append("%d frames were dropped." % dropped)
    if repeated > 0:
        parts.append("%d frames were repeated." % repeated)
    if dropped == 0 and repeated == 0:
        parts.append("Every frame was kept once.")
    if abs(source_fps - target_fps) < 1e-9:
        parts.append("Source and target rate are the same, so nothing changed.")
    return seconds, " ".join(parts)


class SYFrameRateConvert:
    DESCRIPTION = ("Changes the frame rate of a clip, keeping its length. It drops or repeats the nearest frames, no blending. "
                   "Also gives the new length in seconds and an info line with how many frames were dropped or repeated.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("images", "count", "fps", "seconds", "info")

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
        seconds, info = convert_info(images.shape[0], ids, source_fps, target_fps)
        return (images[ids], len(ids), float(target_fps), seconds, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameRateConvert", SYFrameRateConvert)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameRateConvert"] = "Frame Rate Convert SY"
