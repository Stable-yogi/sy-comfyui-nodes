"""Sampler Settings SY and Sampler Settings Unpack SY: bundle steps, cfg, sampler and scheduler into one wire, and split them again."""
try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names

KEYS = ("steps", "cfg", "sampler_name", "scheduler")


def build_settings(steps, cfg, sampler_name, scheduler, valid_samplers=None, valid_schedulers=None):
    """Pure function. Checks the values and returns the settings dict."""
    steps = int(steps)
    cfg = float(cfg)
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
    return {"steps": steps, "cfg": cfg, "sampler_name": str(sampler_name), "scheduler": str(scheduler)}


def unpack_settings(settings):
    """Pure function. Returns (steps, cfg, sampler_name, scheduler) from a settings dict."""
    if not isinstance(settings, dict):
        raise ValueError("settings must come from a Sampler Settings node")
    missing = [k for k in KEYS if k not in settings]
    if missing:
        raise ValueError("settings is missing: %s" % ", ".join(missing))
    return (int(settings["steps"]), float(settings["cfg"]), str(settings["sampler_name"]), str(settings["scheduler"]))


class SYSamplerSettings:
    DESCRIPTION = "Bundles steps, cfg, sampler and scheduler into one wire so a workflow stays tidy."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("SY_SAMPLER_SETTINGS",)
    RETURN_NAMES = ("settings",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "tooltip": "How many denoising steps to run."}),
            "cfg": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "How strongly the prompt is followed."}),
            "sampler_name": (sampler_names(), {"tooltip": "The sampling method."}),
            "scheduler": (scheduler_names(), {"tooltip": "How the noise levels are spaced over the steps."}),
        }}

    def run(self, steps, cfg, sampler_name, scheduler):
        return (build_settings(steps, cfg, sampler_name, scheduler, sampler_names(), scheduler_names()),)


class SYSamplerSettingsUnpack:
    DESCRIPTION = "Splits a sampler settings bundle back into steps, cfg, sampler and scheduler."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("steps", "cfg", "sampler_name", "scheduler")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"settings": ("SY_SAMPLER_SETTINGS", {"tooltip": "The bundle from a Sampler Settings node."})}}

    def run(self, settings):
        return unpack_settings(settings)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SamplerSettings", SYSamplerSettings)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SamplerSettingsUnpack", SYSamplerSettingsUnpack)
NODE_DISPLAY_NAME_MAPPINGS["SYSamplerSettings"] = "Sampler Settings SY"
NODE_DISPLAY_NAME_MAPPINGS["SYSamplerSettingsUnpack"] = "Sampler Settings Unpack SY"
