import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_krea2_oneclick as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    names = ["flux_dev.safetensors", "my_krea2_q8.gguf", "other.safetensors", "Muse_v2.safetensors"]
    assert m.rank_names(names, m.MODEL_HINTS) == ["my_krea2_q8.gguf", "Muse_v2.safetensors", "flux_dev.safetensors", "other.safetensors"]; n += 1
    assert m.rank_names([], m.MODEL_HINTS) == []; n += 1
    assert m.pick_auto(["a.safetensors", "qwen3vl_4b_fp8.safetensors"], m.CLIP_HINTS, "text encoder") == "qwen3vl_4b_fp8.safetensors"; n += 1
    assert raises(m.pick_auto, ["x.safetensors"], m.VAE_HINTS, "VAE"); n += 1
    assert raises(m.pick_auto, [], m.VAE_HINTS, "VAE"); n += 1
    assert m.quality_values("Fast (8 steps)", 99, 9.0) == (8, 1.0); n += 1
    assert m.quality_values("Custom", 30, 4.5) == (30, 4.5); n += 1
    assert raises(m.quality_values, "nope", 1, 1.0); n += 1
    assert m.size_values("Square 1:1 (1024x1024)", 1, 1) == (1024, 1024); n += 1
    assert m.size_values("Custom", 1001, 70) == (1000, 70 // 8 * 8 if 70 // 8 * 8 >= 64 else 64); n += 1
    assert m.size_values("Custom", 10, 10) == (64, 64); n += 1
    assert raises(m.size_values, "nope", 1, 1); n += 1
    assert m.detail_denoise("Off") == 0.0 and m.detail_denoise("Full") == 0.40; n += 1
    assert raises(m.detail_denoise, "huge"); n += 1
    assert m.negative_mode("blurry", 2.0) == "encode"; n += 1
    assert m.negative_mode("  ", 1.0) == "zero"; n += 1
    assert m.negative_mode("", 2.0) == "empty"; n += 1
    assert m.active_loras([("None", 0.8), ("a.safetensors", 0.0), ("b.safetensors", 0.5), ("", 1.0)]) == [("b.safetensors", 0.5)]; n += 1
    assert m.is_gguf("X.GGUF") and not m.is_gguf("x.safetensors"); n += 1
    # declarations identical to the old node
    spec = m.SYKrea2OneClick.INPUT_TYPES()
    assert list(spec["required"]) == ["model", "prompt", "negative", "quality", "size", "seed", "detail_pass"]; n += 1
    assert list(spec["optional"]) == ["lora_1", "lora_1_strength", "lora_2", "lora_2_strength", "lora_3", "lora_3_strength",
                                      "text_encoder", "vae", "custom_steps", "custom_cfg", "custom_width", "custom_height",
                                      "batch_size", "shift", "sampler_name", "scheduler", "weight_dtype"]; n += 1
    assert spec["required"]["seed"][1]["default"] == 0 and spec["optional"]["shift"][1]["default"] == 2.95; n += 1
    assert m.SYKrea2OneClick.RETURN_TYPES == ("IMAGE", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT"); n += 1
    assert m.SYKrea2OneClick.RETURN_NAMES == ("image", "model", "clip", "vae", "positive", "negative", "latent"); n += 1
    assert list(m.QUALITY_PRESETS) == ["Fast (8 steps)", "Best (16 steps)", "Max (20 steps)", "Custom"]; n += 1
    assert m.NODE_CLASS_MAPPINGS == {"SYKrea2OneClick": m.SYKrea2OneClick}; n += 1
    return n
