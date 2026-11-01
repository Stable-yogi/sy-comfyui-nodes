"""Power Lora Loader SY: any number of LoRAs in one node, a switch per row, trigger words, and a picture on hover (browser part)."""
import json
import math
import os
from collections import OrderedDict

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_ROWS = 64
MAX_STRENGTH = 10.0
JOINS = {"comma": ", ", "newline": "\n", "space": " "}
CACHE_SIZE = 8


def _num(value, what, row):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Row %d: %s must be a number, got %r. Set it again in the row editor." % (row, what, value))
    if math.isnan(value) or math.isinf(value):
        raise ValueError("Row %d: %s is not a usable number. Set it again in the row editor." % (row, what))
    return float(value)


def check_rows(rows):
    """Pure function. Plain refusal when there are too many rows or a strength is outside -10..10. Returns the rows."""
    if not isinstance(rows, list):
        raise ValueError("The LoRA list must be a list of rows. Use the row editor on the node.")
    if len(rows) > MAX_ROWS:
        raise ValueError("There are %d LoRA rows but the most allowed is %d. Delete some rows." % (len(rows), MAX_ROWS))
    for i, r in enumerate(rows, 1):
        for key, label in (("strength", "strength"), ("strength_clip", "clip strength")):
            v = r.get(key)
            if v is None:
                continue
            if not -MAX_STRENGTH <= v <= MAX_STRENGTH:
                raise ValueError("Row %d: %s %s is outside the allowed range -%g to %g. Change the number." % (i, label, v, MAX_STRENGTH, MAX_STRENGTH))
    return rows


def parse_rows(text):
    """Pure function. The lora_rows text (JSON list) -> list of clean rows
    {"on": bool, "name": str, "strength": float, "strength_clip": float or None, "triggers": str}. Extra keys are dropped."""
    if text is None or not str(text).strip():
        return []
    try:
        data = json.loads(text)
    except ValueError:
        raise ValueError("The LoRA list is not readable. Use the row editor on the node, or reset the list to [].")
    if not isinstance(data, list):
        raise ValueError("The LoRA list must be a list of rows. Use the row editor on the node.")
    if len(data) > MAX_ROWS:
        raise ValueError("There are %d LoRA rows but the most allowed is %d. Delete some rows." % (len(data), MAX_ROWS))
    rows = []
    for i, r in enumerate(data, 1):
        if not isinstance(r, dict):
            raise ValueError("Row %d is not a LoRA row. Delete it in the row editor." % i)
        on = r.get("on", True)
        if not isinstance(on, bool):
            raise ValueError("Row %d: the on/off switch must be true or false, got %r." % (i, on))
        name = r.get("name", "")
        if not isinstance(name, str):
            raise ValueError("Row %d: the LoRA name must be text, got %r. Pick it again in the list." % (i, name))
        strength = _num(r.get("strength", 1.0), "strength", i)
        sc = r.get("strength_clip", None)
        sc = None if sc is None else _num(sc, "clip strength", i)
        trig = r.get("triggers", "")
        if trig is None:
            trig = ""
        if not isinstance(trig, str):
            raise ValueError("Row %d: the trigger words must be text, got %r." % (i, trig))
        rows.append({"on": on, "name": name.strip(), "strength": strength, "strength_clip": sc, "triggers": trig})
    return check_rows(rows)


def rows_to_json(rows):
    """Pure function. Rows -> the JSON text stored in lora_rows."""
    return json.dumps([{"on": bool(r["on"]), "name": r["name"], "strength": r["strength"],
                        "strength_clip": r["strength_clip"], "triggers": r["triggers"]} for r in rows])


def clean_triggers(texts, join="comma"):
    """Pure function. Texts -> one string: split on commas and new lines, trim, drop repeats (any letter case) in order."""
    if join not in JOINS:
        raise ValueError("trigger_join must be one of: %s, got %r" % (", ".join(JOINS), join))
    seen, words = set(), []
    for t in texts:
        for part in str(t or "").replace("\r", "\n").replace("\n", ",").split(","):
            w = part.strip()
            if w and w.lower() not in seen:
                seen.add(w.lower())
                words.append(w)
    return JOINS[join].join(words)


def _flat(name):
    return str(name).replace("\\", "/")


def resolve_name(name, available, row=None):
    """Pure function. The entry of `available` that a saved name means: exact match, else the one entry whose path ends with the name."""
    where = " (row %d)" % row if row else ""
    want = _flat(name).strip()
    if not want:
        raise ValueError("LoRA '%s'%s was not found. Pick it again in the list." % (name, where))
    for a in available:
        if _flat(a) == want:
            return a
    tail = "/" + want.lstrip("/")
    hits = [a for a in available if ("/" + _flat(a)).endswith(tail)]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise ValueError("LoRA '%s'%s matches more than one file (%s). Pick the one you want in the list." % (name, where, ", ".join(hits[:4])))
    raise ValueError("LoRA '%s'%s was not found. Pick it again in the list." % (name, where))


def _eff_clip(r):
    return r["strength"] if r["strength_clip"] is None else r["strength_clip"]


def rows_to_info(rows, applied, notes=None):
    """Pure function. One line per row. `applied` = set of 0-based row numbers that were applied, notes = {index: text}."""
    notes = notes or {}
    lines = []
    for i, r in enumerate(rows):
        n = i + 1
        name = r["name"] or "(no LoRA picked)"
        if i in applied:
            line = "%d. %s x%.2f (clip x%.2f) on" % (n, name, r["strength"], _eff_clip(r))
        elif not r["on"]:
            line = "%d. %s off" % (n, name)
        elif not r["name"]:
            line = "%d. %s skipped" % (n, name)
        elif r["strength"] == 0 and _eff_clip(r) == 0:
            line = "%d. %s skipped (strength 0)" % (n, name)
        else:
            line = "%d. %s not applied" % (n, name)
        if i in notes:
            line += " - " + notes[i]
        lines.append(line)
    return "\n".join(lines) if lines else "No LoRA rows."


class LoraCache:
    """Small in-memory cache of loaded LoRA tensors, keyed by (path, modified time). Keeps at most `size` entries."""

    def __init__(self, size=CACHE_SIZE):
        self.size = size
        self.items = OrderedDict()

    def get(self, key, loader):
        if key in self.items:
            self.items.move_to_end(key)
            return self.items[key]
        value = loader()
        self.items[key] = value
        while len(self.items) > self.size:
            self.items.popitem(last=False)
        return value


def apply_rows(rows, model, clip, available, load_lora, apply_lora, join="comma"):
    """The apply loop. load_lora(real_name) -> tensors, apply_lora(model, clip, tensors, s_model, s_clip) -> (model, clip).
    Returns (model, clip, trigger_text, info_text). Torch is never touched here, so it can be tested with plain stand-ins."""
    applied, notes, trig = set(), {}, []
    for i, r in enumerate(rows):
        if not r["on"] or not r["name"]:
            continue
        s_model = r["strength"]
        s_clip = _eff_clip(r)
        if s_model == 0 and s_clip == 0:
            continue
        if clip is None and s_clip != 0:
            s_clip = 0.0
            notes[i] = "no clip connected, only the model part was applied"
            if s_model == 0:
                notes[i] = "no clip connected, so there was nothing to apply"
                continue
        real = resolve_name(r["name"], available, i + 1)
        tensors = load_lora(real)
        model, clip = apply_lora(model, clip, tensors, s_model, s_clip)
        applied.add(i)
        trig.append(r["triggers"])
    return model, clip, clean_triggers(trig, join), rows_to_info(rows, applied, notes)


_cache = LoraCache()


class SYPowerLoraLoader:
    DESCRIPTION = ("Loads any number of LoRAs into the model and clip with one node. Each row has its own on/off switch, "
                   "strength, optional separate clip strength and trigger words. The trigger_words output joins the words of "
                   "every LoRA that was applied, without repeats, ready for your prompt. The master switch passes the model "
                   "and clip on unchanged. Use the row editor on the node to add and pick LoRAs.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "trigger_words", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model the LoRAs are applied to."}),
                "lora_rows": ("STRING", {"default": "[]", "multiline": False,
                                         "tooltip": "The list of LoRAs. The row editor on the node fills this in; you do not type it."}),
                "all_on": ("BOOLEAN", {"default": True, "tooltip": "Master switch. Off passes the model and clip on unchanged."}),
                "trigger_join": (list(JOINS), {"default": "comma", "tooltip": "How the trigger words are joined in the trigger_words output."}),
            },
            "optional": {
                "clip": ("CLIP", {"tooltip": "The text encoder. Without it only the model part of each LoRA is applied."}),
            },
        }

    def run(self, model, lora_rows, all_on, trigger_join, clip=None):
        rows = parse_rows(lora_rows)
        if trigger_join not in JOINS:
            raise ValueError("trigger_join must be one of: %s, got %r" % (", ".join(JOINS), trigger_join))
        if not all_on:
            info = "Master switch is off: the model and clip were passed on unchanged."
            if rows:
                info += "\n" + rows_to_info([dict(r, on=False) for r in rows], set())
            return (model, clip, "", info)
        if not any(r["on"] and r["name"] for r in rows):
            return (model, clip, "", rows_to_info(rows, set()))
        import folder_paths
        import comfy.sd
        import comfy.utils
        available = list(folder_paths.get_filename_list("loras"))

        def load_lora(real):
            path = folder_paths.get_full_path("loras", real)
            if not path:
                raise ValueError("LoRA '%s' was not found. Pick it again in the list." % real)
            key = (path, os.path.getmtime(path))
            return _cache.get(key, lambda: comfy.utils.load_torch_file(path, safe_load=True))

        def apply_lora(m, c, tensors, s_model, s_clip):
            return comfy.sd.load_lora_for_models(m, c, tensors, s_model, s_clip)

        return apply_rows(rows, model, clip, available, load_lora, apply_lora, trigger_join)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PowerLoraLoader", SYPowerLoraLoader)
NODE_DISPLAY_NAME_MAPPINGS["SYPowerLoraLoader"] = "Power Lora Loader SY"
