"""Shared pure helpers for the batch A1 utility nodes: name filter, file facts, plain warnings, safetensors header.

No node class in here, no torch, no comfy. Everything runs in the plain selftest.
"""
import json
import os
import re
import struct

# ---------------------------------------------------------------- name filter


def split_words(text):
    """Pure function. 'Flux  Dev' -> ['flux', 'dev']. Empty or None gives []."""
    return [w for w in re.split(r"\s+", str(text or "").strip().lower()) if w]


def match_names(names, include="", exclude=""):
    """Pure function. Names that contain EVERY include word and NO exclude word (case does not matter), A to Z."""
    inc, exc = split_words(include), split_words(exclude)
    out = []
    for n in names:
        low = str(n).lower().replace("\\", "/")
        if all(w in low for w in inc) and not any(w in low for w in exc):
            out.append(n)
    return sorted(out, key=lambda s: (s.lower(), s))


def pick_with_filter(names, current, text, kind, field="name_filter"):
    """Pure function. Returns (chosen_name, note).

    Empty filter text: the dropdown pick stays (note is empty). With text: the first name (A to Z) that holds all the words.
    """
    words = split_words(text)
    if not words:
        return current, ""
    shown = " ".join(words)
    if not names:
        raise ValueError("No %s files were found, so %s %r cannot match anything. Put a file in the folder and refresh the list." % (kind, field, shown))
    found = match_names(names, shown)
    if not found:
        raise ValueError("No %s file name contains %r. Clear the %s box, or try fewer or shorter words." % (kind, shown, field))
    if len(found) == 1:
        return found[0], "%s %r picked %s." % (field, shown, found[0])
    return found[0], "%s %r matched %d files; using %s (first in A to Z order). Add more words to narrow it." % (field, shown, len(found), found[0])


# ---------------------------------------------------------------- file facts

KINDS = {
    ".safetensors": "safetensors (safe format)",
    ".sft": "safetensors (safe format)",
    ".gguf": "GGUF (compressed)",
    ".ckpt": "ckpt (older format)",
    ".pt": "pt (older format)",
    ".pth": "pth (older format)",
    ".bin": "bin (older format)",
}

PRECISION_NOTES = {
    "fp8": "fp8 = numbers stored in 8 bits: about half the size of fp16 and less memory, a small quality loss. Fastest on RTX 40 and newer cards; older cards still work.",
    "fp16": "fp16 = half precision, the usual size for a model file.",
    "bf16": "bf16 = same size as fp16 with a wider number range; good on newer cards.",
    "fp32": "fp32 = full precision, twice the size of fp16; rarely needed for rendering.",
    "nf4": "nf4 = 4-bit, very small, some quality loss.",
    "fp4": "fp4 = 4-bit, very small, some quality loss.",
    "int8": "int8 = 8-bit whole numbers, small, a little quality loss.",
}

QUANT_NOTES = {
    "2": "Q2 = smallest and fastest, big quality loss; last resort for low memory.",
    "3": "Q3 = small, visible quality loss.",
    "4": "Q4 = good balance of size and quality (Q4_K_M is the usual pick).",
    "5": "Q5 = close to the full quality, a bit bigger than Q4.",
    "6": "Q6 = very close to the full quality.",
    "8": "Q8 = nearly the same as the full file at about half the size of fp16.",
}

_PRECISION = re.compile(r"(?:^|[^a-z0-9])(fp8|fp16|bf16|fp32|nf4|fp4|int8)(?:[^a-z0-9]|$)", re.I)
_QUANT = re.compile(r"(?:^|[-_.\s/])(i?q(\d)(?:_[a-z0-9]+)*)(?=\.gguf$|\.|$|[-\s/])", re.I)


def base_name(name):
    return str(name).replace("\\", "/").split("/")[-1]


def file_kind(name):
    """Pure function. 'a/b.safetensors' -> 'safetensors (safe format)'. Unknown endings give the ending itself."""
    ext = os.path.splitext(base_name(name))[1].lower()
    if ext in KINDS:
        return KINDS[ext]
    return ext[1:] if ext else "no file ending"


def precision_hint(name):
    """Pure function. Looks for fp8 / fp16 / bf16 / fp32 / nf4 in the file name. Returns the key or ''."""
    low = base_name(name).lower()
    m = _PRECISION.search(low)
    if m:
        return m.group(1).lower()
    if "e4m3fn" in low or "e5m2" in low:
        return "fp8"
    return ""


def quant_hint(name):
    """Pure function. 'flux-dev-Q4_K_M.gguf' -> ('Q4_K_M', note). No quant in the name gives ('', '')."""
    m = _QUANT.search(base_name(name))
    if not m:
        return "", ""
    label = m.group(1).upper()
    return label, QUANT_NOTES.get(m.group(2), "")


def format_bytes(num_bytes):
    """Pure function. 1536 -> '1.5 KB'."""
    n = float(num_bytes)
    if n < 0:
        raise ValueError("size cannot be negative, got %s" % num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d B" % n) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


def check_size(name, size):
    """Pure function. A file of 0 bytes is a broken download: refuse it in plain words."""
    if int(size) <= 0:
        raise ValueError("%r is empty (0 bytes). The download probably did not finish: download the file again." % name)
    return int(size)


def file_facts(name, size):
    """Pure function. One line: 'name | safetensors (safe format) | 6.2 GB | fp8'."""
    parts = [str(name), file_kind(name), format_bytes(size)]
    prec = precision_hint(name)
    if prec:
        parts.append(prec)
    label, _ = quant_hint(name)
    if label:
        parts.append(label)
    return " | ".join(parts)


def precision_notes(name):
    """Pure function. Plain sentences that explain what the file name says about precision or quantisation."""
    out = []
    prec = precision_hint(name)
    if prec:
        out.append(PRECISION_NOTES[prec])
    label, note = quant_hint(name)
    if note:
        out.append("%s: %s" % (label, note))
    return out


# ---------------------------------------------------------------- plain warnings

_TOKEN_SPLIT = re.compile(r"[^a-z0-9]+")


def checkpoint_warnings(name):
    """Pure function. Plain warnings for a file that is loaded as a full checkpoint."""
    out = []
    low = base_name(name).lower()
    tokens = set(t for t in _TOKEN_SPLIT.split(low) if t)
    if low.endswith(".gguf"):
        out.append("This is a GGUF file. A checkpoint loader cannot open it: use UnetLoaderGGUF SY.")
    if low.endswith((".ckpt", ".pt", ".pth", ".bin")):
        out.append("This is an older file format. Use the .safetensors version of this model if there is one.")
    odd = sorted(tokens & {"vae", "lora", "controlnet", "t5xxl", "umt5", "embedding"})
    if odd:
        out.append("The file name contains %r: this may not be a full checkpoint. Check the file." % odd[0])
    return out


def missing_parts_note(has_clip, has_vae):
    """Pure function. Tells what a loaded checkpoint does not hold."""
    out = []
    if not has_vae:
        out.append("This checkpoint has no VAE inside: connect a VAE loader before decoding.")
    if not has_clip:
        out.append("This checkpoint has no text encoder (CLIP) inside: load one with a CLIP loader.")
    return out


# Name part a text encoder of that family usually has. Only families where the mix-up is common.
TYPE_EXPECTS = {"wan": ("umt5",), "qwen_image": ("qwen",)}
_OTHER_ENCODER_PARTS = ("t5", "clip_l", "clip_g", "gemma", "mistral", "llama", "umt5", "qwen")
UMT5_FAMILIES = ("wan", "ace")


def text_encoder_warning(name, clip_type):
    """Pure function. A plain hint when the file name and the chosen family do not fit. '' when nothing looks wrong.

    It only reads the file name, so it can be wrong: it is a warning, never an error.
    """
    low = base_name(name).lower()
    if clip_type in TYPE_EXPECTS and not any(p in low for p in TYPE_EXPECTS[clip_type]):
        if any(p in low for p in _OTHER_ENCODER_PARTS):
            return ("The file name does not look like a %s text encoder (those usually have %r in the name), "
                    "but the family is %s. Check that the file and the family belong together." % (clip_type, TYPE_EXPECTS[clip_type][0], clip_type))
    if "umt5" in low and clip_type not in UMT5_FAMILIES:
        return ("The file name says umt5, which is the Wan style text encoder, but the family is %s. "
                "If this is for Wan, set the family to wan." % clip_type)
    if "qwen" in low and "vl" in low and clip_type == "stable_diffusion":
        return ("The file name looks like a Qwen vision-language encoder, but the family is stable_diffusion. "
                "Check the family (for example qwen_image).")
    return ""


# ---------------------------------------------------------------- safetensors header


def read_st_header(path, max_bytes=16_000_000):
    """Reads ONLY the small header of a .safetensors file. Returns a dict, or {} for any other file."""
    try:
        with open(path, "rb") as f:
            raw = f.read(8)
            if len(raw) < 8:
                return {}
            n = struct.unpack("<Q", raw)[0]
            if n <= 0 or n > max_bytes:
                return {}
            data = f.read(n)
        header = json.loads(data.decode("utf-8"))
        return header if isinstance(header, dict) else {}
    except (OSError, ValueError, UnicodeDecodeError, struct.error):
        return {}


def st_metadata(path):
    """The __metadata__ block of a .safetensors file as {str: str}. {} when there is none."""
    meta = read_st_header(path).get("__metadata__", {})
    if not isinstance(meta, dict):
        return {}
    return {str(k): str(v) for k, v in meta.items()}


def lora_hints(meta, top=5):
    """Pure function. From safetensors metadata: {'base': text, 'triggers': [..], 'tags': [..]} (each may be empty).

    triggers = words the maker wrote down. tags = the most used training tags (kohya files).
    """
    base = meta.get("ss_base_model_version") or meta.get("modelspec.architecture") or ""
    triggers = []
    for key in ("modelspec.trigger_phrase", "trigger_words", "trigger_word", "ss_trigger_words"):
        val = str(meta.get(key, "")).strip()
        if val:
            triggers = [t.strip() for t in re.split(r"[,\n]+", val) if t.strip()][:top]
            break
    tags = []
    raw = meta.get("ss_tag_frequency")
    if raw:
        try:
            data = json.loads(raw)
            counts = {}
            if isinstance(data, dict):
                for tagmap in data.values():
                    if isinstance(tagmap, dict):
                        for tag, num in tagmap.items():
                            try:
                                counts[str(tag).strip()] = counts.get(str(tag).strip(), 0) + int(num)
                            except (TypeError, ValueError):
                                continue
            ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            tags = [t for t, _ in ranked if t][:top]
        except (ValueError, TypeError):
            tags = []
    return {"base": str(base), "triggers": triggers, "tags": tags}


# ---------------------------------------------------------------- folder wrong-place hint


def folders_holding(name, by_folder):
    """Pure function. by_folder = {folder: [names]}. Returns the folders whose list holds `name`."""
    return [f for f, names in by_folder.items() if name in names]
