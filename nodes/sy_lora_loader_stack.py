"""Lora Loader Stack SY: applies up to 4 LoRAs to a model and clip in one node, with an off switch and trigger word hints."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
    from ._sy_a1_files import st_metadata, lora_hints, check_size
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
    from _sy_a1_files import st_metadata, lora_hints, check_size

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


def check_clip_scale(clip_scale):
    """Pure function. The clip strength is the LoRA strength times this number. 0 leaves the text encoder alone."""
    v = float(clip_scale)
    if not (0.0 <= v <= 4.0):  # also rejects nan
        raise ValueError("clip_scale must be between 0 and 4, got %s" % clip_scale)
    return v


def duplicate_names(plan):
    """Pure function. LoRA names used in more than one slot."""
    seen, dup = set(), []
    for name, _ in plan:
        if name in seen and name not in dup:
            dup.append(name)
        seen.add(name)
    return dup


def hint_lines(hints_by_name):
    """Pure function. hints_by_name = {lora: lora_hints(...)} -> (info_text, trigger_text)."""
    info, trig = [], []
    for name, h in hints_by_name.items():
        if h.get("base"):
            info.append("%s was trained for: %s" % (name, h["base"]))
        words = h.get("triggers") or h.get("tags") or []
        if words:
            label = "trigger words" if h.get("triggers") else "most used training tags"
            trig.append("%s (%s): %s" % (name, label, ", ".join(words)))
    return "\n".join(info), "\n".join(trig)


def build_info(plan, clip_scale, bypass, hints_text="", dup=()):
    """Pure function. The info text of one run."""
    if bypass:
        return "Bypassed: the model and clip were passed on without any LoRA."
    lines = [summarize(plan)]
    if plan and clip_scale != 1.0:
        lines.append("Clip strength = LoRA strength x %s." % fmt_strength(clip_scale))
    if hints_text:
        lines.append(hints_text)
    for name in dup:
        lines.append("Warning: %s is used in more than one slot; its effect adds up." % name)
    return "\n".join(lines)


class SYLoraLoaderStack:
    DESCRIPTION = ("Applies up to 4 LoRAs to the model and clip. Slots on None or with strength 0 are skipped. Adds: a bypass "
                   "switch (compare with and without LoRAs without rewiring), a clip_scale (0 = change only the model), "
                   "trigger words or common training tags read from the LoRA files, and a warning for a LoRA used twice.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "applied", "info", "trigger_words")

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
        return {
            "required": req,
            "optional": {
                "bypass": ("BOOLEAN", {"default": False, "tooltip": "On = pass model and clip on without any LoRA. Handy to compare."}),
                "clip_scale": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 4.0, "step": 0.05, "tooltip": "Clip strength = strength x this. 1 = same as before, 0 = model only."}),
            },
        }

    def run(self, model, clip, bypass=False, clip_scale=1.0, **kw):
        scale = check_clip_scale(clip_scale)
        plan = plan_loras([(kw["lora_%d" % i], kw["strength_%d" % i]) for i in range(1, SLOTS + 1)])
        if bypass:
            return (model, clip, "No LoRAs applied.", build_info(plan, scale, True), "")
        # Check every file first so a typo fails before any patching starts.
        paths = [(name, s, find_file("loras", name)) for name, s in plan]
        hints = {}
        if paths:
            import os
            import comfy.sd
            import comfy.utils
            for name, _s, path in paths:
                check_size(name, os.path.getsize(path))
                hints[name] = lora_hints(st_metadata(path))
        for name, s, path in paths:
            try:
                lora = comfy.utils.load_torch_file(path, safe_load=True)
                model, clip = comfy.sd.load_lora_for_models(model, clip, lora, s, s * scale)
            except Exception as e:
                raise ValueError("could not apply LoRA %r: %s" % (name, e))
        info_hints, trig = hint_lines(hints)
        return (model, clip, summarize(plan), build_info(plan, scale, False, info_hints, duplicate_names(plan)), trig)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraLoaderStack", SYLoraLoaderStack)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraLoaderStack"] = "Lora Loader Stack SY"
