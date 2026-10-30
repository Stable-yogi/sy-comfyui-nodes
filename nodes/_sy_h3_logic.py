"""Pure logic for the H3SpeedOptimizer SY and H3LowVRAM SY nodes. No torch, no comfy: runs in the selftest.

Ported from ComfyUI-TeaCache (Apache-2.0). Changed for the SY pack by Stable Yogi.
Licence copy: third_party/ComfyUI-TeaCache/LICENSE. Original idea: the sol-engine MiniMax H3 acceleration line.
"""
import math

SPARSE_MODES = ("auto", "enabled", "disabled")
CACHE_DEVICES = ("gpu", "cpu")
H3_MODEL_CLASS = "MiniMaxH3Model"
MAX_FF_CHUNKS = 64
SPARSE_HEAD_DIM = 128
SPARSE_MIN_SPEEDUP = 1.05
SPARSE_GATE_REL_L2 = 0.02


def _num(name, value, lo, hi):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be a number, got %r" % (name, value))
    if math.isnan(value) or value < lo or value > hi:
        raise ValueError("%s must be between %s and %s, got %r" % (name, lo, hi, value))
    return value


def check_speed_options(first_block_cache, fbc_threshold, fbc_start_percent, fbc_end_percent, fbc_max_consecutive,
                        sparse_attention, sparse_dense_steps_pct, sparse_dense_layers, sparse_tau,
                        sparse_min_video_rows, fbc_cache_device):
    """Check the speed settings. Raises ValueError in plain words. Returns True when the settings are fine."""
    _num("fbc_threshold", fbc_threshold, 0.0, 1.0)
    _num("fbc_start_percent", fbc_start_percent, 0.0, 1.0)
    _num("fbc_end_percent", fbc_end_percent, 0.0, 1.0)
    _num("fbc_max_consecutive", fbc_max_consecutive, 1, 50)
    _num("sparse_dense_steps_pct", sparse_dense_steps_pct, 0.0, 1.0)
    _num("sparse_dense_layers", sparse_dense_layers, 0, 50)
    _num("sparse_tau", sparse_tau, -10.0, 100.0)
    _num("sparse_min_video_rows", sparse_min_video_rows, 0, 1000000)
    if sparse_attention not in SPARSE_MODES:
        raise ValueError("sparse_attention must be one of %s, got %r" % (", ".join(SPARSE_MODES), sparse_attention))
    if fbc_cache_device not in CACHE_DEVICES:
        raise ValueError("fbc_cache_device must be one of %s, got %r" % (", ".join(CACHE_DEVICES), fbc_cache_device))
    if first_block_cache and fbc_start_percent >= fbc_end_percent:
        raise ValueError("fbc_start_percent (%s) must be smaller than fbc_end_percent (%s), or no step can be skipped"
                         % (fbc_start_percent, fbc_end_percent))
    return True


def require_h3_model(type_name, node_name):
    """Raise ValueError unless the diffusion model class name is the MiniMax H3 one."""
    if type_name != H3_MODEL_CLASS:
        raise ValueError("%s needs a MiniMax H3 model, got %s. Connect the MiniMax H3 diffusion model "
                         "(for example minimax_h3_fl2va or ref2va)." % (node_name, type_name))
    return True


def speed_is_noop(first_block_cache, sparse_attention):
    """True when both techniques are off: the node passes the model through."""
    return (not first_block_cache) and sparse_attention == "disabled"


def nearest_step(sigma, sigma_values):
    """Index of the schedule value closest to `sigma` (first one on a tie), and the step count (values - 1)."""
    best, best_d = 0, None
    for i, s in enumerate(sigma_values):
        d = abs(s - sigma)
        if best_d is None or d < best_d:
            best, best_d = i, d
    return best, len(sigma_values) - 1


def fallback_step(sigma, last_sigma, step_index, total_steps):
    """Step clock when the schedule is unknown: sigma falls inside a run and jumps up on a new run.

    Returns (index, total)."""
    if last_sigma is None or sigma > last_sigma + 1e-6:
        idx = 0
    else:
        idx = step_index + (0 if abs(sigma - (last_sigma if last_sigma else -1)) <= 1e-9 else 1)
    return idx, max(idx + 1, total_steps)


def fbc_window_open(enabled, step_index, total_steps, start_percent, end_percent):
    """True while skipping is allowed. The end bound is strict, so the last step always computes."""
    if not enabled or total_steps <= 0:
        return False
    pct = step_index / max(total_steps, 1)
    return start_percent <= pct < end_percent


def fbc_decide(delta, accum, consec, threshold, max_consecutive):
    """One skip decision. Returns (skip, accum, consec)."""
    accum = accum + delta
    if accum < threshold and consec < max_consecutive:
        return True, accum, consec + 1
    return False, 0.0, 0


def sparse_basic_eligible(layer, step_index, total_steps, dense_steps_pct, dense_layers, seq_len, video_start,
                          min_video_rows):
    """The number checks for sparse attention (no tensor needed)."""
    if seq_len is None or video_start is None:
        return False
    if not (0 < video_start < seq_len):
        return False
    if (seq_len - video_start) < min_video_rows:
        return False
    if layer < dense_layers:
        return False
    if step_index < math.ceil(dense_steps_pct * max(total_steps, 1)):
        return False
    return True


def sparse_shape_ok(shape, heads, seq_len, skip_reshape, has_mask):
    """The tensor-shape checks for sparse attention, on a plain shape tuple."""
    if not skip_reshape or has_mask:
        return False
    return len(shape) == 4 and shape[0] == 1 and shape[1] == heads and shape[-1] == SPARSE_HEAD_DIM \
        and seq_len is not None and shape[2] == seq_len


def sparse_gate_passed(rel_l2):
    return rel_l2 <= SPARSE_GATE_REL_L2


def sparse_keep(speedup, mode):
    """Keep the sparse kernel? In auto mode only when at least 5 percent faster than the current backend."""
    return speedup >= SPARSE_MIN_SPEEDUP if mode == "auto" else True


# ---------------------------------------------------------------- low VRAM

def group_sizes(heads, groups):
    """Split `heads` into `groups` near-equal parts (the first parts get the extra head)."""
    if heads < 1 or groups < 1:
        raise ValueError("heads and groups must be 1 or more, got %r and %r" % (heads, groups))
    return [heads // groups + (1 if i < heads % groups else 0) for i in range(groups)]


def plan_low_vram(exact_output, attention_head_groups, feedforward_chunks, min_tokens, heads):
    """Settings the low-VRAM patch uses. Returns (chunks, groups, min_tokens).

    chunks and groups of 1 together mean there is nothing to do (the node passes the model through)."""
    _num("attention_head_groups", attention_head_groups, 1, 56)
    _num("feedforward_chunks", feedforward_chunks, 1, MAX_FF_CHUNKS)
    _num("min_tokens", min_tokens, 256, 1048576)
    if heads < 1:
        raise ValueError("the model reports %r attention heads, cannot plan head groups" % (heads,))
    chunks = max(1, min(int(feedforward_chunks), MAX_FF_CHUNKS))
    groups = 1 if exact_output else max(1, min(int(attention_head_groups), heads))
    return chunks, groups, max(0, int(min_tokens))


def lowvram_is_noop(chunks, groups):
    return groups <= 1 and chunks <= 1


def block_patch_keys(index):
    """The three object-patch names for one transformer block."""
    base = "diffusion_model.blocks.%d" % index
    return base + ".forward", base + ".mlp.forward", base + ".attn.forward"


def mlp_chunk_active(chunks, rows, min_tokens):
    """True when the feedforward is split for a sequence of `rows` tokens."""
    return not (chunks <= 1 or rows <= min_tokens)


def attention_groups_for(rows, min_tokens, head_groups, heads):
    """Head groups used for one attention call (1 = no grouping)."""
    if rows > min_tokens:
        return min(int(head_groups), heads)
    return 1


def split_sizes(total, parts):
    """Row counts per chunk the same way torch.chunk splits `total` rows into at most `parts` chunks."""
    if total < 1 or parts < 1:
        raise ValueError("total and parts must be 1 or more, got %r and %r" % (total, parts))
    size = -(-total // parts)
    out = []
    left = total
    while left > 0:
        out.append(min(size, left))
        left -= size
    return out
