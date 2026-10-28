"""Model Preset Bundle SY: pick a model family and get sensible starting settings for it."""
try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names, pick_valid
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names, pick_valid

# name: (steps, cfg, sampler, scheduler, width, height, note). Starting points only, not rules.
PRESETS = {
    "Krea 2": (28, 3.5, "euler", "simple", 1024, 1024, "Starting point for Krea 2 pictures. Raise steps for fine detail."),
    "Qwen Image 2.1": (30, 4.0, "euler", "simple", 1328, 1328, "Starting point for Qwen Image 2.1. Good with long, plain-sentence prompts."),
    "Flux": (20, 1.0, "euler", "simple", 1024, 1024, "Flux uses its own built-in guidance, so cfg stays at 1."),
    "SDXL (old)": (30, 7.0, "dpmpp_2m", "karras", 1024, 1024, "Classic SDXL settings. Keep sizes near one megapixel."),
    "Z-Image": (8, 1.0, "res_multistep", "simple", 1024, 1024, "Z-Image turbo style: few steps, cfg 1."),
    "Wan 2.2 video": (20, 3.5, "uni_pc", "simple", 832, 480, "Wan 2.2 video starting point. Frame count is set elsewhere."),
    "LTX video": (30, 3.0, "euler", "simple", 768, 512, "LTX video starting point. Multiples of 32 work best for size."),
    "H3": (25, 4.0, "euler", "simple", 1024, 1024, "General starting point for H3. Adjust after a first test."),
    "MiniMax image": (30, 4.0, "euler", "normal", 1024, 1024, "General starting point for MiniMax pictures."),
    "MiniMax video": (30, 5.0, "euler", "normal", 1280, 720, "General starting point for MiniMax video, 16:9."),
    "HunyuanVideo": (30, 1.0, "euler", "simple", 848, 480, "HunyuanVideo uses embedded guidance, so cfg stays at 1."),
    "Qwen edit": (20, 4.0, "euler", "simple", 1024, 1024, "Starting point for Qwen picture editing."),
    "SD 1.5": (25, 7.0, "dpmpp_2m", "karras", 512, 512, "Classic SD 1.5 settings. Stay near 512 pixels, then upscale."),
    "Generic": (20, 5.0, "euler", "normal", 1024, 1024, "Neutral starting point for any model."),
}

SAMPLER_FALLBACKS = ("euler", "dpmpp_2m", "uni_pc")
SCHEDULER_FALLBACKS = ("simple", "normal", "karras")


def preset_names():
    return list(PRESETS.keys())


def get_preset(name, valid_samplers=None, valid_schedulers=None):
    """Pure function. Returns a dict for the preset. Unknown sampler/scheduler names fall back to valid ones."""
    if name not in PRESETS:
        raise ValueError("unknown preset %r. Pick one of: %s" % (name, ", ".join(PRESETS)))
    steps, cfg, sampler, scheduler, width, height, note = PRESETS[name]
    if valid_samplers is not None:
        sampler = pick_valid(sampler, list(valid_samplers), SAMPLER_FALLBACKS)
    if valid_schedulers is not None:
        scheduler = pick_valid(scheduler, list(valid_schedulers), SCHEDULER_FALLBACKS)
    return {"steps": steps, "cfg": cfg, "sampler_name": sampler, "scheduler": scheduler,
            "width": width, "height": height, "note": note}


class SYModelPresetBundle:
    DESCRIPTION = "Pick a model family and get its usual steps, cfg, sampler, scheduler, size and a short note. These are starting points."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("steps", "cfg", "sampler_name", "scheduler", "width", "height", "note")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"preset": (preset_names(), {"tooltip": "The model family whose usual settings you want."})}}

    def run(self, preset):
        p = get_preset(preset, sampler_names(), scheduler_names())
        return (p["steps"], p["cfg"], p["sampler_name"], p["scheduler"], p["width"], p["height"], p["note"])


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ModelPresetBundle", SYModelPresetBundle)
NODE_DISPLAY_NAME_MAPPINGS["SYModelPresetBundle"] = "Model Preset Bundle SY"
