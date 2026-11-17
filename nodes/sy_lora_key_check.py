"""LoRA Key Check SY: tells you which parts of a LoRA file fit the loaded model, and which do not ("lora key not loaded")."""
import logging

try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, NONE_NAME

MISS_PREFIX = "lora key not loaded: "
LIST_LIMIT = 200
# Endings a LoRA file adds to the name of the model part it changes.
KEY_ENDINGS = (".lora_up.weight", ".lora_down.weight", ".lora_A.weight", ".lora_B.weight", ".lora.up.weight", ".lora.down.weight",
               ".lora_A.default.weight", ".lora_B.default.weight", ".lora_mid.weight", ".hada_w1_a", ".hada_w1_b", ".hada_w2_a",
               ".hada_w2_b", ".lokr_w1", ".lokr_w2", ".lokr_w1_a", ".lokr_w1_b", ".lokr_w2_a", ".lokr_w2_b", ".alpha", ".dora_scale",
               ".diff", ".diff_b", ".set_weight", ".w_norm", ".b_norm", ".weight", ".bias")


def part_name(key):
    """Pure function. 'a.b.lora_up.weight' -> 'a.b' (the model part this key belongs to)."""
    k = str(key)
    for end in KEY_ENDINGS:
        if k.endswith(end):
            return k[: -len(end)]
    return k


def group_parts(keys):
    """Pure function. Many keys -> sorted unique part names."""
    return sorted({part_name(k) for k in keys})


def top_prefixes(names, depth=1, limit=3):
    """Pure function. Most common first name pieces (split on '.' or '_' for lora_unet style names). Returns [(prefix, count)]."""
    counts = {}
    for n in names:
        s = str(n)
        sep = "." if "." in s else "_"
        pieces = s.split(sep)
        d = depth + 1 if pieces[0] == "lora" else depth  # lora_te1_..., lora_unet_... keep their second piece
        prefix = sep.join(pieces[:d])
        counts[prefix] = counts.get(prefix, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]


def verdict(total_keys, missed_keys, not_applied=0):
    """Pure function. One plain line: OK, PARTLY or NO MATCH."""
    if total_keys <= 0:
        return "EMPTY: the LoRA file holds no keys."
    used = total_keys - missed_keys
    pct = 100.0 * used / total_keys
    if missed_keys == 0 and not_applied == 0:
        return "OK: all %d LoRA keys fit this model." % total_keys
    if used == 0:
        return "NO MATCH: none of the %d LoRA keys fit this model. The LoRA is for another model, or uses names this ComfyUI does not know." % total_keys
    line = "PARTLY: %d of %d LoRA keys fit this model (%.0f%%); %d do not." % (used, total_keys, pct, missed_keys)
    if not_applied:
        line += " %d matched parts could not be put on the model." % not_applied
    return line


def build_report(lora_name, total_keys, missed, not_applied=()):
    """Pure function. Full plain-word report. missed = LoRA keys that were not loaded; not_applied = matched model parts not put on."""
    missed = list(missed)
    lines = ["LoRA: %s" % lora_name, verdict(total_keys, len(missed), len(not_applied))]
    if missed:
        parts = group_parts(missed)
        lines.append("Parts that do not fit: %d" % len(parts))
        tops = ", ".join("%s (%d)" % (p, c) for p, c in top_prefixes(parts))
        lines.append("They mostly start with: %s" % tops)
        lines.append("Tip: if most parts are the text encoder (te, text_model, lora_te) and you only load the model, connect clip too. "
                     "If they are the main model, the LoRA was trained for a different model or version.")
    if not_applied:
        lines.append("Matched but not put on the model: %d (shape or name mismatch)." % len(not_applied))
    return "\n".join(lines)


def list_text(keys, limit=LIST_LIMIT):
    """Pure function. Newline list of part names, cut at limit with a count of the rest."""
    parts = group_parts(keys)
    shown = parts[:limit]
    if len(parts) > limit:
        shown.append("... and %d more" % (len(parts) - limit))
    return "\n".join(shown)


class _MissCatcher(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.keys = []

    def emit(self, record):
        try:
            msg = record.getMessage()
        except Exception:
            return
        if msg.startswith(MISS_PREFIX):
            self.keys.append(msg[len(MISS_PREFIX):].strip())


def check_lora(model, clip, lora_sd):
    """Runs ComfyUI's own LoRA matching. Returns (total_keys, missed_keys, not_applied_targets). Changes nothing on the model."""
    import comfy.lora
    try:
        import comfy.lora_convert as lc
        lora_sd = lc.convert_lora(lora_sd)
    except ImportError:
        pass
    key_map = comfy.lora.model_lora_keys_unet(model.model, {})
    if clip is not None:
        key_map = comfy.lora.model_lora_keys_clip(clip.cond_stage_model, key_map)
    catcher = _MissCatcher()
    root = logging.getLogger()
    root.addHandler(catcher)
    try:
        loaded = comfy.lora.load_lora(lora_sd, key_map, log_missing=True)
    finally:
        root.removeHandler(catcher)
    applied = set(model.clone().add_patches(loaded, 1.0))
    if clip is not None:
        applied |= set(clip.clone().add_patches(loaded, 1.0))
    not_applied = [str(k) for k in loaded if k not in applied]
    return len(lora_sd), catcher.keys, not_applied


class SYLoraKeyCheck:
    DESCRIPTION = ("Checks a LoRA against the loaded model before you use it. Says OK when every part fits, or lists the parts that do "
                   "not fit (the 'lora key not loaded' lines in the console), so you can see if the LoRA is for another model. "
                   "The model goes through unchanged.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("model", "report", "unmatched_parts", "match_percent")
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                    "model": ("MODEL", {"tooltip": "The model the LoRA is meant for. It goes out unchanged."}),
                    "lora_name": ([NONE_NAME] + list_names("loras"), {"tooltip": "The LoRA file to check."}),
                },
                "optional": {
                    "clip": ("CLIP", {"tooltip": "Optional. Connect it if the LoRA also changes the text encoder, so those parts count as fitting."}),
                }}

    def run(self, model, lora_name, clip=None):
        if lora_name == NONE_NAME:
            return {"ui": {"text": ["No LoRA picked."]}, "result": (model, "No LoRA picked.", "", 0.0)}
        import comfy.utils
        sd = comfy.utils.load_torch_file(find_file("loras", lora_name), safe_load=True)
        total, missed, not_applied = check_lora(model, clip, sd)
        report = build_report(lora_name, total, missed, not_applied)
        pct = round(100.0 * (total - len(missed)) / total, 1) if total else 0.0
        return {"ui": {"text": [report]}, "result": (model, report, list_text(missed), pct)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraKeyCheck", SYLoraKeyCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraKeyCheck"] = "LoRA Key Check SY"
