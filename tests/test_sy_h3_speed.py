import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_h3_logic as L
import sy_h3_speed as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


GOOD = dict(first_block_cache=True, fbc_threshold=0.08, fbc_start_percent=0.15, fbc_end_percent=0.95,
            fbc_max_consecutive=3, sparse_attention="auto", sparse_dense_steps_pct=0.2, sparse_dense_layers=2,
            sparse_tau=1.0, sparse_min_video_rows=4096, fbc_cache_device="gpu")


def run():
    n = 0
    # registration and names
    assert set(m.NODE_CLASS_MAPPINGS) == {"SYH3SpeedOptimizer", "SYH3LowVRAM"}; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYH3SpeedOptimizer"] == "H3SpeedOptimizer SY"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYH3LowVRAM"] == "H3LowVRAM SY"; n += 1
    # same widget order as the original nodes
    req = list(m.SYH3SpeedOptimizer.INPUT_TYPES()["required"])
    opt = list(m.SYH3SpeedOptimizer.INPUT_TYPES()["optional"])
    assert req + opt == ["model", "first_block_cache", "fbc_threshold", "fbc_start_percent", "fbc_end_percent",
                         "fbc_max_consecutive", "sparse_attention", "sparse_dense_steps_pct", "sparse_dense_layers",
                         "sparse_tau", "sparse_min_video_rows", "fbc_cache_device", "verbose", "enable_speedup"]; n += 1
    assert list(m.SYH3LowVRAM.INPUT_TYPES()["required"]) + list(m.SYH3LowVRAM.INPUT_TYPES()["optional"]) == [
        "model", "enable_low_vram", "exact_output", "attention_head_groups", "feedforward_chunks", "min_tokens"]; n += 1
    assert m.SYH3SpeedOptimizer.RETURN_NAMES == ("model", "speedup_enabled"); n += 1
    assert m.SYH3LowVRAM.RETURN_TYPES == ("MODEL",); n += 1
    # option checks
    assert L.check_speed_options(**GOOD) is True; n += 1
    assert raises(L.check_speed_options, **dict(GOOD, sparse_attention="maybe")); n += 1
    assert raises(L.check_speed_options, **dict(GOOD, fbc_cache_device="tpu")); n += 1
    assert raises(L.check_speed_options, **dict(GOOD, fbc_threshold=2.0)); n += 1
    assert raises(L.check_speed_options, **dict(GOOD, fbc_start_percent=0.9, fbc_end_percent=0.5)); n += 1
    assert L.check_speed_options(**dict(GOOD, first_block_cache=False, fbc_start_percent=0.9, fbc_end_percent=0.5)); n += 1
    assert raises(L.check_speed_options, **dict(GOOD, fbc_max_consecutive=0)); n += 1
    assert raises(L.check_speed_options, **dict(GOOD, sparse_tau=float("nan"))); n += 1
    assert raises(L.require_h3_model, "UNet", "x"); n += 1
    assert L.require_h3_model("MiniMaxH3Model", "x"); n += 1
    assert L.speed_is_noop(False, "disabled") and not L.speed_is_noop(True, "disabled") \
        and not L.speed_is_noop(False, "auto"); n += 1
    # step clock
    assert L.nearest_step(0.5, [1.0, 0.75, 0.5, 0.25, 0.0]) == (2, 4); n += 1
    assert L.nearest_step(0.6, [1.0, 0.75, 0.5, 0.25, 0.0]) == (2, 4); n += 1
    assert L.fallback_step(0.9, None, -1, 0) == (0, 1); n += 1
    assert L.fallback_step(0.8, 0.9, 0, 1) == (1, 2); n += 1
    assert L.fallback_step(0.95, 0.8, 3, 4) == (0, 4); n += 1
    # skip window and decision
    assert L.fbc_window_open(True, 3, 20, 0.15, 0.95) and not L.fbc_window_open(True, 2, 20, 0.15, 0.95); n += 1
    assert not L.fbc_window_open(True, 19, 20, 0.15, 0.95) and not L.fbc_window_open(False, 5, 20, 0.0, 1.0); n += 1
    assert not L.fbc_window_open(True, 1, 0, 0.0, 1.0); n += 1
    assert L.fbc_decide(0.03, 0.0, 0, 0.08, 3) == (True, 0.03, 1); n += 1
    assert L.fbc_decide(0.06, 0.03, 1, 0.08, 3) == (False, 0.0, 0); n += 1
    assert L.fbc_decide(0.001, 0.0, 3, 0.08, 3) == (False, 0.0, 0); n += 1
    # sparse attention checks
    assert L.sparse_basic_eligible(2, 10, 50, 0.2, 2, 8000, 3000, 4096) is True; n += 1
    assert not L.sparse_basic_eligible(1, 10, 50, 0.2, 2, 8000, 3000, 4096); n += 1
    assert not L.sparse_basic_eligible(2, 9, 50, 0.2, 2, 8000, 3000, 4096); n += 1
    assert not L.sparse_basic_eligible(2, 10, 50, 0.2, 2, 8000, 6000, 4096); n += 1
    assert not L.sparse_basic_eligible(2, 10, 50, 0.2, 2, None, 3000, 4096); n += 1
    assert L.sparse_shape_ok((1, 8, 100, 128), 8, 100, True, False); n += 1
    assert not L.sparse_shape_ok((1, 8, 100, 64), 8, 100, True, False); n += 1
    assert not L.sparse_shape_ok((1, 8, 100, 128), 8, 100, False, False); n += 1
    assert not L.sparse_shape_ok((1, 8, 100, 128), 8, 100, True, True); n += 1
    assert L.sparse_gate_passed(0.02) and not L.sparse_gate_passed(0.0201); n += 1
    assert L.sparse_keep(1.05, "auto") and not L.sparse_keep(1.04, "auto") and L.sparse_keep(0.5, "enabled"); n += 1
    # low VRAM
    assert L.group_sizes(56, 8) == [7] * 8; n += 1
    assert L.group_sizes(10, 4) == [3, 3, 2, 2]; n += 1
    assert raises(L.group_sizes, 0, 2); n += 1
    assert L.plan_low_vram(True, 8, 4, 4096, 56) == (4, 1, 4096); n += 1
    assert L.plan_low_vram(False, 8, 4, 4096, 56) == (4, 8, 4096); n += 1
    assert L.plan_low_vram(False, 56, 4, 4096, 4) == (4, 4, 4096); n += 1
    assert raises(L.plan_low_vram, True, 8, 100, 4096, 56); n += 1
    assert raises(L.plan_low_vram, True, 8, 4, 10, 56); n += 1
    assert raises(L.plan_low_vram, True, 8, 4, 4096, 0); n += 1
    assert L.lowvram_is_noop(1, 1) and not L.lowvram_is_noop(2, 1) and not L.lowvram_is_noop(1, 2); n += 1
    assert L.block_patch_keys(3) == ("diffusion_model.blocks.3.forward", "diffusion_model.blocks.3.mlp.forward",
                                     "diffusion_model.blocks.3.attn.forward"); n += 1
    assert L.mlp_chunk_active(4, 5000, 4096) and not L.mlp_chunk_active(4, 4096, 4096) \
        and not L.mlp_chunk_active(1, 9000, 4096); n += 1
    assert L.attention_groups_for(5000, 4096, 8, 56) == 8 and L.attention_groups_for(4000, 4096, 8, 56) == 1; n += 1
    assert L.attention_groups_for(5000, 0, 99, 56) == 56; n += 1
    assert L.split_sizes(10, 4) == [3, 3, 3, 1]; n += 1
    assert L.split_sizes(8, 4) == [2, 2, 2, 2]; n += 1
    # off switch needs no model object
    assert m.SYH3SpeedOptimizer().apply("M", **dict(GOOD, enable_speedup=False)) == ("M", False); n += 1
    assert m.SYH3LowVRAM().apply("M", False) == ("M",); n += 1
    return n
