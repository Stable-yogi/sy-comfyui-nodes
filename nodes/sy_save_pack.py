"""Save Pack SY: saves pictures into the output folder with a file name built from tokens, plus a settings text file.

Never overwrites: a taken name gets the next free number. Folder rules are the shared safe ones (no .., no drive letters).
"""
import os
import re
from datetime import datetime

try:
    from ._sy_safe_paths import (safe_join, root_folder, list_files, tensor_to_pil, write_image, workflow_chunks)
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import (safe_join, root_folder, list_files, tensor_to_pil, write_image, workflow_chunks)
    from _sy_common import category, register

TOKENS = ("date", "time", "name", "seed", "steps", "cfg", "width", "height", "format", "counter", "batch")
FORMATS = ["png", "jpeg", "webp"]
EXT = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}
WRITE_FMT = {"png": "png", "jpeg": "jpg", "webp": "webp"}  # the names the shared writer knows
ON_EXISTS = ["next number", "skip"]
COUNTER_WIDTH = 5
MAX_PART = 100        # longest folder part or {name} text
MAX_STEM = 120        # longest file name without ending
MAX_TEXT = 100000
_BAD = set('<>:"/\\|?*')
_RESERVED = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}
_MARK = "COUNTER"  # private-use letters: cannot be typed by accident and are not cleaned away


def valid_tokens_text():
    return " ".join("{%s}" % t for t in TOKENS)


def clean_text(text, limit=MAX_PART, fallback="image"):
    """Pure function. Makes free text safe inside ONE file or folder name: bad characters become _, length limited."""
    t = "".join("_" if (c in _BAD or ord(c) < 32) else c for c in str(text if text is not None else ""))
    t = " ".join(t.split()).strip(" .")
    t = t[:limit].strip(" .")
    if t.split(".")[0].lower() in _RESERVED:
        t = "_" + t
    return t or fallback


def check_pattern(pattern, allow_counter=True, what="file name pattern"):
    """Pure function. Plain refusal for a wrong token, a lonely brace, or {counter} used twice. Returns the tokens found."""
    pattern = str(pattern)
    found = re.findall(r"\{([^{}]*)\}", pattern)
    for t in found:
        if t not in TOKENS:
            raise ValueError("unknown token {%s} in the %s. Valid tokens: %s" % (t, what, valid_tokens_text()))
    rest = re.sub(r"\{[^{}]*\}", "", pattern)
    if "{" in rest or "}" in rest:
        raise ValueError("the %s has a lonely { or }: %r. Valid tokens: %s" % (what, pattern, valid_tokens_text()))
    if found.count("counter") > 1:
        raise ValueError("use {counter} only once in the %s" % what)
    if found.count("counter") and not allow_counter:
        raise ValueError("{counter} cannot be used in the %s; use it in the file name pattern" % what)
    return found


def cfg_text(cfg):
    """Pure function. 7.5 -> '7.5', 7.0 -> '7', 0 -> '0'."""
    return ("%.2f" % float(cfg)).rstrip("0").rstrip(".") or "0"


def token_values(name, seed, steps, cfg, width, height, fmt, batch_no, now):
    """Pure function. The text each token turns into (except {counter})."""
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H%M%S"),
        "name": clean_text(name, MAX_PART, "image"),
        "seed": "noseed" if int(seed) < 0 else str(int(seed)),
        "steps": str(int(steps)),
        "cfg": cfg_text(cfg),
        "width": str(int(width)),
        "height": str(int(height)),
        "format": str(fmt),
        "batch": "%02d" % int(batch_no),
    }


def fill_tokens(pattern, values, keep_counter=True):
    """Pure function. Replaces every token except {counter}, which becomes a private marker (or is left as it is)."""
    out = str(pattern)
    for key, val in values.items():
        out = out.replace("{%s}" % key, val)
    if keep_counter:
        out = out.replace("{counter}", _MARK)
    return out


def fill_subfolder(pattern, values):
    """Pure function. Folder text with tokens filled, each part cleaned. '' stays ''. '..' and drive letters are refused later."""
    check_pattern(pattern, allow_counter=False, what="subfolder")
    text = fill_tokens(pattern, values, keep_counter=False).replace("\\", "/")
    parts = []
    for p in text.split("/"):
        p = p.strip()
        if p in ("", "."):
            continue
        if p == "..":
            raise ValueError("the subfolder must not contain '..': %r" % pattern)
        if re.match(r"^[A-Za-z]:$", p):
            raise ValueError("the subfolder must not contain a drive letter: %r" % pattern)
        parts.append(clean_text(p, MAX_PART, "_"))
    return "/".join(parts)


def stem_template(pattern, values):
    """Pure function. The file name (no ending) with tokens filled and the length limited. {counter} stays as a marker."""
    check_pattern(pattern)
    if not str(pattern).strip():
        raise ValueError("the file name pattern is empty: type something such as {date}_{name}_{counter}")
    text = fill_tokens(pattern, values)
    text = "".join("_" if (c in _BAD or ord(c) < 32) else c for c in text)
    if _MARK in text:
        left, right = text.split(_MARK, 1)
        right = right[:20]
        left = left[:max(1, MAX_STEM - COUNTER_WIDTH - len(right))]
        return left + _MARK + right
    return text[:MAX_STEM - COUNTER_WIDTH - 1]


def _is_taken(stem, ext, taken, companion):
    return (stem + ext).lower() in taken or (companion and (stem + companion).lower() in taken)


def pick_name(template, ext, taken, on_exists, companion=".txt"):
    """Pure function. Chooses one free file name stem. Returns (stem, skipped).

    `taken` = set of lower case names already in the folder (the caller adds each name it picks).
    With a {counter} marker the number goes after the highest one found. Without: the plain name, then _00001, _00002...
    on_exists 'skip' never saves under a taken plain name (stem is None, skipped True).
    """
    if on_exists not in ON_EXISTS:
        raise ValueError("on_exists must be one of: %s, got %r" % (", ".join(ON_EXISTS), on_exists))
    if _MARK in template:
        left, right = template.split(_MARK, 1)
        rx = re.compile("^" + re.escape(left.lower()) + r"(\d+)" + re.escape(right.lower()) + re.escape(ext.lower()) + "$")
        highest = max([int(m.group(1)) for m in (rx.match(n) for n in taken) if m] or [0])
        stem = "%s%0*d%s" % (left, COUNTER_WIDTH, highest + 1, right)
        while _is_taken(stem, ext, taken, companion):
            highest += 1
            stem = "%s%0*d%s" % (left, COUNTER_WIDTH, highest + 1, right)
        return stem, False
    if not _is_taken(template, ext, taken, companion):
        return template, False
    if on_exists == "skip":
        return None, True
    n = 1
    while _is_taken("%s_%0*d" % (template, COUNTER_WIDTH, n), ext, taken, companion):
        n += 1
    return "%s_%0*d" % (template, COUNTER_WIDTH, n), False


def settings_text(name, seed, steps, cfg, width, height, fmt, quality, batch_no, batch_count, extra, now):
    """Pure function. The text for the .txt file and for the png metadata."""
    lines = ["saved: " + now.strftime("%Y-%m-%d %H:%M:%S"), "name: " + str(name)]
    if int(seed) >= 0:
        lines.append("seed: %d" % int(seed))
    if int(steps) > 0:
        lines.append("steps: %d" % int(steps))
    if float(cfg) > 0:
        lines.append("cfg: " + cfg_text(cfg))
    lines.append("size: %dx%d" % (int(width), int(height)))
    lines.append("format: " + str(fmt) + ("" if fmt == "png" else " (quality %d)" % int(quality)))
    lines.append("picture: %d of %d" % (int(batch_no), int(batch_count)))
    if str(extra or "").strip():
        lines.append("")
        lines.append(str(extra).strip())
    return "\n".join(lines)


def check_settings(fmt, quality, seed, steps, cfg, on_exists, count, extra_text):
    """Pure function. Plain refusals for values outside what the node accepts."""
    if fmt not in FORMATS:
        raise ValueError("format must be one of: %s, got %r" % (", ".join(FORMATS), fmt))
    if not (1 <= int(quality) <= 100):
        raise ValueError("quality must be from 1 to 100, got %s" % quality)
    if int(seed) < -1:
        raise ValueError("seed must be -1 (not used) or higher, got %s" % seed)
    if not (0 <= int(steps) <= 1000):
        raise ValueError("steps must be from 0 to 1000, got %s" % steps)
    if not (0 <= float(cfg) <= 100):
        raise ValueError("cfg must be from 0 to 100, got %s" % cfg)
    if on_exists not in ON_EXISTS:
        raise ValueError("on_exists must be one of: %s, got %r" % (", ".join(ON_EXISTS), on_exists))
    if int(count) < 1:
        raise ValueError("nothing to save: the images input is empty")
    if len(str(extra_text or "")) > MAX_TEXT:
        raise ValueError("settings_text is too long (%d characters, max %d)" % (len(str(extra_text)), MAX_TEXT))


def plan_saves(existing, pattern, ext, count, name, seed, steps, cfg, width, height, fmt, on_exists, now):
    """Pure function. For `count` pictures: [(stem or None, skipped_flag)], never clashing with `existing` names."""
    taken = {str(n).lower() for n in existing}
    out = []
    for i in range(int(count)):
        vals = token_values(name, seed, steps, cfg, width, height, fmt, i + 1, now)
        stem, skipped = pick_name(stem_template(pattern, vals), ext, taken, on_exists)
        if stem is not None:
            taken.add((stem + ext).lower())
            taken.add((stem + ".txt").lower())
        out.append((stem, skipped))
    return out


def save_info(saved, skipped, width, height, fmt, where, channels, wrote_text):
    """Pure function. A plain report of what happened."""
    n = len(saved)
    if n == 0:
        lines = ["Nothing was saved: every name was already taken (on_exists is skip)."]
    else:
        names = saved[0] if n == 1 else "%s ... %s" % (saved[0], saved[-1])
        lines = ["Saved %d picture%s (%s, %dx%d) to %s: %s" % (n, "" if n == 1 else "s", fmt, width, height, where or "(output folder)", names)]
    if skipped:
        lines.append("Skipped %d picture%s because the name was already taken." % (skipped, "" if skipped == 1 else "s"))
    if wrote_text:
        lines.append("Wrote %d settings text file%s with the same names." % (wrote_text, "" if wrote_text == 1 else "s"))
    if channels == 4 and fmt == "jpeg":
        lines.append("Note: jpeg cannot hold transparency, so the alpha channel was dropped. Use png or webp to keep it.")
    return "\n".join(lines)


class SYSavePack:
    DESCRIPTION = ("Saves pictures into the ComfyUI output folder. The file name is built from tokens "
                   "{date} {time} {name} {seed} {steps} {cfg} {width} {height} {format} {counter} {batch}. "
                   "Never overwrites. Optional settings text file beside every picture (also stored inside png files).")
    CATEGORY = category("Image")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("paths", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The pictures to save. A batch saves every picture."}),
            },
            "optional": {
                "filename_pattern": ("STRING", {"default": "{date}_{name}_{counter}", "tooltip": "File name without ending. Tokens: {date} {time} {name} {seed} {steps} {cfg} {width} {height} {format} {counter} {batch}."}),
                "name": ("STRING", {"default": "image", "tooltip": "Text for the {name} token. Bad file name characters are replaced."}),
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside the output folder, made if missing. May use tokens such as {date}. Empty: the output folder."}),
                "format": (FORMATS, {"default": "png", "tooltip": "File type. png keeps the workflow inside the file."}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "tooltip": "Quality for jpeg and webp. png ignores it."}),
                "seed": ("INT", {"default": 0, "min": -1, "max": 2 ** 53, "tooltip": "Number for the {seed} token. -1 means not used."}),
                "steps": ("INT", {"default": 0, "min": 0, "max": 1000, "tooltip": "Number for the {steps} token. 0 means not used."}),
                "cfg": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "Number for the {cfg} token. 0 means not used."}),
                "settings_text": ("STRING", {"default": "", "multiline": True, "tooltip": "Extra text for the settings file, for example the prompt."}),
                "write_settings_file": ("BOOLEAN", {"default": True, "tooltip": "On: a .txt beside every picture with seed, steps, cfg, size, date and your text."}),
                "on_exists": (ON_EXISTS, {"default": "next number", "tooltip": "When the exact name is taken: use the next number, or skip that picture."}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def run(self, images, filename_pattern="{date}_{name}_{counter}", name="image", subfolder="", format="png", quality=95,
            seed=0, steps=0, cfg=0.0, settings_text="", write_settings_file=True, on_exists="next number",
            prompt=None, extra_pnginfo=None):
        if len(tuple(images.shape)) != 4:
            raise ValueError("the images input is not a picture batch (expected 4 dimensions, got %d)" % len(tuple(images.shape)))
        count, height, width, channels = (int(v) for v in images.shape)
        check_settings(format, quality, seed, steps, cfg, on_exists, count, settings_text)
        now = datetime.now()
        sub = fill_subfolder(subfolder, token_values(name, seed, steps, cfg, width, height, format, 1, now))
        out_root = root_folder("output")
        folder = safe_join(out_root, sub)
        os.makedirs(folder, exist_ok=True)
        ext = EXT[format]
        plan = plan_saves(list_files(folder), filename_pattern, ext, count, name, seed, steps, cfg, width, height, format, on_exists, now)
        chunks = workflow_chunks(prompt, extra_pnginfo) if format == "png" else None
        rel = os.path.relpath(folder, os.path.realpath(out_root))
        rel = "" if rel == "." else rel.replace("\\", "/")
        paths, shown, names, skipped, wrote = [], [], [], 0, 0
        for i, (stem, was_skipped) in enumerate(plan):
            if was_skipped:
                skipped += 1
                continue
            text = settings_text_for(i, count, name, seed, steps, cfg, width, height, format, quality, settings_text, now) if write_settings_file else None
            path = os.path.join(folder, stem + ext)
            c = dict(chunks) if chunks is not None else None
            if c is not None and text is not None:
                c["sy_settings"] = text
            write_image(tensor_to_pil(images[i]), path, WRITE_FMT[format], quality, c)
            if text is not None:
                with open(os.path.join(folder, stem + ".txt"), "x", encoding="utf-8", newline="\n") as f:
                    f.write(text)
                wrote += 1
            paths.append(path)
            names.append(stem + ext)
            shown.append({"filename": stem + ext, "subfolder": rel, "type": "output"})
        info = save_info(names, skipped, width, height, format, rel, channels, wrote)
        return {"ui": {"images": shown}, "result": ("\n".join(paths), info)}


def settings_text_for(i, count, name, seed, steps, cfg, width, height, fmt, quality, extra, now):
    return settings_text(name, seed, steps, cfg, width, height, fmt, quality, i + 1, count, extra, now)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SavePack", SYSavePack)
NODE_DISPLAY_NAME_MAPPINGS["SYSavePack"] = "Save Pack SY"
