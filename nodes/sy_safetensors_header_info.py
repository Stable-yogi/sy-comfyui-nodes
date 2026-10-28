"""Safetensors Header Info SY: reads only the small JSON header of a .safetensors file and reports what is inside."""
import json
import os
import struct

try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, NONE_NAME

MAX_HEADER_BYTES = 20 * 1024 * 1024
KINDS = ("checkpoints", "loras", "vae")


def read_header(path, max_header=MAX_HEADER_BYTES):
    """Pure file function. Reads only the 8-byte length and the JSON header. Never reads tensor data."""
    size = os.path.getsize(path)
    if size < 8:
        raise ValueError("file is too small to be a safetensors file")
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
        if n > max_header:
            raise ValueError("header claims %d bytes, more than the %d byte limit. This is not a normal safetensors file." % (n, max_header))
        if n + 8 > size:
            raise ValueError("header is longer than the file. The file is damaged or not a safetensors file.")
        raw = f.read(n)
    try:
        header = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise ValueError("header is not valid JSON. The file is damaged or not a safetensors file.")
    if not isinstance(header, dict):
        raise ValueError("header is not a JSON object")
    return header


def summarize_header(header):
    """Pure function. Returns a dict: tensor_count, dtype_counts, total_params, metadata_keys."""
    meta = header.get("__metadata__") or {}
    tensors = {k: v for k, v in header.items() if k != "__metadata__"}
    dtypes = {}
    total = 0
    for name, info in tensors.items():
        if not isinstance(info, dict) or "dtype" not in info or "shape" not in info:
            raise ValueError("tensor %r has no dtype/shape in the header" % name)
        dtypes[info["dtype"]] = dtypes.get(info["dtype"], 0) + 1
        n = 1
        for d in info["shape"]:
            n *= int(d)
        total += n
    return {"tensor_count": len(tensors), "dtype_counts": dtypes, "total_params": total,
            "metadata_keys": sorted(meta.keys()) if isinstance(meta, dict) else []}


def format_report(summary, file_size=None):
    """Pure function. Plain-text report."""
    lines = []
    lines.append("Tensors: %d" % summary["tensor_count"])
    total = summary["total_params"]
    lines.append("Parameters (estimate from shapes): %d (about %.2f billion)" % (total, total / 1e9))
    if file_size is not None:
        lines.append("File size: %.2f GB" % (file_size / 1e9))
    if summary["dtype_counts"]:
        parts = ["%s x%d" % (k, v) for k, v in sorted(summary["dtype_counts"].items())]
        lines.append("Data types: " + ", ".join(parts))
    keys = summary["metadata_keys"]
    lines.append("Metadata keys (%d): %s" % (len(keys), ", ".join(keys) if keys else "none"))
    return "\n".join(lines)


def split_choice(choice):
    """Pure function. 'loras/sub/a.safetensors' -> ('loras', 'sub/a.safetensors')."""
    if not isinstance(choice, str) or "/" not in choice:
        raise ValueError("pick a file from the list")
    kind, name = choice.split("/", 1)
    if kind not in KINDS:
        raise ValueError("unknown folder %r. Pick a file from the list." % kind)
    return kind, name


def _choices():
    out = []
    for kind in KINDS:
        out.extend("%s/%s" % (kind, n) for n in list_names(kind) if n.lower().endswith(".safetensors"))
    return out or [NONE_NAME]


class SYSafetensorsHeaderInfo:
    DESCRIPTION = "Shows what is inside a .safetensors model file (tensor count, data types, parameter estimate, metadata keys) without loading the model."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("report",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model_file": (_choices(), {"tooltip": "A checkpoint, LoRA or VAE file. Only its small header is read."})}}

    def run(self, model_file):
        if model_file == NONE_NAME:
            raise ValueError("no .safetensors files were found in the checkpoints, loras or vae folders")
        kind, name = split_choice(model_file)
        path = find_file(kind, name)
        summary = summarize_header(read_header(path))
        return (format_report(summary, os.path.getsize(path)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SafetensorsHeaderInfo", SYSafetensorsHeaderInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYSafetensorsHeaderInfo"] = "Safetensors Header Info SY"
