"""LoRA Strength Sweep SY: one LoRA, several strengths at once. Gives a list of models (one per strength), so the sampler
after it runs once per strength and you can compare them side by side. Strength 0 = the picture without the LoRA.
It also gives one main model at the strength you pick, for the rest of the workflow, so the LoRA is picked only once."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, fmt_strength, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, fmt_strength, NONE_NAME

MAX_STRENGTHS = 12


def parse_strengths(text):
    """Pure function. '0, 0.6, 0.8, 1.0' (commas, spaces or new lines) -> [0.0, 0.6, 0.8, 1.0]. Order is kept."""
    parts = [p for p in str(text or "").replace(";", ",").replace("\n", ",").replace(" ", ",").split(",") if p.strip()]
    if not parts:
        raise ValueError("type at least one strength, for example 0, 0.6, 0.8, 1.0")
    out = []
    for p in parts:
        try:
            v = float(p)
        except ValueError:
            raise ValueError("%r is not a number; type strengths like 0, 0.6, 0.8, 1.0" % p.strip())
        if v != v or v < -20 or v > 20:
            raise ValueError("LoRA strength must be between -20 and 20, got %s" % p.strip())
        out.append(v)
    if len(out) > MAX_STRENGTHS:
        raise ValueError("at most %d strengths at once (you typed %d); each one is a full picture" % (MAX_STRENGTHS, len(out)))
    return out


def strength_label(value):
    """Pure function. Caption for one strength: 0 says 'no LoRA'."""
    return "no LoRA" if value == 0 else "LoRA " + fmt_strength(value)


def sweep_info(name, strengths, main):
    """Pure function. One short report."""
    return "%s: %d strengths (%s); main model at %s" % (name, len(strengths), ", ".join(fmt_strength(s) for s in strengths),
                                                        fmt_strength(main))


class SYLoraStrengthSweep:
    DESCRIPTION = ("One LoRA at several strengths in one go. The models output is a list, so the sampler after it makes one "
                   "picture per strength (same seed, fair compare). Strength 0 shows the picture without the LoRA. "
                   "main_model is the LoRA at one strength you pick, for the rest of the workflow.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "MODEL", "STRING", "STRING")
    RETURN_NAMES = ("models", "main_model", "labels", "info")
    OUTPUT_IS_LIST = (True, False, False, False)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model to add the LoRA to."}),
                "lora": ([NONE_NAME] + list_names("loras"), {"tooltip": "The LoRA file. None = every output is the plain model."}),
                "strengths": ("STRING", {"default": "0, 0.6, 0.8, 1.0", "tooltip": "Strengths to compare, with commas. 0 = without the LoRA. At most 12."}),
                "main_strength": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.05, "tooltip": "Strength of main_model."}),
            },
        }

    def run(self, model, lora, strengths, main_strength):
        values = parse_strengths(strengths)
        labels = "\n".join(strength_label(v) for v in values)
        if not lora or lora == NONE_NAME:
            return ([model] * len(values), model, labels, "no LoRA picked: every output is the plain model")
        import comfy.sd
        import comfy.utils
        path = find_file("loras", lora)
        try:
            data = comfy.utils.load_torch_file(path, safe_load=True)
        except Exception as e:
            raise ValueError("could not read LoRA %r: %s" % (lora, e))

        def at(s):
            if s == 0:
                return model
            try:
                return comfy.sd.load_lora_for_models(model, None, data, s, 0.0)[0]
            except Exception as e:
                raise ValueError("could not apply LoRA %r at %s: %s" % (lora, fmt_strength(s), e))
        models = [at(v) for v in values]
        return (models, at(float(main_strength)), labels, sweep_info(lora, values, float(main_strength)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraStrengthSweep", SYLoraStrengthSweep)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraStrengthSweep"] = "LoRA Strength Sweep SY"
