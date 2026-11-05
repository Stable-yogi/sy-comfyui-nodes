"""H3 Skin Recipe SY: one node that loads the speed, people and detail LoRAs and gives the steps, sampler and scheduler for realistic skin."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
    from ._sy_sampler_names import sampler_names, scheduler_names
    from .sy_lora_trigger_words import read_sidecar_words
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
    from _sy_sampler_names import sampler_names, scheduler_names
    from sy_lora_trigger_words import read_sidecar_words

TIERS = ("fast", "balanced", "max skin")
AUTO = "auto"
NONE = "none"
SAMPLER = "euler"
SCHEDULER = "beta"
CFG = 1.0
MAX_SKIN_NOTE = "Max skin may follow the prompt a little less."


def base_name(name):
    """Pure function. 'folder/My_File.safetensors' -> 'my_file.safetensors' (lower case, no folder)."""
    return str(name or "").replace("\\", "/").split("/")[-1].lower()


def pick_auto(names, kind, tier):
    """Pure function. Picks the first LoRA name that fits kind ('turbo', 'people', 'detail') and tier. Returns 'none' when nothing fits."""
    if kind not in ("turbo", "people", "detail"):
        raise ValueError("kind must be turbo, people or detail, not %r" % (kind,))
    if tier not in TIERS:
        raise ValueError("tier must be one of: %s" % ", ".join(TIERS))
    for name in names or []:
        b = base_name(name)
        if kind == "turbo":
            step_word = "4step" if tier == "fast" else "8step"
            ok = "turbo" in b and step_word in b
        elif kind == "people":
            ok = "realism" in b or "people" in b
        else:
            ok = "ema" in b
        if ok:
            return name
    return NONE


def tier_plan(tier, people_strength=0.75, steps_override=0):
    """Pure function. Returns a dict: steps, people_strength, use_detail, sampler, scheduler, cfg, note."""
    if tier not in TIERS:
        raise ValueError("tier must be one of: %s" % ", ".join(TIERS))
    if steps_override < 0:
        raise ValueError("steps_override must be 0 (use the tier) or more")
    if tier == "fast":
        steps, strength, detail, note = 4, 0.6, False, ""
    elif tier == "balanced":
        steps, strength, detail, note = 8, float(people_strength), False, ""
    else:
        steps, strength, detail, note = 10, float(people_strength), True, MAX_SKIN_NOTE
    if steps_override > 0:
        steps = int(steps_override)
    return {"steps": steps, "people_strength": strength, "use_detail": detail,
            "sampler": SAMPLER, "scheduler": SCHEDULER, "cfg": CFG, "note": note}


def resolve_loras(names, tier, turbo, people, detail, plan):
    """Pure function. Turns auto/none/name picks into the final list of (kind, name_or_none). Detail is only used by max skin."""
    picks = {"turbo": turbo, "people": people, "detail": detail}
    out = []
    for kind in ("turbo", "people", "detail"):
        choice = picks[kind]
        if kind == "detail" and not plan["use_detail"]:
            out.append((kind, NONE))
            continue
        if choice == AUTO:
            choice = pick_auto(names, kind, tier)
        if choice in (None, "", NONE, NONE_NAME):
            choice = NONE
        elif choice not in (names or []):
            raise ValueError("LoRA file %r was not found in the ComfyUI loras folder. Pick another file, or choose auto or none." % choice)
        out.append((kind, choice))
    return out


def info_text(tier, loras, strengths, steps, note):
    """Pure function. Plain words: tier, each LoRA with its strength (or none), steps."""
    labels = {"turbo": "speed", "people": "people", "detail": "detail"}
    parts = []
    for kind, name in loras:
        if name == NONE:
            parts.append("%s LoRA: none" % labels[kind])
        else:
            parts.append("%s LoRA: %s at %s" % (labels[kind], name, fmt_strength(strengths[kind])))
    text = "Tier %s. %s. Steps %d, sampler %s, scheduler %s, cfg %s." % (
        tier, ". ".join(parts), steps, SAMPLER, SCHEDULER, fmt_strength(CFG))
    return text + ((" " + note) if note else "")


def _lora_choices():
    return [AUTO, NONE] + list_names("loras")


class SYH3SkinRecipe:
    DESCRIPTION = ("Sets up realistic skin for the H3 video model in one step. Loads the speed, people and detail LoRAs (auto-picked "
                   "by name or chosen by you) and gives you the steps, sampler, scheduler and cfg to feed your sampler.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    # sampler_name / scheduler are plain STRING. The last two outputs carry the same values typed as ComfyUI's own
    # sampler and scheduler lists, so they can be wired straight into a sampler-select combo input.
    RETURN_TYPES = ("MODEL", "INT", "STRING", "STRING", "FLOAT", "STRING", "STRING", sampler_names(), scheduler_names())
    RETURN_NAMES = ("model", "steps", "sampler_name", "scheduler", "cfg", "trigger_text", "info", "sampler_combo", "scheduler_combo")

    @classmethod
    def INPUT_TYPES(cls):
        choices = _lora_choices()
        return {"required": {
            "model": ("MODEL", {"tooltip": "The video model to put the LoRAs on."}),
            "tier": (list(TIERS), {"default": "balanced", "tooltip": "fast = 4 steps, balanced = 8 steps, max skin = 10 steps plus the detail LoRA."}),
            "turbo_lora": (choices, {"default": AUTO, "tooltip": "The speed LoRA. auto finds a turbo LoRA with the right step count in its name."}),
            "people_lora": (choices, {"default": AUTO, "tooltip": "The people LoRA. auto finds the first name with realism or people in it."}),
            "detail_lora": (choices, {"default": AUTO, "tooltip": "The detail LoRA, used by max skin only. auto finds the first name with ema in it."}),
            "people_strength": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.5, "step": 0.05, "tooltip": "How strong the people LoRA is. Fast always uses 0.6."}),
            "turbo_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "How strong the speed LoRA is."}),
            "detail_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "How strong the detail LoRA is (max skin only)."}),
            "steps_override": ("INT", {"default": 0, "min": 0, "max": 60, "tooltip": "0 uses the step count of the tier. Anything above 0 is used instead."}),
        }}

    def run(self, model, tier="balanced", turbo_lora=AUTO, people_lora=AUTO, detail_lora=AUTO,
            people_strength=0.75, turbo_strength=1.0, detail_strength=1.0, steps_override=0):
        names = list_names("loras")
        plan = tier_plan(tier, people_strength, steps_override)
        loras = resolve_loras(names, tier, turbo_lora, people_lora, detail_lora, plan)
        strengths = {"turbo": float(turbo_strength), "people": plan["people_strength"], "detail": float(detail_strength)}
        trigger_text = ""
        for kind, name in loras:
            if name == NONE:
                continue
            path = find_file("loras", name)
            if kind == "people":
                trigger_text = ", ".join(read_sidecar_words(path))
            if strengths[kind] == 0:
                continue
            model = self._apply(model, name, path, strengths[kind])
        info = info_text(tier, loras, strengths, plan["steps"], plan["note"])
        return (model, plan["steps"], plan["sampler"], plan["scheduler"], plan["cfg"], trigger_text, info,
                plan["sampler"], plan["scheduler"])

    @staticmethod
    def _apply(model, name, path, strength):
        import comfy.sd
        import comfy.utils
        try:
            data = comfy.utils.load_torch_file(path, safe_load=True)
            model, _ = comfy.sd.load_lora_for_models(model, None, data, strength, 0)
        except Exception as e:
            raise ValueError("could not apply LoRA %r: %s" % (name, e))
        return model


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3SkinRecipe", SYH3SkinRecipe)
NODE_DISPLAY_NAME_MAPPINGS["SYH3SkinRecipe"] = "H3 Skin Recipe SY"
