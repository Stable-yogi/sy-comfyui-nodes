"""LoRA SY: one LoRA with an on/off switch, separate model and text strengths, and its trigger words added to your prompt."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
    from .sy_lora_trigger_words import read_sidecar_words
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
    from sy_lora_trigger_words import read_sidecar_words

POSITIONS = ["Before the prompt", "After the prompt"]


def plan_lora(name, enabled, strength_model, strength_clip, has_clip):
    """Pure function. Returns (apply, model_strength, clip_strength, reason). Raises ValueError on strengths outside -20..20."""
    sm, sc = float(strength_model), float(strength_clip)
    for s in (sm, sc):
        if s < -20 or s > 20:
            raise ValueError("LoRA strength must be between -20 and 20, got %s" % s)
    if not enabled:
        return False, sm, sc, "switched off"
    if not name or name == NONE_NAME:
        return False, sm, sc, "no LoRA picked"
    if sm == 0 and (sc == 0 or not has_clip):
        return False, sm, sc, "strength is 0"
    return True, sm, (sc if has_clip else 0.0), ""


def merge_prompt(prompt, words, position):
    """Pure function. Adds trigger words before or after the prompt, skipping words the prompt already has."""
    if position not in POSITIONS:
        raise ValueError("position must be one of %s, got %r" % (POSITIONS, position))
    base = str(prompt or "").strip()
    have = base.lower()
    fresh = []
    for w in words:
        w = " ".join(str(w).split())
        if w and w.lower() not in have and w.lower() not in [f.lower() for f in fresh]:
            fresh.append(w)
    if not fresh:
        return base
    joined = ", ".join(fresh)
    if not base:
        return joined
    return (joined + ", " + base) if position == POSITIONS[0] else (base + ", " + joined)


def info_text(name, applied, sm, sc, reason, words):
    """Pure function. One short report."""
    if not applied:
        head = "LoRA not applied (%s)" % reason
    else:
        head = "%s (model %s, text %s)" % (name, fmt_strength(sm), fmt_strength(sc))
    return head + ("; trigger words: " + ", ".join(words) if words else "")


class SYLora:
    DESCRIPTION = ("Applies one LoRA with an on/off switch (no bypassing), separate strengths for the picture model and the text "
                   "encoder, and adds the LoRA's trigger words to your prompt for you. Chain several for a stack.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "prompt", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model to add the LoRA to."}),
                "lora": ([NONE_NAME] + list_names("loras"), {"tooltip": "The LoRA file. None = nothing is applied."}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off: everything passes through unchanged, no bypass needed."}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.05, "tooltip": "Strength on the picture model."}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.05, "tooltip": "Strength on the text encoder. Ignored when no clip is connected."}),
                "add_trigger_words": ("BOOLEAN", {"default": True, "tooltip": "On: reads the words from the .json or .txt file next to the LoRA and adds them to the prompt."}),
                "position": (POSITIONS, {"default": POSITIONS[0], "tooltip": "Where the trigger words go."}),
            },
            "optional": {
                "clip": ("CLIP", {"tooltip": "The text encoder. Leave empty for models that need no clip LoRA."}),
                "prompt": ("STRING", {"forceInput": True, "tooltip": "Your prompt text. The trigger words are added to it."}),
            },
        }

    def run(self, model, lora, enabled, strength_model, strength_clip, add_trigger_words, position, clip=None, prompt=""):
        apply, sm, sc, reason = plan_lora(lora, enabled, strength_model, strength_clip, clip is not None)
        words = []
        if apply:
            path = find_file("loras", lora)
            if add_trigger_words:
                words = read_sidecar_words(path)
            import comfy.sd
            import comfy.utils
            try:
                data = comfy.utils.load_torch_file(path, safe_load=True)
                model, clip = comfy.sd.load_lora_for_models(model, clip, data, sm, sc)
            except Exception as e:
                raise ValueError("could not apply LoRA %r: %s" % (lora, e))
        out_prompt = merge_prompt(prompt, words, position) if (apply and add_trigger_words) else str(prompt or "")
        return (model, clip, out_prompt, info_text(lora, apply, sm, sc, reason, words))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Lora", SYLora)
NODE_DISPLAY_NAME_MAPPINGS["SYLora"] = "LoRA SY"
