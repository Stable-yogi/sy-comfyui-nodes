"""Patched forward functions of H3LowVRAM SY: lower peak memory of the MiniMax H3 transformer.

Ported from ComfyUI-TeaCache (Apache-2.0). Changed for the SY pack by Stable Yogi.
Licence copy: third_party/ComfyUI-TeaCache/LICENSE.
Changes: sizes and switches are pure functions in _sy_h3_logic.py; torch and comfy are imported inside functions.

Three ideas, safest first: (1) free the big attention buffers at their last use, (2) run the feedforward over token
chunks (same numbers), (3) optionally split attention into head groups (can shift the result by one rounding step).
"""
try:
    from . import _sy_h3_logic as L
except ImportError:  # run as a plain file by the selftest
    import _sy_h3_logic as L

# Same keys the other MiniMax low-VRAM nodes use, so several of them can sit in one workflow.
HEAD_GROUPS_KEY = "minimax_head_chunks"
MIN_TOKENS_KEY = "minimax_h3_low_vram_min_tokens"


def h3_helpers():
    """The two ComfyUI modulation helpers, or (None, None) when this ComfyUI has no MiniMax H3 support."""
    try:
        from comfy.ldm.minimax.model import _mod_scale_shift, _mod_gate
    except ImportError:
        return None, None
    return _mod_scale_shift, _mod_gate


def _grouped_attention(q, k, v, heads, head_dim, groups, out, transformer_options):
    """Run attention in head groups, writing each group into its slice of out."""
    from comfy.ldm.modules.attention import optimized_attention
    start = 0
    for size in L.group_sizes(heads, groups):
        stop = start + size
        out[:, start * head_dim:stop * head_dim] = optimized_attention(
            q[:, start:stop], k[:, start:stop], v[:, start:stop], size, mask=None,
            skip_reshape=True, transformer_options=transformer_options).squeeze(0)
        start = stop
    return out


def attention_forward(self, x, rope_freqs=None, transformer_options={}):
    """Attention.forward, restructured to drop each large buffer at its last use."""
    import torch
    import comfy.model_management as mm
    import comfy.quant_ops
    from comfy.ldm.modules.attention import optimized_attention
    # The patched block forward hands x over inside a single-item list, so popping it
    # here leaves exactly one reference and the normed block input dies with the qkv GEMM.
    if isinstance(x, list):
        x = x.pop()
    s = x.shape[0]
    device, dtype = x.device, x.dtype
    qkv = self.qkv_proj(x)
    del x
    q, k, v = qkv.split(self.heads * self.head_dim, dim=-1)
    v = v.view(s, self.heads, self.head_dim)
    if rope_freqs is not None:
        q = q.view(1, s, self.heads, self.head_dim)
        k = k.view(1, s, self.heads, self.head_dim)
        qw = mm.cast_to(self.q_norm.weight, device=device)
        kw = mm.cast_to(self.k_norm.weight, device=device)
        rot = rope_freqs.shape[-3] * 2
        if mm.in_training:
            q, k = comfy.quant_ops.ck.rms_rope_split_half(
                q, k, rope_freqs, qw, kw, epsilon=self.q_norm.eps, rot_dim=rot)
        else:
            comfy.quant_ops.ck.rms_rope_split_half_(
                q, k, rope_freqs, qw, kw, epsilon=self.q_norm.eps, rot_dim=rot)
        q = q[0]
        k = k[0]
    else:
        q = self.q_norm(q.view(s, self.heads, self.head_dim))
        k = self.k_norm(k.view(s, self.heads, self.head_dim))
    q = q.transpose(0, 1).unsqueeze(0)
    k = k.transpose(0, 1).unsqueeze(0)
    v = v.transpose(0, 1).unsqueeze(0)

    groups = 1
    if isinstance(transformer_options, dict):
        groups = L.attention_groups_for(s, transformer_options.get(MIN_TOKENS_KEY, 0),
                                        transformer_options.get(HEAD_GROUPS_KEY, 1), self.heads)
    if groups <= 1:
        out = optimized_attention(q, k, v, self.heads, mask=None, skip_reshape=True,
                                  transformer_options=transformer_options).squeeze(0)
    else:
        out = _grouped_attention(q, k, v, self.heads, self.head_dim, groups,
                                 torch.empty((s, self.heads * self.head_dim), dtype=dtype, device=device),
                                 transformer_options)
    # free the whole fused qkv buffer before out_proj allocates
    del q, k, v, qkv
    return self.out_proj(out)


# Attention overrides that hook optimized_attention (sparse attention, other sage patches) still apply inside
# this forward rather than being bypassed by it.
attention_forward._uses_optimized_attention = True
# Marks this forward as willing to take the block's normed input inside a list and free it.
attention_forward._h3_accepts_list = True


def make_mlp_forward(chunks, min_tokens):
    def forward(self, x):
        """MLP.forward over token chunks. Only one chunk's gate/up activation is live at a time. Rows are
        independent and the INT8 activation quantizer works per row, so the result equals the whole-tensor call."""
        import torch
        import comfy.ops
        if not L.mlp_chunk_active(chunks, x.shape[0], min_tokens):
            return comfy.ops.linear_input_act(self.fc2, self.fc1(x), "swiglu")

        out = None
        offset = 0
        for chunk in torch.chunk(x, chunks, dim=0):
            y = comfy.ops.linear_input_act(self.fc2, self.fc1(chunk), "swiglu")
            if out is None:
                out = torch.empty((x.shape[0], y.shape[1]), dtype=y.dtype, device=y.device)
            out[offset:offset + y.shape[0]] = y
            offset += y.shape[0]
            del y
        return out
    return forward


def block_forward(self, x, t_emb, mod_segments, rope_freqs, transformer_options={}):
    """DiTBlock.forward that hands its normed attention input over to attn.

    The handoff is checked per call: another node may own this block's attn.forward, and only a forward that
    advertises _h3_accepts_list knows what to do with the list. Anything else gets the plain tensor."""
    _mod_scale_shift, _mod_gate = h3_helpers()
    shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.adaln_proj(t_emb)
    h = _mod_scale_shift(self.norm1(x), shift_msa, scale_msa, mod_segments)
    if getattr(self.attn.forward, "_h3_accepts_list", False):
        h = [h]
    x = _mod_gate(x, gate_msa, self.attn(h, rope_freqs=rope_freqs, transformer_options=transformer_options), mod_segments)
    h = _mod_scale_shift(self.norm2(x), shift_mlp, scale_mlp, mod_segments)
    return _mod_gate(x, gate_mlp, self.mlp(h), mod_segments)
