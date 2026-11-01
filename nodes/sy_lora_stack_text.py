"""LoRA Stack Text SY: turns up to 4 LoRA names and strengths into a text summary and prompt tags. Does not change any model."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, lora_stem, fmt_strength, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, lora_stem, fmt_strength, NONE_NAME

SLOTS = 4


def active_loras(pairs, skip_zero=False):
    """Pure function. pairs = [(name, strength)]. Drops 'None' and empty names (and strength 0 when skip_zero). Returns [(name, float strength)]."""
    out = []
    for name, strength in pairs:
        if not name or name == NONE_NAME:
            continue
        s = float(strength)
        if s < -20 or s > 20:
            raise ValueError("strength for %s must be between -20 and 20, got %s" % (name, s))
        if skip_zero and s == 0:
            continue
        out.append((name, s))
    return out


def stack_notes(pairs, skip_zero=False):
    """Pure function. Plain warnings about the stack, or 'OK: no warnings.'"""
    act = active_loras(pairs, skip_zero)
    notes = []
    seen = set()
    for name, _ in act:
        if name in seen and ("%s is picked more than once" % name) not in notes:
            notes.append("%s is picked more than once" % name)
        seen.add(name)
    if not skip_zero and any(s == 0 for _, s in act):
        notes.append("a LoRA has strength 0 and does nothing (turn on skip_zero to leave it out)")
    total = sum(abs(s) for _, s in act)
    if total > 3:
        notes.append("the strengths add up to %s; a big total often over-bakes the picture" % fmt_strength(total))
    return ("WARNING: " + "; ".join(notes) + ".") if notes else "OK: no warnings."


def stack_text(pairs, skip_zero=False):
    """Pure function. Returns (summary, tags). Tags look like <lora:name:0.8>."""
    act = active_loras(pairs, skip_zero)
    if not act:
        return "No LoRAs selected.", ""
    lines = ["%d. %s (strength %s)" % (i + 1, n, fmt_strength(s)) for i, (n, s) in enumerate(act)]
    tags = " ".join("<lora:%s:%s>" % (lora_stem(n), fmt_strength(s)) for n, s in act)
    return "\n".join(lines), tags


class SYLoraStackText:
    DESCRIPTION = ("Writes up to 4 LoRA names and strengths as a short summary and as <lora:name:0.8> tags. It does not apply the LoRAs. "
                   "Gives the count, can leave out strength-0 slots, and warns when a LoRA is picked twice or the total is very high.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("summary", "tags", "count", "notes")

    @classmethod
    def INPUT_TYPES(cls):
        names = [NONE_NAME] + list_names("loras")
        req = {}
        for i in range(1, SLOTS + 1):
            req["lora_%d" % i] = (names, {"tooltip": "LoRA for slot %d. Leave on None to skip it." % i})
            req["strength_%d" % i] = ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.05, "tooltip": "Strength for slot %d." % i})
        return {"required": req, "optional": {
            "skip_zero": ("BOOLEAN", {"default": False, "tooltip": "On: a slot with strength 0 is left out of the text."}),
        }}

    def run(self, **kw):
        pairs = [(kw["lora_%d" % i], kw["strength_%d" % i]) for i in range(1, SLOTS + 1)]
        skip = bool(kw.get("skip_zero", False))
        summary, tags = stack_text(pairs, skip)
        return summary, tags, len(active_loras(pairs, skip)), stack_notes(pairs, skip)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraStackText", SYLoraStackText)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraStackText"] = "LoRA Stack Text SY"
