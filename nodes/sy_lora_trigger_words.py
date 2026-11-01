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


def read_sidecar_ex(lora_path):
    """Looks for <lora>.json, <lora>.txt, then <lora>.civitai.info next to the LoRA file. Returns (words, file_name_used)."""
    base = os.path.splitext(lora_path)[0]
    for ext, parse in ((".json", words_from_json), (".txt", words_from_txt), (".civitai.info", words_from_json)):
        p = base + ext
        if os.path.isfile(p):
            if os.path.getsize(p) > MAX_SIDECAR_BYTES:
                raise ValueError("sidecar file %s is bigger than 1 MB" % os.path.basename(p))
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                words = parse(f.read())
            if words:
                return words, os.path.basename(p)
    return [], ""


def read_sidecar_words(lora_path):
    """Looks for <lora>.json then <lora>.txt then <lora>.civitai.info next to the LoRA file. Returns a list of words (maybe empty)."""
    return read_sidecar_ex(lora_path)[0]


def merge_triggers(prompt, words):
    """Pure function. Puts trigger words in front of the prompt, skipping the ones the prompt already holds. Returns (text, added_words)."""
    prompt = (prompt or "").strip()
    low = prompt.lower()
    added = [w for w in words if w.lower() not in low]
    if not added:
        return prompt, []
    return ", ".join(added + ([prompt] if prompt else [])), added


def trigger_info(lora_name, words, source, added=None):
    """Pure function. One plain line: where the words came from, or what to do when there are none."""
    if not words:
        stem = os.path.splitext(os.path.basename(str(lora_name).replace("\\", "/")))[0]
        return ("No trigger words found for %s. Put a %s.txt (words) or %s.json (trainedWords) file next to the LoRA." % (lora_name, stem, stem))
    info = "%d trigger word%s from %s." % (len(words), "" if len(words) == 1 else "s", source)
    if added is not None:
        info += " %d added to the prompt, %d already there." % (len(added), len(words) - len(added))
    return info


class SYLoraTriggerWords:
    DESCRIPTION = ("Reads the trigger words for a LoRA from a .json, .txt or .civitai.info file with the same name next to it. Can put "
                   "them in front of your prompt (skipping words already there). An info line says where they came from, or what file to make.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("trigger_words", "prompt", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"lora_name": ([NONE_NAME] + list_names("loras"), {"tooltip": "The LoRA whose trigger words you want."})},
                "optional": {
                    "separator": ("STRING", {"default": ", ", "tooltip": "Text placed between the trigger words, for example a comma and a space."}),
                    "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Optional prompt. The prompt output is this text with the trigger words in front."}),
                }}

    def run(self, lora_name, separator=", ", prompt=""):
        if lora_name == NONE_NAME:
            return ("", (prompt or "").strip(), "No LoRA picked.")
        words, source = read_sidecar_ex(find_file("loras", lora_name))
        joined = separator.join(words)
        merged, added = merge_triggers(prompt, words)
        return (joined, merged, trigger_info(lora_name, words, source, added if (prompt or "").strip() else None))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoraTriggerWords", SYLoraTriggerWords)
NODE_DISPLAY_NAME_MAPPINGS["SYLoraTriggerWords"] = "LoRA Trigger Words SY"
