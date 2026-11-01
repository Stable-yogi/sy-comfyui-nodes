"""VRAM Estimate SY: a rough guess of the video memory a model needs, from its file size."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def estimate_vram(file_size_gb, overhead_factor, extra_models_gb=0.0):
    """Pure function. Returns (gb, text). It is only an estimate. extra_models_gb adds other files loaded at the same time."""
    size = float(file_size_gb)
    factor = float(overhead_factor)
    extra = float(extra_models_gb)
    if size <= 0:
        raise ValueError("file size must be more than 0 GB, got %s" % size)
    if factor < 1.0:
        raise ValueError("overhead factor must be at least 1.0, got %s" % factor)
    if extra < 0:
        raise ValueError("extra models size cannot be negative, got %s" % extra)
    gb = (size + extra) * factor
    if extra > 0:
        text = ("Estimate: about %.1f GB of VRAM (%.1f GB file + %.1f GB other models, x %.2f overhead). "
                "This is only a rough estimate. Picture size, batch size and other models change it." % (gb, size, extra, factor))
    else:
        text = ("Estimate: about %.1f GB of VRAM (%.1f GB file x %.2f overhead). "
                "This is only a rough estimate. Picture size, batch size and other models change it." % (gb, size, factor))
    return gb, text


def fit_verdict(vram_gb, card_gb):
    """Pure function. Returns (fits, text). With no card size (0) nothing is checked and fits is True."""
    card = float(card_gb)
    if card < 0:
        raise ValueError("card_vram_gb cannot be negative, got %s" % card)
    if card == 0:
        return True, "No card size given, so fit was not checked. Type your graphics card memory in card_vram_gb."
    spare = card - float(vram_gb)
    if spare >= 0:
        note = " That is tight: leave room for bigger pictures." if spare < 0.15 * card else ""
        return True, "Should fit: about %.1f GB needed of %g GB, %.1f GB spare.%s" % (vram_gb, card, spare, note)
    return False, ("Probably too big: about %.1f GB needed but the card has %g GB (%.1f GB short). "
                   "Try an fp8 or GGUF Q4/Q5 file of the same model, smaller pictures, or let ComfyUI offload to the CPU."
                   % (vram_gb, card, -spare))


class SYVramEstimate:
    DESCRIPTION = ("Rough estimate of the VRAM a model needs: file size times an overhead factor. Only a guide, not a measurement. "
                   "Add the size of other models loaded together and your card memory to get a plain fits or does not fit answer with tips.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("text", "vram_gb", "fits", "verdict")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "file_size_gb": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 1000.0, "step": 0.1, "tooltip": "Size of the model file in gigabytes."}),
            "overhead_factor": ("FLOAT", {"default": 1.3, "min": 1.0, "max": 5.0, "step": 0.05, "tooltip": "Extra room for work memory. 1.2 to 1.5 is common."}),
        },
            "optional": {
                "extra_models_gb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.1, "tooltip": "Size of other models in memory at the same time, such as the text encoder and VAE. For example 9."}),
                "card_vram_gb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 1.0, "tooltip": "Your graphics card memory in GB, for example 24. 0 turns the fit check off."}),
            }}

    def run(self, file_size_gb, overhead_factor, extra_models_gb=0.0, card_vram_gb=0.0):
        gb, text = estimate_vram(file_size_gb, overhead_factor, extra_models_gb)
        fits, verdict = fit_verdict(gb, card_vram_gb)
        return (text, gb, fits, verdict)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VramEstimate", SYVramEstimate)
NODE_DISPLAY_NAME_MAPPINGS["SYVramEstimate"] = "VRAM Estimate SY"
