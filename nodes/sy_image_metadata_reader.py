"""Image Metadata Reader SY: reads the prompt and workflow text stored inside a png in the input folder. Read only."""
import json
import os
import re

try:
    from ._sy_safe_paths import root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder, safe_join
    from _sy_common import category, register

MAX_FILE_BYTES = 50_000_000
MAX_TEXT_CHARS = 5_000_000


def extract_metadata(info, limit=MAX_TEXT_CHARS):
    """Pure function. (prompt_text, workflow_text) from a dict of png text chunks. Missing ones give ''."""
    out = []
    for key in ("prompt", "workflow"):
        val = (info or {}).get(key, "")
        if not isinstance(val, str):
            val = ""
        if len(val) > limit:
            raise ValueError("the %s text is too big (%d characters, max %d)" % (key, len(val), limit))
        out.append(val)
    return out[0], out[1]


SOURCES = ["input", "output"]
_SETTING_SPLIT = re.compile(r",\s(?=[A-Za-z][A-Za-z0-9 _]*:\s)")
_SAMPLER_KEYS = ("seed", "noise_seed", "steps", "cfg", "sampler_name", "scheduler", "denoise")


def parse_a1111(text):
    """Pure function. A 'parameters' text (Forge, A1111 style) -> (positive, negative, settings_lines)."""
    lines = str(text or "").replace("\r\n", "\n").split("\n")
    settings_at = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("Steps:"):
            settings_at = i
            break
    body = lines if settings_at is None else lines[:settings_at]
    settings = []
    if settings_at is not None:
        settings = [p.strip() for p in _SETTING_SPLIT.split(lines[settings_at]) if p.strip()]
    neg_at = next((i for i, ln in enumerate(body) if ln.startswith("Negative prompt:")), None)
    if neg_at is None:
        return "\n".join(body).strip(), "", settings
    positive = "\n".join(body[:neg_at]).strip()
    negative = "\n".join([body[neg_at][len("Negative prompt:"):]] + body[neg_at + 1:]).strip()
    return positive, negative, settings


def _follow_text(graph, link, depth=0):
    """Walks back from a conditioning link to the first node that holds a plain text input."""
    if depth > 6 or not (isinstance(link, list) and link):
        return ""
    node = graph.get(str(link[0]))
    if not isinstance(node, dict):
        return ""
    inputs = node.get("inputs") or {}
    for key in ("text", "text_g", "prompt"):
        if isinstance(inputs.get(key), str):
            return inputs[key]
    for key in ("conditioning", "conditioning_1", "positive"):
        if isinstance(inputs.get(key), list):
            found = _follow_text(graph, inputs[key], depth + 1)
            if found:
                return found
    return ""


def parse_comfy_prompt(prompt_text):
    """Pure function. A ComfyUI 'prompt' JSON text -> (positive, negative, settings_lines). Bad JSON gives empty values."""
    try:
        graph = json.loads(prompt_text) if prompt_text else {}
    except ValueError:
        return "", "", []
    if not isinstance(graph, dict):
        return "", "", []
    positive = negative = ""
    settings = []
    for nid in sorted(graph, key=lambda k: (len(str(k)), str(k))):
        node = graph[nid]
        inputs = node.get("inputs") if isinstance(node, dict) else None
        if not isinstance(inputs, dict):
            continue
        if "positive" in inputs and "negative" in inputs and not positive:
            positive = _follow_text(graph, inputs.get("positive"))
            negative = _follow_text(graph, inputs.get("negative"))
            for key in _SAMPLER_KEYS:
                if key in inputs and not isinstance(inputs[key], (list, dict)):
                    settings.append("%s: %s" % (key, inputs[key]))
    for nid in sorted(graph, key=lambda k: (len(str(k)), str(k))):
        node = graph[nid]
        inputs = node.get("inputs") if isinstance(node, dict) else None
        if not isinstance(inputs, dict):
            continue
        for key in ("ckpt_name", "unet_name"):
            if isinstance(inputs.get(key), str) and "model: %s" % inputs[key] not in settings:
                settings.append("model: %s" % inputs[key])
        if "width" in inputs and "height" in inputs and "batch_size" in inputs and not any(x.startswith("size:") for x in settings):
            if isinstance(inputs["width"], int) and isinstance(inputs["height"], int):
                settings.append("size: %dx%d" % (inputs["width"], inputs["height"]))
    return positive, negative, settings


def summarize_metadata(info, size=None):
    """Pure function. info = png text chunks. Returns (parameters, positive, negative, settings, info_text)."""
    info = info or {}
    params = info.get("parameters", "")
    params = params if isinstance(params, str) else ""
    prompt = info.get("prompt", "")
    prompt = prompt if isinstance(prompt, str) else ""
    workflow = info.get("workflow", "")
    found = []
    if params:
        found.append("Forge/A1111 'parameters' text")
    if prompt:
        found.append("ComfyUI prompt")
    if isinstance(workflow, str) and workflow:
        found.append("ComfyUI workflow")
    if params:
        pos, neg, sets = parse_a1111(params)
    else:
        pos, neg, sets = parse_comfy_prompt(prompt)
    head = ("Picture %dx%d. " % size) if size else ""
    if not found:
        return "", "", "", "", head + "No generation data found. The picture may have been saved without it, or converted by a site or app that strips it."
    text = head + "Found: " + ", ".join(found) + "."
    if prompt and not params and not pos and not sets:
        text += " Could not read a sampler out of the prompt (custom nodes?); the raw text is in prompt_text."
    return params, pos, neg, "\n".join(sets), text


class SYImageMetadataReader:
    DESCRIPTION = ("Reads the prompt and workflow text saved inside a png file from the input folder. It never changes the file. "
                   "Optional source can look in the output folder instead. Also splits out the positive and negative prompt "
                   "and the main settings (seed, steps, cfg, model), reads Forge/A1111 'parameters' text, and says what was found.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt_text", "workflow_json", "parameters", "positive", "negative", "settings", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"file": ("STRING", {"default": "", "tooltip": "A .png file inside the input folder, like image.png or a/b.png."})},
            "optional": {"source": (SOURCES, {"default": "input", "tooltip": "Which ComfyUI folder the file is in."})},
        }

    @classmethod
    def IS_CHANGED(cls, file, source="input"):
        try:
            return os.path.getmtime(safe_join(root_folder(source), file))
        except Exception:
            return float("nan")

    def run(self, file, source="input"):
        from PIL import Image

        if source not in SOURCES:
            raise ValueError("source must be input or output, got %r" % (source,))
        rel = str(file).strip()
        if not rel.lower().endswith(".png"):
            raise ValueError("only .png files carry this metadata, got %r" % rel)
        path = safe_join(root_folder(source), rel)
        if not os.path.isfile(path):
            raise ValueError("png file not found in the %s folder: %s" % (source, rel))
        size = os.path.getsize(path)
        if size > MAX_FILE_BYTES:
            raise ValueError("file is too big (%d bytes, max %d)" % (size, MAX_FILE_BYTES))
        try:
            with Image.open(path) as img:
                img.load()
                meta = dict(img.info)
                dims = img.size
        except (OSError, SyntaxError, ValueError):
            raise ValueError("%s could not be read as a picture. The file may be damaged." % rel)
        return extract_metadata(meta) + summarize_metadata(meta, dims)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageMetadataReader", SYImageMetadataReader)
NODE_DISPLAY_NAME_MAPPINGS["SYImageMetadataReader"] = "Image Metadata Reader SY"
