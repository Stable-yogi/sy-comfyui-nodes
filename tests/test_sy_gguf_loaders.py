import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_gguf_loaders as m
import _sy_gguf_names as n


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    c = 0
    # file name filters
    assert n.is_gguf_name("a/b/Model-Q4_0.GGUF"); c += 1
    assert not n.is_gguf_name("model.safetensors") and not n.is_gguf_name(None); c += 1
    assert n.only_gguf(["b.gguf", "a.safetensors", "a.gguf", "b.gguf"]) == ["a.gguf", "b.gguf"]; c += 1
    assert n.clip_choices(["t5.safetensors", "z.safetensors"], ["t5-q8.gguf", "x.bin"]) == ["t5-q8.gguf", "t5.safetensors", "z.safetensors"]; c += 1
    assert n.clip_folder_key("enc/t5-Q8_0.gguf") == "sy_clip_gguf"; c += 1
    assert n.clip_folder_key("t5.safetensors") == "text_encoders"; c += 1
    assert n.check_unet_name("sub/flux-Q4_0.gguf") == "sub/flux-Q4_0.gguf"; c += 1
    assert raises(n.check_unet_name, "flux.safetensors"); c += 1
    assert raises(n.check_unet_name, ""); c += 1
    assert raises(n.check_unet_name, None); c += 1
    # option checks
    assert n.check_dtype_option(None, "x") is None and n.check_dtype_option("default", "x") is None; c += 1
    assert n.check_dtype_option("bfloat16", "x") == "bfloat16" and n.check_dtype_option("target", "x") == "target"; c += 1
    assert raises(n.check_dtype_option, "float8", "dequant_dtype"); c += 1
    assert n.check_clip_type("sd3", ["sd3", "flux"]) == "sd3"; c += 1
    assert raises(n.check_clip_type, "nope", ["sd3", "flux"]); c += 1
    # install message names the package and the command
    assert "gguf" in n.INSTALL_MESSAGE and "python -m pip install gguf" in n.INSTALL_MESSAGE; c += 1
    # quant type names
    assert n.qtype_label(0) == "F32 (plain)" and n.qtype_label(1) == "F16 (plain)"; c += 1
    assert n.qtype_label(2) == "Q4_0 (fast unpack)" and n.qtype_label(8) == "Q8_0 (fast unpack)"; c += 1
    assert n.qtype_label(30) == "BF16 (fast unpack)"; c += 1
    assert n.qtype_label(16) == "type 16 (slow unpack)"; c += 1
    assert len(n.FAST_QTYPES) == 13 and not (set(n.FAST_QTYPES) & set(n.PLAIN_QTYPES)); c += 1
    # architecture lists and detection
    assert "flux" in n.IMG_ARCH_LIST and "t5" in n.TXT_ARCH_LIST and "mmproj" in n.VIS_TYPE_LIST; c += 1
    assert n.detect_arch({"double_blocks.0.img_attn.proj.weight", "x"}) == "flux"; c += 1
    assert n.detect_arch({"blocks.0.self_attn.norm_q.weight", "text_embedding.2.weight", "head.modulation"}) == "wan"; c += 1
    assert n.detect_arch({"label_emb.0.0.weight"}) == "sdxl"; c += 1
    assert raises(n.detect_arch, {"nothing.weight"}); c += 1
    assert raises(n.detect_arch, {"transformer_blocks.0.attn.norm_added_k.weight"}); c += 1
    # key renaming
    assert n.rename_key("blk.0.attn_q.weight", n.LLAMA_SD_MAP) == "model.layers.0.self_attn.q_proj.weight"; c += 1
    assert n.rename_key("output.weight", n.LLAMA_SD_MAP) == "lm_head.weight"; c += 1
    assert n.rename_key("enc.blk.3.ffn_up.weight", n.T5_SD_MAP) == "encoder.block.3.layer.1.DenseReluDense.wi_1.weight"; c += 1
    assert n.rename_key("blk.1.ffn_norm.weight", n.GEMMA3_SD_MAP) == "model.layers.1.pre_feedforward_layernorm.weight"; c += 1
    assert n.sd_map_replace({"token_embd.weight": 7}, n.T5_SD_MAP) == {"shared.weight": 7}; c += 1
    assert n.is_gemma3_norm_key("model.layers.0.input_layernorm.weight") and not n.is_gemma3_norm_key("model.layers.0.mlp.up_proj.weight"); c += 1
    # mmproj matching
    assert n.strip_quant_suffix("qwen2.5-vl-7b-instruct-q4_k_m") == "qwen2.5-vl-7b-instruct"; c += 1
    assert n.strip_quant_suffix("model-ud-q8_0") == "model"; c += 1
    assert n.strip_quant_suffix("plain-name") == "plain-name"; c += 1
    assert n.is_mmproj_for("qwen-vl", "Qwen-VL-mmproj-F16.gguf"); c += 1
    assert not n.is_mmproj_for("qwen-vl", "qwen-vl-q4_0.gguf") and not n.is_mmproj_for("qwen-vl", "qwen-vl-mmproj.bin"); c += 1
    # byte table (tekken tokenizer): 256 distinct printable characters, ASCII letters map to themselves
    table = n.bytes_to_unicode()
    assert len(table) == 256 and len(set(table.values())) == 256; c += 1
    assert table[ord("A")] == "A" and table[32] == "Ġ" and table[0] == "Ā"; c += 1
    # the module imports without torch, numpy or gguf
    for bad in ("torch", "numpy", "gguf"):
        assert not hasattr(m, bad) and not hasattr(n, bad); c += 1
    # node classes
    for cls, rets in ((m.SYUnetLoaderGGUF, ("MODEL",)), (m.SYCLIPLoaderGGUF, ("CLIP",)), (m.SYDualCLIPLoaderGGUF, ("CLIP",))):
        assert cls.RETURN_TYPES == rets and cls.CATEGORY.startswith("SY/") and cls.DESCRIPTION; c += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYUnetLoaderGGUF"] == "UnetLoaderGGUF SY"; c += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYCLIPLoaderGGUF"] == "CLIPLoaderGGUF SY"; c += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYDualCLIPLoaderGGUF"] == "DualCLIPLoaderGGUF SY"; c += 1
    # input names match the original nodes
    assert list(m.SYUnetLoaderGGUF.INPUT_TYPES()["required"]) == ["unet_name"]; c += 1
    assert list(m.SYCLIPLoaderGGUF.INPUT_TYPES()["required"]) == ["clip_name", "type"]; c += 1
    assert list(m.SYDualCLIPLoaderGGUF.INPUT_TYPES()["required"]) == ["clip_name1", "clip_name2", "type"]; c += 1
    # bad input is a plain ValueError, before any heavy import
    assert raises(m.SYUnetLoaderGGUF().run, "model.safetensors"); c += 1
    assert raises(m.SYCLIPLoaderGGUF().run, "", "stable_diffusion"); c += 1
    assert raises(m.SYCLIPLoaderGGUF().run, "enc.gguf", "not_a_type"); c += 1
    assert raises(m.SYDualCLIPLoaderGGUF().run, "a.gguf", "b.gguf", "not_a_type"); c += 1
    return c
