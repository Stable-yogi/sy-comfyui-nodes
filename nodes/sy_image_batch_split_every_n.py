"""Image Batch Split Every N SY: cuts a batch into slices of N and outputs one slice."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_videoframes import split_range
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_videoframes import split_range


class SYImageBatchSplitEveryN:
    DESCRIPTION = "Cuts a batch into slices of N pictures and gives you slice number K. The last slice may be shorter."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("images", "parts_total", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to cut."}),
                "part_size": ("INT", {"default": 16, "min": 1, "max": 100000, "tooltip": "How many pictures go in each slice."}),
                "part": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which slice to output, counting from 0."}),
            }
        }

    def run(self, images, part_size, part):
        check_shape(images.shape)
        start, end, parts_total = split_range(images.shape[0], part_size, part)
        return (images[start:end], parts_total, end - start)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageBatchSplitEveryN", SYImageBatchSplitEveryN)
NODE_DISPLAY_NAME_MAPPINGS["SYImageBatchSplitEveryN"] = "Image Batch Split Every N SY"
