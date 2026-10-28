"""VRAM Estimate SY: a rough guess of the video memory a model needs, from its file size."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def estimate_vram(file_size_gb, overhead_factor):
    """Pure function. Returns (gb, text). It is only an estimate."""
    size = float(file_size_gb)
    factor = float(overhead_factor)
    if size <= 0:
        raise ValueError("file size must be more than 0 GB, got %s" % size)
    if factor < 1.0:
        raise ValueError("overhead factor must be at least 1.0, got %s" % factor)
    gb = size * factor
    text = ("Estimate: about %.1f GB of VRAM (%.1f GB file x %.2f overhead). "
            "This is only a rough estimate. Picture size, batch size and other models change it." % (gb, size, factor))
    return gb, text


class SYVramEstimate:
    DESCRIPTION = "Rough estimate of the VRAM a model needs: file size times an overhead factor. Only a guide, not a measurement."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT")
    RETURN_NAMES = ("text", "vram_gb")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "file_size_gb": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 1000.0, "step": 0.1, "tooltip": "Size of the model file in gigabytes."}),
            "overhead_factor": ("FLOAT", {"default": 1.3, "min": 1.0, "max": 5.0, "step": 0.05, "tooltip": "Extra room for work memory. 1.2 to 1.5 is common."}),
        }}

    def run(self, file_size_gb, overhead_factor):
        gb, text = estimate_vram(file_size_gb, overhead_factor)
        return (text, gb)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VramEstimate", SYVramEstimate)
NODE_DISPLAY_NAME_MAPPINGS["SYVramEstimate"] = "VRAM Estimate SY"
