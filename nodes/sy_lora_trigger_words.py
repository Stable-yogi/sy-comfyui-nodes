"""LoRA Trigger Words SY: reads trigger words from a small .json or .txt file that sits next to a LoRA."""
import json
import os

try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, NONE_NAME

MAX_SIDECAR_BYTES = 1024 * 1024
WORD_KEYS = ("trainedWords", "trained_words", "trigger_words", "triggerWords", "trigger", "activation text", "activation_text")


def _flatten(value):
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            out.extend(_flatten(v))
        return out
    return []


def words_from_json(text):
    """Pure function. Finds trigger words in sidecar JSON text (top level or one level down)."""
    try:
        data = json.loads(text)
    except ValueError:
        raise ValueError("the sidecar .json file is not valid JSON")
    found = []

    def scan(obj):
        if isinstance(obj, dict):
            for k in WORD_KEYS:
                if k in obj:
                    found.extend(_flatten(obj[k]))
    scan(data)
    if not found and isinstance(data, dict):
        for v in data.values():
            scan(v)
    seen = []
    for w in found:
        if w not in seen:
            seen.append(w)
    return seen


def words_from_txt(text):
    """Pure function. A .txt sidecar is taken as it is (trimmed)."""
    t = " ".join(text.split())
    return [t] if t else []


def read_sidecar_words(lora_path):
    """Looks for <lora>.json then <lora>.txt next to the LoRA file. Returns a list of words (maybe empty)."""
    base = os.path.splitext(lora_path)[0]
    for ext, parse in ((".json", words_from_json), (".txt", words_from_txt)):
        p = base + ext
        if os.path.isfile(p):
            if os.path.getsize(p) > MAX_SIDECAR_BYTES:
                raise ValueError("sidecar file %s is bigger than 1 MB" % os.path.basename(p))
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                words = parse(f.read())
            if words:
                return words
    return []


class SYLoraTriggerWords:
    DESCRIPTION = "Reads the trigger words for a LoRA from a .json or .txt file with the same name next to it. Empty when there is none."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("trigger_words",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"lora_name": ([NONE_NAME] + list_names("loras"), {"tooltip": "The LoRA whose trigger words you want."})}}

    def run(self, lora_name):
        if lora_name == NONE_NAME:
            return ("",)
        words = read_sidecar_words(find_file("loras", lora_name))
        return (", ".join(words),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraTriggerWords", SYLoraTriggerWords)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraTriggerWords"] = "LoRA Trigger Words SY"
