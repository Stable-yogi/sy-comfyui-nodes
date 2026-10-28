"""Lora Loader Stack SY: applies up to 4 LoRAs to a model and clip in one node."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, fmt_strength, NONE_NAME

SLOTS = 4


def plan_loras(pairs):
    """Pure function. pairs = [(name, strength)]. Skips 'None' and strength 0. Raises ValueError on bad values."""
    plan = []
    for name, strength in pairs:
        s = float(strength)
        if s < -20 or s > 20:
            raise ValueError("LoRA strength must be between -20 and 20, got %s" % s)
        if not name or name == NONE_NAME or s == 0:
            continue
        plan.append((name, s))
    return plan


def summarize(plan):
    """Pure function. One line per applied LoRA."""
    if not plan:
        return "No LoRAs applied."
    return "\n".join("%s (strength %s)" % (n, fmt_strength(s)) for n, s in plan)


class SYLoraLoaderStack:
    DESCRIPTION = "Applies up to 4 LoRAs to the model and clip. Slots on None or with strength 0 are skipped."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "STRING")
    RETURN_NAMES = ("model", "clip", "applied")

    @classmethod
    def INPUT_TYPES(cls):
        names = [NONE_NAME] + list_names("loras")
        req = {
            "model": ("MODEL", {"tooltip": "The model to add LoRAs to."}),
            "clip": ("CLIP", {"tooltip": "The text encoder (clip) to add LoRAs to."}),
        }
        for i in range(1, SLOTS + 1):
            req["lora_%d" % i] = (names, {"tooltip": "LoRA for slot %d. Leave on None to skip it." % i})
            req["strength_%d" % i] = ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.05, "tooltip": "Strength for slot %d, used for model and clip. 0 skips it." % i})
        return {"required": req}

    def run(self, model, clip, **kw):
        plan = plan_loras([(kw["lora_%d" % i], kw["strength_%d" % i]) for i in range(1, SLOTS + 1)])
        # Check every file first so a typo fails before any patching starts.
        paths = [(name, s, find_file("loras", name)) for name, s in plan]
        if paths:
            import comfy.sd
            import comfy.utils
        for name, s, path in paths:
            try:
                lora = comfy.utils.load_torch_file(path, safe_load=True)
                model, clip = comfy.sd.load_lora_for_models(model, clip, lora, s, s)
            except Exception as e:
                raise ValueError("could not apply LoRA %r: %s" % (name, e))
        return (model, clip, summarize(plan))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraLoaderStack", SYLoraLoaderStack)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraLoaderStack"] = "Lora Loader Stack SY"
