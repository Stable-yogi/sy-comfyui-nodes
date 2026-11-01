"""Sampler Settings SY and Sampler Settings Unpack SY: bundle steps, cfg, sampler and scheduler into one wire, and split them again."""
try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names

KEYS = ("steps", "cfg", "sampler_name", "scheduler")


def build_settings(steps, cfg, sampler_name, scheduler, valid_samplers=None, valid_schedulers=None, denoise=1.0):
    """Pure function. Checks the values and returns the settings dict."""
    steps = int(steps)
    cfg = float(cfg)
    denoise = float(denoise)
    if not 0.0 <= denoise <= 1.0:  # also rejects nan
        raise ValueError("denoise must be between 0 and 1, got %s" % denoise)
    if steps < 1:
        raise ValueError("steps must be at least 1, got %d" % steps)
    if cfg < 0:
        raise ValueError("cfg must be 0 or more, got %s" % cfg)
    if not sampler_name:
        raise ValueError("pick a sampler")
    if not scheduler:
        raise ValueError("pick a scheduler")
    if valid_samplers is not None and sampler_name not in valid_samplers:
        raise ValueError("unknown sampler %r. Pick one from the list." % sampler_name)
    if valid_schedulers is not None and scheduler not in valid_schedulers:
        raise ValueError("unknown scheduler %r. Pick one from the list." % scheduler)
    settings = {"steps": steps, "cfg": cfg, "sampler_name": str(sampler_name), "scheduler": str(scheduler)}
    if denoise != 1.0:  # kept out of the bundle at 1 so older bundles and new ones look the same
        settings["denoise"] = denoise
    return settings


def settings_hints(settings):
    """Pure function. Plain tips for the values in a settings dict (a list of short sentences, may be empty)."""
    steps, cfg, sampler, scheduler = int(settings["steps"]), float(settings["cfg"]), str(settings["sampler_name"]), str(settings["scheduler"])
    denoise = float(settings.get("denoise", 1.0))
    tips = []
    if cfg == 0:
        tips.append("cfg 0 ignores your prompt completely.")
    elif cfg == 1:
        tips.append("cfg 1 skips the negative prompt, which is faster. Right for turbo, flux and distilled models.")
    elif cfg > 12:
        tips.append("cfg %g is high and can burn the colours. 3 to 8 is usual." % cfg)
    if steps <= 6 and cfg > 2:
        tips.append("Only %d steps with cfg %g: that suits turbo or lightning models, not a normal model." % (steps, cfg))
    if steps > 100:
        tips.append("%d steps is a lot. Most models stop improving after 30 to 50." % steps)
    if "ancestral" in sampler or sampler.endswith("_a") or "sde" in sampler:
        tips.append("%s adds fresh noise each step, so the picture keeps changing as steps grow." % sampler)
    if denoise < 1.0:
        tips.append("denoise %g keeps part of the input picture (use 1 for a new picture)." % denoise)
    return tips


def info_text(settings):
    """Pure function. One line with the values, then any tips."""
    steps, cfg, sampler, scheduler = unpack_settings(settings)[:4]
    line = "%d steps, cfg %g, %s / %s, denoise %g" % (steps, cfg, sampler, scheduler, float(settings.get("denoise", 1.0)))
    tips = settings_hints(settings)
    return line + ("\n" + "\n".join(tips) if tips else "")


def unpack_settings(settings):
    """Pure function. Returns (steps, cfg, sampler_name, scheduler) from a settings dict."""
    if not isinstance(settings, dict):
        raise ValueError("settings must come from a Sampler Settings node")
    missing = [k for k in KEYS if k not in settings]
    if missing:
        raise ValueError("settings is missing: %s" % ", ".join(missing))
    return (int(settings["steps"]), float(settings["cfg"]), str(settings["sampler_name"]), str(settings["scheduler"]))


class SYSamplerSettings:
    DESCRIPTION = ("Bundles steps, cfg, sampler, scheduler and denoise into one wire so a workflow stays tidy. "
                   "The info output shows the values in one line and warns about common mistakes, such as cfg 0 or too many steps.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("SY_SAMPLER_SETTINGS", "STRING")
    RETURN_NAMES = ("settings", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "tooltip": "How many denoising steps to run."}),
            "cfg": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "How strongly the prompt is followed."}),
            "sampler_name": (sampler_names(), {"tooltip": "The sampling method."}),
            "scheduler": (scheduler_names(), {"tooltip": "How the noise levels are spaced over the steps."}),
        },
            "optional": {
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "1 makes a new picture. Lower keeps part of the input picture, for example 0.6."}),
            }}

    def run(self, steps, cfg, sampler_name, scheduler, denoise=1.0):
        settings = build_settings(steps, cfg, sampler_name, scheduler, sampler_names(), scheduler_names(), denoise)
        return (settings, info_text(settings))


class SYSamplerSettingsUnpack:
    DESCRIPTION = "Splits a sampler settings bundle back into steps, cfg, sampler, scheduler and denoise. Bundles made before denoise existed give denoise 1."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING", "STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("steps", "cfg", "sampler_name", "scheduler", "denoise", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"settings": ("SY_SAMPLER_SETTINGS", {"tooltip": "The bundle from a Sampler Settings node."})}}

    def run(self, settings):
        return unpack_settings(settings) + (float(settings.get("denoise", 1.0)), info_text(settings))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SamplerSettings", SYSamplerSettings)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SamplerSettingsUnpack", SYSamplerSettingsUnpack)
NODE_DISPLAY_NAME_MAPPINGS["SYSamplerSettings"] = "Sampler Settings SY"
NODE_DISPLAY_NAME_MAPPINGS["SYSamplerSettingsUnpack"] = "Sampler Settings Unpack SY"
