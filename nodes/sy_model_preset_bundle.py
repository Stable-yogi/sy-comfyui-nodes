"""Model Preset Bundle SY: pick a model family and get sensible starting settings for it."""
try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names, pick_valid
    from ._sy_a1_sizes import ASPECTS, fit_aspect, snap_value, ratio_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names, pick_valid
    from _sy_a1_sizes import ASPECTS, fit_aspect, snap_value, ratio_text

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


def size_multiple(name):
    """Pure function. The size step a preset wants: 32 for LTX video, 16 for the others."""
    return 32 if name == "LTX video" else 16


def preset_size(name, aspect="preset"):
    """Pure function. (width, height) of a preset. With an aspect (like '16:9') the picture keeps about the same number
    of pixels (the memory budget of the preset) in that shape, snapped to the size step of the preset."""
    if name not in PRESETS:
        raise ValueError("unknown preset %r. Pick one of: %s" % (name, ", ".join(PRESETS)))
    if aspect not in ASPECTS:
        raise ValueError("unknown aspect %r. Pick one of: %s" % (aspect, ", ".join(ASPECTS)))
    width, height = PRESETS[name][4], PRESETS[name][5]
    if ASPECTS[aspect] is None:
        return width, height
    step = size_multiple(name)
    w, h = fit_aspect(width * height, ASPECTS[aspect][0], ASPECTS[aspect][1])
    return snap_value(w, step, "nearest", minimum=step), snap_value(h, step, "nearest", minimum=step)


def preset_info(name, p, aspect="preset"):
    """Pure function. One readable summary of what the node gives."""
    mp = p["width"] * p["height"] / 1_000_000
    size = "%dx%d (%.2f MP, %s)" % (p["width"], p["height"], mp, ratio_text(p["width"], p["height"]))
    if aspect != "preset":
        size += ", reshaped to %s from the preset size" % aspect
    return "%s: %d steps, cfg %g, %s / %s, %s. %s" % (name, p["steps"], p["cfg"], p["sampler_name"], p["scheduler"], size, p["note"])


class SYModelPresetBundle:
    DESCRIPTION = ("Pick a model family and get its usual steps, cfg, sampler, scheduler, size and a short note. These are starting points. "
                   "Adds an aspect choice (the preset's pixel budget in another shape, such as 16:9 or 9:16, snapped to a size the model likes) "
                   "and a one-line info text.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING", "STRING", "INT", "INT", "STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("steps", "cfg", "sampler_name", "scheduler", "width", "height", "note", "megapixels", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"preset": (preset_names(), {"tooltip": "The model family whose usual settings you want."})},
            "optional": {"aspect": (list(ASPECTS), {"default": "preset", "tooltip": "preset = the preset's own size. Or a shape like 16:9: same pixel budget, new shape."})},
        }

    def run(self, preset, aspect="preset"):
        p = get_preset(preset, sampler_names(), scheduler_names())
        p["width"], p["height"] = preset_size(preset, aspect)
        mp = p["width"] * p["height"] / 1_000_000
        return (p["steps"], p["cfg"], p["sampler_name"], p["scheduler"], p["width"], p["height"], p["note"], mp, preset_info(preset, p, aspect))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ModelPresetBundle", SYModelPresetBundle)
NODE_DISPLAY_NAME_MAPPINGS["SYModelPresetBundle"] = "Model Preset Bundle SY"
