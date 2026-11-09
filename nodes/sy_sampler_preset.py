"""Sampler Preset SY: pick a model family, then one sampler pair we tested for it. Pairs that break the picture are not offered."""
try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names

# family: list of (sampler, scheduler, steps, cfg). Easy to edit: keep the shape.
PAIRS = {  # MOSS rows: card test 2026-11-10, one prompt, seed 101, 1024x1024, shift 5. karras and exponential spoil MOSS pictures, so they are left out.
    "MOSS": [("er_sde", "normal", 25, 4.0), ("er_sde", "simple", 25, 4.0), ("euler", "simple", 25, 4.0),
             ("euler", "beta", 25, 4.0), ("sa_solver", "simple", 25, 4.0)],
    "MOSS + turbo LoRA": [("euler", "simple", 8, 1.0), ("euler", "normal", 8, 1.0), ("euler", "beta", 8, 1.0)],
    "Krea 2 Turbo": [("euler", "simple", 8, 1.0)],  # from the official Krea 2 Turbo template
}

# family: one plain sentence shown in the info text.
NOTES = {
    "MOSS": "Tested pairs for the normal MOSS model. er_sde gives the most skin detail.",
    "MOSS + turbo LoRA": "Few steps and cfg 1 because the turbo LoRA does the speed-up.",
    "Krea 2 Turbo": "Few steps and cfg 1, as in the official Turbo example.",
}

SEP = ": "


def pair_labels(pairs):
    """Pure function. Every pair label of every family, in table order: '<family>: <sampler> + <scheduler>'."""
    labels = []
    for family, rows in pairs.items():
        for row in rows:
            labels.append("%s%s%s + %s" % (family, SEP, row[0], row[1]))
    return labels


def parse_label(label):
    """Pure function. Splits a label into (family, sampler, scheduler)."""
    text = str(label)
    family, sep, rest = text.partition(SEP)
    sampler, plus, scheduler = rest.partition(" + ")
    if not sep or not plus or not family.strip() or not sampler.strip() or not scheduler.strip():
        raise ValueError("pair %r is not in the form '<family>: <sampler> + <scheduler>'. Pick one from the list." % text)
    return family.strip(), sampler.strip(), scheduler.strip()


def pick(family, label, steps_override, valid_samplers, valid_schedulers, pairs=None, notes=None):
    """Pure function. Returns (sampler, scheduler, steps, cfg, info) for the picked pair."""
    pairs = PAIRS if pairs is None else pairs
    notes = NOTES if notes is None else notes
    if family not in pairs:
        raise ValueError("unknown family %r. Pick one of: %s" % (family, ", ".join(pairs)))
    label_family, sampler, scheduler = parse_label(label)
    if label_family != family:
        raise ValueError("This pair is for %s. Pick a pair that starts with %s." % (label_family, family))
    row = None
    for r in pairs[family]:
        if r[0] == sampler and r[1] == scheduler:
            row = r
            break
    if row is None:
        raise ValueError("%s has no tested pair %s + %s. Pick one from the list." % (family, sampler, scheduler))
    if valid_samplers is not None and sampler not in valid_samplers:
        raise ValueError("This ComfyUI has no sampler %r. Update ComfyUI." % sampler)
    if valid_schedulers is not None and scheduler not in valid_schedulers:
        raise ValueError("This ComfyUI has no scheduler %r. Update ComfyUI." % scheduler)
    override = int(steps_override)
    if override < 0:
        raise ValueError("steps_override must be 0 or more, got %d" % override)
    steps = override if override > 0 else int(row[2])
    cfg = float(row[3])
    info = "%s: %s + %s, %d steps, cfg %g." % (family, sampler, scheduler, steps, cfg)
    note = notes.get(family, "")
    if note:
        info += " " + note
    return sampler, scheduler, steps, cfg, info


class SYSamplerPreset:
    DESCRIPTION = ("Pick a model family, then one sampler and scheduler pair that we tested for it. "
                   "Gives sampler, scheduler, steps and cfg to plug into a sampler. Untested pairs are not offered.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = (sampler_names(), scheduler_names(), "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("sampler_name", "scheduler", "steps", "cfg", "info")

    @classmethod
    def INPUT_TYPES(cls):
        labels = pair_labels(PAIRS)
        return {"required": {
            "family": (list(PAIRS.keys()), {"tooltip": "The model family. The pair below must start with the same name."}),
            "pair": (labels, {"default": labels[0], "tooltip": "A sampler and scheduler pair tested for the family. Pick one that starts with it."}),
            "steps_override": ("INT", {"default": 0, "min": 0, "max": 200, "tooltip": "0 uses the steps of the preset. Any other number replaces them."}),
        }}

    def run(self, family, pair, steps_override):
        return pick(family, pair, steps_override, sampler_names(), scheduler_names())


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SamplerPreset", SYSamplerPreset)
