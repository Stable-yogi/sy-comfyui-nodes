"""Krea2 Conditioning Rebalance SY: gives each of the 12 text layers its own gain, then one global gain.

Ported from: comfyui-krea2-conditioning (ConditioningKrea2Rebalance)
Original author: Hu White. Licence: Apache-2.0 (copy in third_party/comfyui-krea2-conditioning/LICENSE).
Copyright 2026 Hu White.
Changed by Stable Yogi (renamed, SY standard).

Krea 2 reads its prompt as a stack of 12 text layers packed into one tensor (B, seq, 12*D).
This node reshapes that tensor to see the layer axis, multiplies each layer by its own gain,
can hold the overall size (RMS) constant, then applies a global multiplier. Masks and pooled
outputs are left alone.
"""
from __future__ import annotations

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

# Preset per-layer weight profiles (12 taps, shallow -> deep).
PRESET_WEIGHTS = {
    "balanced": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.5, 5.0, 1.1, 4.0, 1.0],
    "detail": [0.8, 0.8, 0.9, 0.9, 1.0, 1.0, 1.2, 3.0, 6.0, 1.5, 5.0, 1.2],
    "subtle": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 2.0, 1.0, 1.5, 1.0],
    "uniform": [1.0] * 12,
}

PRESET_NAMES = ["balanced", "detail", "subtle", "uniform", "custom"]


def parse_weights(text):
    """Pure function. Turn 'a, b; c' into a list of floats. Needs at least 2 numbers."""
    if text is None:
        raise ValueError("per_layer_weights is empty.")
    parts = [p.strip() for p in str(text).replace(";", ",").split(",") if p.strip() != ""]
    try:
        vals = [float(p) for p in parts]
    except ValueError as exc:
        raise ValueError(f"per_layer_weights has a non-numeric entry: {exc}") from exc
    if len(vals) < 2:
        raise ValueError("per_layer_weights needs at least 2 values.")
    return vals


def resolve_weights(preset, per_layer_weights):
    """Pure function. The weight list for a preset name ('custom' reads the text; unknown names use 'balanced')."""
    if preset == "custom":
        return parse_weights(per_layer_weights)
    return PRESET_WEIGHTS.get(preset, PRESET_WEIGHTS["balanced"])


def weights_text(weights):
    """Pure function. The default text shown in the per_layer_weights box."""
    return ", ".join(str(w) for w in weights)


def _rms(t):
    """Root-mean-square over every dim except the batch (dim 0). Returns shape (B,)."""
    return t.pow(2).mean(dim=tuple(range(1, t.dim()))).sqrt()


def _scale_cond_tensor(t, multiplier, per_layer_weights=None, renormalize=False):
    """Scale one (B, seq, N*D) tensor per layer; optionally keep its RMS; then apply the multiplier."""
    import torch

    if per_layer_weights is None or len(per_layer_weights) <= 1:
        return t * multiplier

    flat = t.shape[-1]
    n_layers = len(per_layer_weights)
    if flat % n_layers != 0:
        return t * multiplier

    orig_dtype = t.dtype
    ref_rms = _rms(t.float()) if renormalize else None
    t = t.float()
    t = t.view(*t.shape[:-1], n_layers, flat // n_layers)
    gains = torch.tensor(list(per_layer_weights), dtype=t.dtype, device=t.device)
    t = t * gains.view(*([1] * (t.dim() - 2)), n_layers, 1)
    t = t.view(*t.shape[:-2], flat)

    if renormalize and ref_rms is not None:
        new_rms = _rms(t).clamp_min(1e-8)
        t = t * (ref_rms / new_rms).view(-1, *([1] * (t.dim() - 1)))

    return t.to(orig_dtype) * multiplier


def scale_conditioning(structure, multiplier, per_layer_weights=None, renormalize=False):
    """Scale every conditioning tensor inside a ComfyUI CONDITIONING structure. Leaves masks and other payloads alone."""
    import torch

    if isinstance(structure, list):
        out = []
        for item in structure:
            if (
                isinstance(item, (list, tuple))
                and len(item) == 2
                and isinstance(item[0], torch.Tensor)
                and isinstance(item[1], dict)
            ):
                cond_t, extras = item
                out.append(
                    [
                        _scale_cond_tensor(cond_t, multiplier, per_layer_weights, renormalize),
                        dict(extras),
                    ]
                )
            else:
                out.append(scale_conditioning(item, multiplier, per_layer_weights, renormalize))
        return out
    if isinstance(structure, torch.Tensor):
        return _scale_cond_tensor(structure, multiplier, per_layer_weights, renormalize)
    if isinstance(structure, dict):
        return {k: scale_conditioning(v, multiplier, per_layer_weights, renormalize) for k, v in structure.items()}
    return structure


class SYKrea2ConditioningRebalance:
    DESCRIPTION = "Rebalances Krea 2's 12 text layers one by one, then applies a global gain. Keeps the overall strength by default."
    CATEGORY = category("Utility")
    FUNCTION = "rebalance"
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning": ("CONDITIONING", {"tooltip": "The encoded prompt (positive or negative) to rebalance."}),
                "preset": (
                    PRESET_NAMES,
                    {
                        "default": "balanced",
                        "tooltip": "Named per-layer gain profile. Pick custom to type your own gains below.",
                    },
                ),
                "per_layer_weights": (
                    "STRING",
                    {
                        "default": weights_text(PRESET_WEIGHTS["balanced"]),
                        "multiline": False,
                        "tooltip": "Comma-separated gains, one per text layer (12 for Krea 2). Used only when preset is custom.",
                    },
                ),
                "multiplier": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": -1000.0,
                        "max": 1000.0,
                        "step": 0.01,
                        "tooltip": "Global gain after the per-layer gains. Keep near 1.0; higher values can oversaturate.",
                    },
                ),
                "renormalize": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Keep the overall strength the same, so only the balance between layers changes.",
                    },
                ),
            }
        }

    def rebalance(self, conditioning, preset="balanced", per_layer_weights="", multiplier=1.0, renormalize=True):
        weights = resolve_weights(preset, per_layer_weights)
        return (scale_conditioning(conditioning, multiplier, weights, renormalize),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Krea2ConditioningRebalance", SYKrea2ConditioningRebalance)
