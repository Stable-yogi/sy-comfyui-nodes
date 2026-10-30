"""Pure logic for the SY GGUF loaders: file name filters, option checks, name tables, key maps.

Ported from ComfyUI-GGUF (Apache-2.0, city96). Changed for the SY pack by Stable Yogi.
Original copyright: (c) City96. Licence copy: third_party/ComfyUI-GGUF/LICENSE.
No torch, numpy or gguf here: this file runs in the plain selftest.
"""
import re

INSTALL_MESSAGE = ("GGUF loaders need the Python package gguf. "
                   "Install it with: python -m pip install gguf (use the python of your ComfyUI).")

# Our own folder keys, so we never clash with a separately installed GGUF pack.
UNET_KEY = "sy_unet_gguf"
CLIP_KEY = "sy_clip_gguf"
UNET_BASE_KEYS = ("diffusion_models", "unet")
CLIP_BASE_KEYS = ("text_encoders", "clip")
GGUF_EXT = ".gguf"

IMG_ARCH_LIST = {"flux", "sd1", "sdxl", "sd3", "aura", "hidream", "cosmos", "ltxv", "hyvid", "wan", "lumina2", "qwen_image"}
TXT_ARCH_LIST = {"t5", "t5encoder", "llama", "qwen2vl", "qwen3", "qwen3vl", "gemma3"}
VIS_TYPE_LIST = {"clip-vision", "mmproj"}

# Quant types the fast unpacker knows, by GGUF type number. Anything else falls back to a slow path.
FAST_QTYPES = {30: "BF16", 8: "Q8_0", 7: "Q5_1", 6: "Q5_0", 3: "Q4_1", 2: "Q4_0", 14: "Q6_K", 13: "Q5_K",
               12: "Q4_K", 11: "Q3_K", 10: "Q2_K", 20: "IQ4_NL", 23: "IQ4_XS"}
PLAIN_QTYPES = {0: "F32", 1: "F16"}  # stored as normal torch numbers, no unpacking

ADVANCED_DTYPES = ("default", "target", "float32", "float16", "bfloat16")

# Fallback lists for the selftest; the real node asks ComfyUI for its own list.
CLIP_TYPES_FALLBACK = ["stable_diffusion", "stable_cascade", "sd3", "stable_audio", "mochi", "ltxv", "pixart", "cosmos",
                       "lumina2", "wan", "hidream", "chroma", "ace", "omnigen2", "qwen_image", "hunyuan_image",
                       "flux2", "ovis", "longcat_image", "krea2"]


def is_gguf_name(name):
    """Pure function. True when the file name ends in .gguf (any case)."""
    return isinstance(name, str) and name.lower().endswith(GGUF_EXT)


def only_gguf(names):
    """Pure function. Keeps the .gguf names, sorted, without doubles."""
    return sorted({n for n in names if is_gguf_name(n)})


def clip_choices(plain_names, gguf_names):
    """Pure function. The file list of the CLIP loaders: normal encoders plus .gguf ones, sorted, no doubles."""
    return sorted(set(plain_names) | set(only_gguf(gguf_names)))


def clip_folder_key(name):
    """Pure function. Which ComfyUI folder key holds this encoder file: .gguf files have their own key."""
    return CLIP_KEY if is_gguf_name(name) else CLIP_BASE_KEYS[0]


def check_unet_name(name):
    """Pure function. The Unet file must be a .gguf name."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("pick a GGUF model file")
    if not is_gguf_name(name):
        raise ValueError("this loader opens .gguf files only, got %r. Use the normal Unet Loader for other files." % name)
    return name


def check_dtype_option(value, what):
    """Pure function. dequant_dtype / patch_dtype choice -> None (default), 'target', or a torch dtype name."""
    if value in (None, "default"):
        return None
    if value not in ADVANCED_DTYPES:
        raise ValueError("%s %r is not one of: %s" % (what, value, ", ".join(ADVANCED_DTYPES)))
    return value


def check_clip_type(value, allowed):
    """Pure function. The clip type must be in the list ComfyUI offers."""
    if value not in allowed:
        raise ValueError("clip type %r is not one of: %s" % (value, ", ".join(allowed)))
    return value


def qtype_label(number):
    """Pure function. GGUF type number -> readable name and how it is unpacked."""
    if number in PLAIN_QTYPES:
        return "%s (plain)" % PLAIN_QTYPES[number]
    if number in FAST_QTYPES:
        return "%s (fast unpack)" % FAST_QTYPES[number]
    return "type %s (slow unpack)" % number


# ---- architecture detection for files made by other tools (no general.architecture field) ----
# (arch, [key groups; a group matches when every key is present], keys that make it unusable)
ARCH_RULES = (
    ("flux", (("transformer_blocks.0.attn.norm_added_k.weight",), ("double_blocks.0.img_attn.proj.weight",)),
     ("transformer_blocks.0.attn.norm_added_k.weight",)),
    ("sd3", (("transformer_blocks.0.attn.add_q_proj.weight",), ("joint_blocks.0.x_block.attn.qkv.weight",)),
     ("transformer_blocks.0.attn.add_q_proj.weight",)),
    ("aura", (("double_layers.3.modX.1.weight",), ("joint_transformer_blocks.3.ff_context.out_projection.weight",)),
     ("joint_transformer_blocks.3.ff_context.out_projection.weight",)),
    ("hidream", (("caption_projection.0.linear.weight", "double_stream_blocks.0.block.ff_i.shared_experts.w3.weight"),), ()),
    ("cosmos", (("blocks.0.mlp.layer1.weight", "blocks.0.adaln_modulation_cross_attn.1.weight"),), ()),
    ("ltxv", (("adaln_single.emb.timestep_embedder.linear_2.weight", "transformer_blocks.27.scale_shift_table",
               "caption_projection.linear_2.weight"),), ()),
    ("hyvid", (("double_blocks.0.img_attn_proj.weight", "txt_in.individual_token_refiner.blocks.1.self_attn_qkv.weight"),), ()),
    ("wan", (("blocks.0.self_attn.norm_q.weight", "text_embedding.2.weight", "head.modulation"),), ()),
    ("sdxl", (("down_blocks.0.downsamplers.0.conv.weight", "add_embedding.linear_1.weight"),
              ("input_blocks.3.0.op.weight", "input_blocks.6.0.op.weight", "output_blocks.2.2.conv.weight",
               "output_blocks.5.2.conv.weight"),
              ("label_emb.0.0.weight",)), ()),
    ("sd1", (("down_blocks.0.downsamplers.0.conv.weight",),
             ("input_blocks.3.0.op.weight", "input_blocks.6.0.op.weight", "input_blocks.9.0.op.weight",
              "output_blocks.2.1.conv.weight", "output_blocks.5.2.conv.weight", "output_blocks.8.2.conv.weight")), ()),
    ("lumina2", (("cap_embedder.1.weight", "context_refiner.0.attention.qkv.weight"),), ()),
)


def detect_arch(key_names):
    """Pure function. Set of tensor names -> architecture name. Raises ValueError when unknown."""
    keys = set(key_names)
    for arch, groups, banned in ARCH_RULES:
        for group in groups:
            if all(k in keys for k in group):
                if any(k in keys for k in banned):
                    raise ValueError("this model uses a layout the loader cannot read (reference format vs diffusers)")
                return arch
    raise ValueError("unknown model architecture")


# ---- key renaming from llama.cpp names back to the names ComfyUI expects ----
T5_SD_MAP = {
    "enc.": "encoder.",
    ".blk.": ".block.",
    "token_embd": "shared",
    "output_norm": "final_layer_norm",
    "attn_q": "layer.0.SelfAttention.q",
    "attn_k": "layer.0.SelfAttention.k",
    "attn_v": "layer.0.SelfAttention.v",
    "attn_o": "layer.0.SelfAttention.o",
    "attn_norm": "layer.0.layer_norm",
    "attn_rel_b": "layer.0.SelfAttention.relative_attention_bias",
    "ffn_up": "layer.1.DenseReluDense.wi_1",
    "ffn_down": "layer.1.DenseReluDense.wo",
    "ffn_gate": "layer.1.DenseReluDense.wi_0",
    "ffn_norm": "layer.1.layer_norm",
}

LLAMA_SD_MAP = {
    "blk.": "model.layers.",
    "attn_norm": "input_layernorm",
    "attn_q_norm.": "self_attn.q_norm.",
    "attn_k_norm.": "self_attn.k_norm.",
    "attn_v_norm.": "self_attn.v_norm.",
    "attn_q": "self_attn.q_proj",
    "attn_k": "self_attn.k_proj",
    "attn_v": "self_attn.v_proj",
    "attn_output": "self_attn.o_proj",
    "ffn_up": "mlp.up_proj",
    "ffn_down": "mlp.down_proj",
    "ffn_gate": "mlp.gate_proj",
    "ffn_norm": "post_attention_layernorm",
    "token_embd": "model.embed_tokens",
    "output_norm": "model.norm",
    "output.weight": "lm_head.weight",
}

GEMMA3_SD_MAP = dict(LLAMA_SD_MAP)
GEMMA3_SD_MAP.update({
    "ffn_norm": "pre_feedforward_layernorm",
    "post_ffw_norm": "post_feedforward_layernorm",
    "post_attention_norm": "post_attention_layernorm",
})

CLIP_VISION_SD_MAP = {
    "mm.": "visual.merger.mlp.",
    "v.post_ln.": "visual.merger.ln_q.",
    "v.patch_embd": "visual.patch_embed.proj",
    "v.blk.": "visual.blocks.",
    "ffn_up": "mlp.up_proj",
    "ffn_down": "mlp.down_proj",
    "ffn_gate": "mlp.gate_proj",
    "attn_out.": "attn.proj.",
    "ln1.": "norm1.",
    "ln2.": "norm2.",
}

GEMMA3_NORM_PATTERNS = (
    "input_layernorm.weight",
    "post_attention_layernorm.weight",
    "pre_feedforward_layernorm.weight",
    "post_feedforward_layernorm.weight",
    "self_attn.q_norm.weight",
    "self_attn.k_norm.weight",
    "model.norm.weight",
)


def rename_key(key, key_map):
    """Pure function. Applies every replacement of the map to one name, in map order."""
    for old, new in key_map.items():
        key = key.replace(old, new)
    return key


def sd_map_replace(raw_sd, key_map):
    """Pure function. New dict with every key renamed (values untouched)."""
    return {rename_key(k, key_map): v for k, v in raw_sd.items()}


def is_gemma3_norm_key(key):
    """Pure function. True for the norm weights that need the minus-one fix."""
    return any(p in key for p in GEMMA3_NORM_PATTERNS)


def strip_quant_suffix(name):
    """Pure function. 'qwen-image-q4_k_m' -> 'qwen-image'. Used to match a text encoder with its mmproj file."""
    match = re.search(r"[-_]?(?:ud-)?i?q[0-9]_[a-z0-9_\-]{1,8}$", name, re.IGNORECASE)
    if match:
        name = name[:match.start()]
    return name


def is_mmproj_for(encoder_stem, file_name):
    """Pure function. True when file_name is a .gguf mmproj file that belongs to the encoder (already lower case, no quant)."""
    name, ext = file_name.rsplit(".", 1) if "." in file_name else (file_name, "")
    if ext.lower() != "gguf":
        return False
    low = name.lower()
    return "mmproj" in low and encoder_stem in low


def bytes_to_unicode():
    """Pure function. The standard byte -> printable character table used by byte-level tokenizers."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("\xa1"), ord("\xac") + 1)) + list(range(ord("\xae"), ord("\xff") + 1))
    cs = bs[:]
    n = 0
    for b in range(2 ** 8):
        if b not in bs:
            bs.append(b)
            cs.append(2 ** 8 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))
