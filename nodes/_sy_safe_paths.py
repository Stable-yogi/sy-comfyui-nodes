"""Safe file helpers shared by the SY file nodes. Holds no nodes, only pure functions.

Every path stays inside ComfyUI's input or output folder. The folders are asked for lazily.
"""
import os
import re
from datetime import datetime


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff")
TOKENS = ("date", "time", "seed", "counter")
EXTRA_TOKENS = ("width", "height", "batch", "model", "input")  # only the Save Image node offers these
COUNTER_WIDTH = 5
MAX_NAME_LENGTH = 150
_BAD_NAME_CHARS = set('<>:"/\\|?*')
_RESERVED = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}
_DRIVE = re.compile(r"^[A-Za-z]:")


def safe_join(base, sub):
    """Join `sub` under `base`. Refuses absolute paths, drive letters, network paths, '..' and symlink escape."""
    if not isinstance(base, str) or not base:
        raise ValueError("base folder is missing")
    sub = "" if sub is None else str(sub).strip()
    if "\x00" in sub:
        raise ValueError("path contains a hidden null character: remove it")
    if sub.startswith(("/", "\\")):
        raise ValueError("path must be relative to the ComfyUI folder, not start with a slash: %r" % sub)
    if _DRIVE.match(sub):
        raise ValueError("path must not contain a drive letter: %r" % sub)
    if ":" in sub:
        raise ValueError("path must not contain a colon: %r" % sub)
    parts = [p for p in re.split(r"[\\/]+", sub) if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise ValueError("path must not contain '..': %r" % sub)
    base_real = os.path.realpath(base)
    target = os.path.realpath(os.path.join(base_real, *parts)) if parts else base_real
    try:
        inside = os.path.commonpath([base_real, target]) == base_real
    except ValueError:  # different drives
        inside = False
    if not inside:
        raise ValueError("path leaves the allowed folder: %r" % sub)
    return target


def check_filename(name):
    """Return `name` if it is a plain file name. Raise ValueError otherwise."""
    name = str(name)
    if not name.strip():
        raise ValueError("file name is empty: type a name")
    if name != name.strip() or name.endswith("."):
        raise ValueError("file name must not start or end with a space, or end with a dot: %r" % name)
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError("file name is too long (%d characters, max %d)" % (len(name), MAX_NAME_LENGTH))
    if name in (".", ".."):
        raise ValueError("file name is not allowed: %r" % name)
    bad = sorted(c for c in set(name) if c in _BAD_NAME_CHARS or ord(c) < 32)
    if bad:
        raise ValueError("file name has characters that are not allowed %r. Use the subfolder box for folders." % "".join(bad))
    if name.split(".")[0].lower() in _RESERVED:
        raise ValueError("file name is reserved by Windows: %r" % name)
    return name


def clean_extension(ext):
    ext = str(ext or "").strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    if ext and not re.fullmatch(r"\.[a-z0-9]{1,8}", ext):
        raise ValueError("extension must be letters and digits only, like .png: %r" % ext)
    return ext


def parse_extensions(text, default=IMAGE_EXTENSIONS):
    """'png, .JPG' -> ('.png', '.jpg'). Empty text gives `default`."""
    items = [t for t in re.split(r"[,\s;]+", str(text or "")) if t]
    if not items:
        return tuple(default)
    out = []
    for t in items:
        e = clean_extension(t)
        if e and e not in out:
            out.append(e)
    return tuple(out)


def clean_token(value, limit=60):
    """Make a free text safe inside a file name: no folder, no extension, no forbidden characters."""
    text = os.path.splitext(os.path.basename(str(value or "").replace("\\", "/")))[0]
    text = "".join("_" if (c in _BAD_NAME_CHARS or ord(c) < 32) else c for c in text).strip(" .")
    return text[:limit]


def _tokens_in(pattern, extra=False):
    allowed = TOKENS + EXTRA_TOKENS if extra else TOKENS
    found = re.findall(r"\{([^{}]*)\}", pattern)
    for t in found:
        if t not in allowed:
            raise ValueError("unknown token {%s} in the file name pattern. Allowed: %s" % (t, " ".join("{%s}" % a for a in allowed)))
    rest = re.sub(r"\{[^{}]*\}", "", pattern)
    if "{" in rest or "}" in rest:
        raise ValueError("file name pattern has a lonely { or }: %r" % pattern)
    if found.count("counter") > 1:
        raise ValueError("use {counter} only once in the file name pattern")
    return found


def expand_pattern(pattern, seed=0, now=None, counter=None, extra=None):
    """Replace {date} {time} {seed} {counter}. With counter=None the {counter} token is kept for later.

    `extra` (a dict with width, height, batch, model, input) also turns on those five tokens.
    """
    pattern = str(pattern)
    _tokens_in(pattern, extra is not None)
    now = now or datetime.now()
    out = pattern.replace("{date}", now.strftime("%Y-%m-%d"))
    out = out.replace("{time}", now.strftime("%H%M%S"))
    out = out.replace("{seed}", str(int(seed)))
    if extra is not None:
        for key in EXTRA_TOKENS:
            val = extra.get(key, "")
            out = out.replace("{%s}" % key, clean_token(val) if key in ("model", "input") else str(int(val or 0)))
    if counter is not None:
        out = out.replace("{counter}", "%0*d" % (COUNTER_WIDTH, int(counter)))
    return out


def _counter_regex(expanded, exts):
    left, right = expanded.split("{counter}", 1)
    alt = "|".join(re.escape(e) for e in exts)
    return re.compile("^" + re.escape(left) + r"(\d+)" + re.escape(right) + "(?:" + alt + ")$", re.I)


def plan_names(existing, pattern, ext, count, seed=0, now=None, companion=None, extra=None):
    """Pure function. Pick `count` new file names that do not clash with `existing` names.

    With {counter} in the pattern the numbers continue after the highest one found.
    Without it the plain name is used when free, then _00001, _00002 and so on.
    `companion` is a second extension (like .txt) that must also be free.
    """
    pattern = str(pattern)
    if not pattern.strip():
        raise ValueError("file name pattern is empty: type a name such as image_{counter}")
    count = int(count)
    if count < 1:
        raise ValueError("nothing to save: count must be at least 1")
    ext = clean_extension(ext)
    companion = clean_extension(companion) if companion else ""
    exts = [e for e in (ext, companion) if e]
    taken = {str(n).lower() for n in existing}
    _tokens_in(pattern, extra is not None)
    expanded = expand_pattern(pattern, seed, now, extra=extra)
    names = []
    if "{counter}" in expanded:
        rx = _counter_regex(expanded, exts)
        highest = 0
        for n in taken:
            m = rx.match(n)
            if m:
                highest = max(highest, int(m.group(1)))
        for i in range(count):
            names.append(check_filename(expanded.replace("{counter}", "%0*d" % (COUNTER_WIDTH, highest + 1 + i)) + ext))
        return names
    base = check_filename(expanded)
    n = 0
    while len(names) < count:
        stem = base if n == 0 else "%s_%0*d" % (base, COUNTER_WIDTH, n)
        n += 1
        if any((stem + e).lower() in taken for e in exts):
            continue
        taken.update((stem + e).lower() for e in exts)
        names.append(check_filename(stem + ext))
    return names


def list_files(folder, exts=None):
    """Names of the files directly in `folder` (no sub folders), sorted ignoring case. Missing folder gives []."""
    if not os.path.isdir(folder):
        return []
    exts = tuple(e.lower() for e in exts) if exts else None
    out = []
    for n in os.listdir(folder):
        if not os.path.isfile(os.path.join(folder, n)):
            continue
        if exts and os.path.splitext(n)[1].lower() not in exts:
            continue
        out.append(n)
    return sorted(out, key=lambda s: (s.lower(), s))


def pick_index(total, index):
    total = int(total)
    if total <= 0:
        raise ValueError("the folder has no matching files")
    return int(index) % total


def root_folder(root):
    """The input or the output folder of ComfyUI, asked for lazily."""
    import folder_paths
    if root == "input":
        return folder_paths.get_input_directory()
    if root == "output":
        return folder_paths.get_output_directory()
    if root == "temp":
        return folder_paths.get_temp_directory()
    raise ValueError("root must be 'input' or 'output', got %r" % (root,))


def tensor_to_pil(tensor):
    """One image of a ComfyUI IMAGE batch (H, W, C floats 0..1) to a PIL picture."""
    import numpy as np
    from PIL import Image
    arr = np.clip(255.0 * tensor.cpu().numpy(), 0, 255).astype(np.uint8)
    if arr.ndim == 2:
        return Image.fromarray(arr, "L")
    if arr.shape[2] == 1:
        return Image.fromarray(arr[:, :, 0], "L")
    if arr.shape[2] == 4:
        return Image.fromarray(arr, "RGBA")
    return Image.fromarray(arr[:, :, :3], "RGB")


FORMATS = {"png": ".png", "jpg": ".jpg", "webp": ".webp"}


def write_image(pil, path, fmt, quality, text_chunks=None):
    """Write a PIL picture to a NEW file (never overwrites). text_chunks only apply to png."""
    if fmt not in FORMATS:
        raise ValueError("format must be png, jpg or webp, got %r" % (fmt,))
    quality = int(quality)
    if fmt == "png":
        from PIL.PngImagePlugin import PngInfo
        info = PngInfo()
        for k, v in (text_chunks or {}).items():
            info.add_text(k, v)
        kwargs = {"format": "PNG", "pnginfo": info, "compress_level": 4}
    elif fmt == "jpg":
        if pil.mode != "RGB":
            pil = pil.convert("RGB")
        kwargs = {"format": "JPEG", "quality": quality}
    else:
        kwargs = {"format": "WEBP", "quality": quality}
    try:
        with open(path, "xb") as f:
            pil.save(f, **kwargs)
    except FileExistsError:
        raise ValueError("a file with this name appeared while saving: %s. Run it again." % os.path.basename(path))


def workflow_chunks(prompt, extra_pnginfo):
    """Text chunks for a png: the prompt and workflow as JSON text."""
    import json
    chunks = {}
    if prompt is not None:
        chunks["prompt"] = json.dumps(prompt)
    if isinstance(extra_pnginfo, dict):
        for k, v in extra_pnginfo.items():
            chunks[str(k)] = json.dumps(v)
    return chunks


def date_subfolder(subfolder, now=None):
    """'SY' -> 'SY/2026-10-28'. Empty subfolder gives just the date."""
    day = (now or datetime.now()).strftime("%Y-%m-%d")
    sub = str(subfolder or "").strip().strip("/\\")
    return sub + "/" + day if sub else day


def save_images(images, subfolder, pattern, fmt, quality, seed=0, captions=None, prompt=None, extra_pnginfo=None, now=None,
                root="output", extra=None):
    """Save an IMAGE batch into <root>/<subfolder> (root: output, or temp for a preview). Returns (saved_paths, ui_images).

    `captions` (a list, one text per picture) also writes a same-name .txt file next to each picture.
    `extra` (model and input text) turns on the {width} {height} {batch} {model} {input} tokens.
    """
    out_root = root_folder(root)
    folder = safe_join(out_root, subfolder)
    os.makedirs(folder, exist_ok=True)
    count = int(images.shape[0])
    if extra is not None:
        extra = dict(extra, width=int(images.shape[2]), height=int(images.shape[1]), batch=count)
    names = plan_names(list_files(folder), pattern, FORMATS[fmt], count, seed, now,
                       companion=".txt" if captions is not None else None, extra=extra)
    chunks = workflow_chunks(prompt, extra_pnginfo) if fmt == "png" else None
    rel = os.path.relpath(folder, os.path.realpath(out_root))
    rel = "" if rel == "." else rel.replace("\\", "/")
    paths, ui = [], []
    for i, name in enumerate(names):
        path = os.path.join(folder, name)
        write_image(tensor_to_pil(images[i]), path, fmt, quality, chunks)
        if captions is not None:
            txt = os.path.splitext(path)[0] + ".txt"
            with open(txt, "x", encoding="utf-8", newline="\n") as f:
                f.write(captions[i if i < len(captions) else -1])
        paths.append(path)
        ui.append({"filename": name, "subfolder": rel, "type": root})
    return paths, ui
