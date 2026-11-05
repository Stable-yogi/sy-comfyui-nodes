"""Pure helpers for the batch A2 utility nodes (header reading, file kind guess, plain notes for loaders). No node inside."""
import json
import os
import struct

MAX_HEADER_BYTES = 20 * 1024 * 1024

DTYPE_NAMES = {
    "F64": "fp64", "F32": "fp32", "F16": "fp16", "BF16": "bf16",
    "F8_E4M3": "fp8 e4m3", "F8_E5M2": "fp8 e5m2", "F8_E4M3FN": "fp8 e4m3",
    "I64": "int64", "I32": "int32", "I16": "int16", "I8": "int8", "U8": "uint8", "BOOL": "bool",
}


def read_header(path, max_header=MAX_HEADER_BYTES):
    """Reads only the 8-byte length and the JSON header of a .safetensors file. Never reads tensor data."""
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


def dtype_label(code):
    """'BF16' -> 'bf16'. Unknown codes are shown as they are."""
    return DTYPE_NAMES.get(str(code).upper(), str(code))


def params_by_dtype(header):
    """Pure function. {'BF16': 1234, ...}: how many parameters sit in each data type (from the shapes)."""
    out = {}
    for name, info in header.items():
        if name == "__metadata__" or not isinstance(info, dict) or "shape" not in info or "dtype" not in info:
            continue
        n = 1
        for d in info["shape"]:
            n *= int(d)
        out[info["dtype"]] = out.get(info["dtype"], 0) + n
    return out


def main_dtype_text(header):
    """Pure function. 'bf16 (100%)' or 'mixed: bf16 62%, fp8 e4m3 38%'. Empty header gives 'no tensors'."""
    per = params_by_dtype(header)
    total = sum(per.values())
    if total <= 0:
        return "no tensors"
    ranked = sorted(per.items(), key=lambda kv: -kv[1])
    if len(ranked) == 1:
        return "%s (100%%)" % dtype_label(ranked[0][0])
    return "mixed: " + ", ".join("%s %d%%" % (dtype_label(k), round(100.0 * v / total)) for k, v in ranked[:4])


def kind_guess(header):
    """Pure function. A plain guess of what the file is from its tensor names: LoRA, VAE, checkpoint, diffusion model,
    text encoder or unknown."""
    keys = [k for k in header if k != "__metadata__"]
    if not keys:
        return "empty file"
    low = [k.lower() for k in keys]
    if any(("lora_down" in k or "lora_up" in k or "lora_a" in k or "lora_b" in k or ".lora." in k) for k in low):
        return "LoRA"
    has_unet = any(k.startswith("model.diffusion_model.") for k in low)
    has_vae = any(k.startswith(("first_stage_model.", "vae.")) for k in low)
    has_text = any(k.startswith(("cond_stage_model.", "conditioner.", "text_encoders.")) for k in low)
    if has_unet and (has_vae or has_text):
        return "full checkpoint (model + VAE/text encoder)"
    # a VAE whose decoder is a transformer (MiniMax H3) has "decoder.transformer_blocks": the VAE shape wins over block words
    vae_shape = any(k.startswith(("encoder.down", "decoder.up", "decoder.conv_in", "encoder.conv_in", "quant_conv", "post_quant_conv")) for k in low)
    if has_unet or (not vae_shape and any(("double_blocks" in k or "single_blocks" in k or "transformer_blocks" in k or "input_blocks" in k) for k in low)):
        return "diffusion model"
    if vae_shape:
        return "VAE"
    if any(("text_model" in k or "embed_tokens" in k or k.startswith(("shared.", "encoder.block"))) for k in low):
        return "text encoder"
    return "unknown"


def metadata_lines(header, max_keys=30, max_value=160):
    """Pure function. 'key: value' lines from the header metadata. Long values are cut. Nothing when there is none."""
    meta = header.get("__metadata__") or {}
    if not isinstance(meta, dict) or not meta:
        return ""
    lines = []
    for k in sorted(meta)[:max_keys]:
        v = " ".join(str(meta[k]).split())
        lines.append("%s: %s" % (k, v if len(v) <= max_value else v[:max_value - 3] + "..."))
    extra = len(meta) - max_keys
    if extra > 0:
        lines.append("... and %d more keys" % extra)
    return "\n".join(lines)


def gguf_refusal(name, loader, use_instead="the GGUF loader node"):
    """Pure function. A plain sentence when a .gguf file is given to a loader that cannot read it, else ''."""
    if str(name).lower().endswith(".gguf"):
        return ("%r is a GGUF file. %s cannot read GGUF: use %s for it, or pick a .safetensors file."
                % (name, loader, use_instead))
    return ""


def size_text(num_bytes):
    n = float(num_bytes)
    if n < 0:
        raise ValueError("size cannot be negative, got %s" % num_bytes)
    if n >= 1024 ** 3:
        return "%.2f GB" % (n / 1024 ** 3)
    if n >= 1024 ** 2:
        return "%.0f MB" % (n / 1024 ** 2)
    return "%.0f KB" % (n / 1024)
