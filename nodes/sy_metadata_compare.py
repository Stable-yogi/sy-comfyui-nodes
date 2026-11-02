"""Metadata Compare SY: compares the saved generation info of two pictures and lists what differs. Read only."""
import os
import re

try:
    from ._sy_safe_paths import root_folder, safe_join
    from ._sy_common import category, register
    from .sy_image_metadata_reader import summarize_metadata, MAX_FILE_BYTES
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder, safe_join
    from _sy_common import category, register
    from sy_image_metadata_reader import summarize_metadata, MAX_FILE_BYTES

FIELDS = ("prompt", "negative prompt", "seed", "steps", "cfg", "sampler", "scheduler", "model", "size")
MISSING = "(missing)"
_ALIASES = {
    "seed": "seed", "noise_seed": "seed", "steps": "steps",
    "cfg": "cfg", "cfg scale": "cfg", "sampler": "sampler", "sampler_name": "sampler",
    "scheduler": "scheduler", "schedule type": "scheduler", "model": "model", "size": "size",
}
MAX_CELL_CHARS = 200


def settings_from_info(info, size=None):
    """Pure function. PNG text chunks (a dict) -> dict with the FIELDS that could be found. No data gives {}."""
    info = info or {}
    params, pos, neg, sets, text = summarize_metadata(info, size)
    if not (params or pos or neg or sets or info.get("prompt")):
        return {}
    out = {}
    if pos:
        out["prompt"] = pos
    if neg:
        out["negative prompt"] = neg
    for line in str(sets).split("\n"):
        if ": " not in line:
            continue
        key, val = line.split(": ", 1)
        field = _ALIASES.get(key.strip().lower())
        if field and field not in out:
            out[field] = val.strip()
    if "size" not in out and size:
        out["size"] = "%dx%d" % (size[0], size[1])
    return out


def _norm(value):
    text = re.sub(r"\s+", " ", str(value)).strip()
    try:
        return repr(float(text))
    except ValueError:
        return text


def compare_settings(dict_a, dict_b):
    """Pure function. Two settings dicts -> list of rows (setting, a, b, same). Missing values show as '(missing)'."""
    dict_a = dict_a or {}
    dict_b = dict_b or {}
    rows = []
    for field in FIELDS:
        a = dict_a.get(field)
        b = dict_b.get(field)
        same = (a is None and b is None) or (a is not None and b is not None and _norm(a) == _norm(b))
        rows.append((field, MISSING if a is None else str(a), MISSING if b is None else str(b), same))
    return rows


def _cell(text):
    text = re.sub(r"\s+", " ", str(text)).strip().replace("|", "\\|")
    return text if len(text) <= MAX_CELL_CHARS else text[:MAX_CELL_CHARS - 3] + "..."


def build_report(rows, only_differences=True, note_a="", note_b=""):
    """Pure function. Rows -> (markdown report, identical, number_of_differences)."""
    diffs = sum(1 for r in rows if not r[3])
    lines = []
    for label, note in (("A", note_a), ("B", note_b)):
        if note:
            lines.append("%s: %s" % (label, note))
    if lines:
        lines.append("")
    shown = [r for r in rows if not (only_differences and r[3])]
    if shown:
        lines += ["| Setting | A | B | Result |", "|---|---|---|---|"]
        for name, a, b, same in shown:
            lines.append("| %s | %s | %s | %s |" % (name, _cell(a), _cell(b), "same" if same else "different"))
    else:
        lines.append("Nothing differs in the settings compared.")
    lines.append("")
    lines.append("%d of %d settings differ." % (diffs, len(rows)))
    return "\n".join(lines), diffs == 0, diffs


def _read_one(rel):
    """Find a png inside the input or output folder, return (settings dict, note)."""
    rel = str(rel or "").strip()
    if not rel:
        raise ValueError("a picture path is empty: type a png file name from the input or output folder")
    if not rel.lower().endswith(".png"):
        raise ValueError("only .png files carry this metadata, got %r" % rel)
    safe_join("_check_only", rel)  # rejects '..', absolute paths and drive letters before any folder is asked for
    from PIL import Image

    path = None
    for root in ("input", "output"):
        cand = safe_join(root_folder(root), rel)
        if os.path.isfile(cand):
            path = cand
            break
    if path is None:
        raise ValueError("png file not found in the input or output folder: %s" % rel)
    if os.path.getsize(path) > MAX_FILE_BYTES:
        raise ValueError("file is too big (max %d bytes): %s" % (MAX_FILE_BYTES, rel))
    try:
        with Image.open(path) as img:
            img.load()
            meta = dict(img.info)
            dims = img.size
    except (OSError, SyntaxError, ValueError):
        raise ValueError("%s could not be read as a picture. The file may be damaged." % rel)
    settings = settings_from_info(meta, dims)
    note = "" if settings else "%s holds no generation data (saved without it, or stripped by a site or app)." % rel
    return settings, note


class SYMetadataCompare:
    DESCRIPTION = ("Compares the saved generation info of two png pictures (prompt, negative prompt, seed, steps, cfg, "
                   "sampler, scheduler, model, size) and lists what differs. Reads Forge/A1111 and ComfyUI data. Never changes a file.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "INT")
    RETURN_NAMES = ("report", "identical", "number_of_differences")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a_path": ("STRING", {"default": "", "tooltip": "First png, a file name or sub path inside the input or output folder."}),
                "image_b_path": ("STRING", {"default": "", "tooltip": "Second png, a file name or sub path inside the input or output folder."}),
            },
            "optional": {
                "only_differences": ("BOOLEAN", {"default": True, "tooltip": "On: list only the settings that differ. Off: list every setting."}),
            },
        }

    def run(self, image_a_path, image_b_path, only_differences=True):
        a, note_a = _read_one(image_a_path)
        b, note_b = _read_one(image_b_path)
        report, identical, diffs = build_report(compare_settings(a, b), only_differences, note_a, note_b)
        return (report, identical, diffs)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MetadataCompare", SYMetadataCompare)
NODE_DISPLAY_NAME_MAPPINGS["SYMetadataCompare"] = "Metadata Compare SY"
