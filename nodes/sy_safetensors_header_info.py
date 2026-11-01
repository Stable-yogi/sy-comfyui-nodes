"""Safetensors Header Info SY: reads only the small JSON header of a .safetensors file and reports what is inside."""
import os

try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file, NONE_NAME
    from ._sy_a2_files import MAX_HEADER_BYTES, read_header, kind_guess, main_dtype_text, metadata_lines, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file, NONE_NAME
    from _sy_a2_files import MAX_HEADER_BYTES, read_header, kind_guess, main_dtype_text, metadata_lines, size_text

KINDS = ("checkpoints", "loras", "vae", "diffusion_models", "text_encoders")


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


def one_line_summary(header, file_size=None):
    """Pure function. One plain line: what the file looks like, its main data type, size and parameter count."""
    summary = summarize_header(header)
    parts = [kind_guess(header), main_dtype_text(header), "%.2f billion parameters" % (summary["total_params"] / 1e9)]
    if file_size is not None:
        parts.append(size_text(file_size))
    return ", ".join(parts)


def _choices():
    out = []
    for kind in KINDS:
        out.extend("%s/%s" % (kind, n) for n in list_names(kind) if n.lower().endswith(".safetensors"))
    return out or [NONE_NAME]


class SYSafetensorsHeaderInfo:
    DESCRIPTION = ("Shows what is inside a .safetensors model file without loading it: tensor count, data types, parameter estimate, "
                   "metadata keys. Also gives a one-line summary (looks like a LoRA, VAE, checkpoint ..., main data type, size) "
                   "and the metadata values, such as what a LoRA was trained on. Lists checkpoints, loras, vae, diffusion models and text encoders.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("report", "summary", "metadata")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"model_file": (_choices(), {"tooltip": "A model file, for example loras/my_style.safetensors. Only its small header is read, so it is fast."})}}

    def run(self, model_file):
        if model_file == NONE_NAME:
            raise ValueError("no .safetensors files were found in the checkpoints, loras or vae folders")
        kind, name = split_choice(model_file)
        path = find_file(kind, name)
        header = read_header(path)
        summary = summarize_header(header)
        size = os.path.getsize(path)
        return (format_report(summary, size), one_line_summary(header, size), metadata_lines(header) or "no metadata in this file")


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SafetensorsHeaderInfo", SYSafetensorsHeaderInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYSafetensorsHeaderInfo"] = "Safetensors Header Info SY"
