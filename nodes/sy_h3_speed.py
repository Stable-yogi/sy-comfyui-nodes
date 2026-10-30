"""H3 speed nodes SY: H3SpeedOptimizer (faster sampling) and H3LowVRAM (lower peak memory) for the MiniMax H3 model.

Ported from ComfyUI-TeaCache (Apache-2.0). Changed for the SY pack by Stable Yogi.
Licence copy: third_party/ComfyUI-TeaCache/LICENSE. Original idea: the sol-engine MiniMax H3 acceleration line.
Changes: SY names and tooltips, pure checks in _sy_h3_logic.py, bad input raises ValueError, torch and comfy are
imported inside methods. The VAE speedup node of the original is not part of this port. The sparse attention kernel
is not bundled: with 'auto' or 'enabled' it is used when it can be found (see _sy_h3_speed_core.load_sol_attn),
otherwise the normal attention runs. Inputs, outputs, defaults and widget order match the original nodes.
"""
import logging
import types

try:
    from ._sy_common import category, register
    from . import _sy_h3_logic as L
    from . import _sy_h3_speed_core as S
    from . import _sy_h3_lowvram_core as V
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_h3_logic as L
    import _sy_h3_speed_core as S
    import _sy_h3_lowvram_core as V


def _diffusion_model(model):
    try:
        return model.get_model_object("diffusion_model")
    except AttributeError:  # not a diffusion model patcher at all
        return None


class SYH3SpeedOptimizer:
    DESCRIPTION = ("Makes MiniMax H3 sampling faster. It skips the rest of the model on steps where the first block "
                   "barely changed, and can use sparse attention. A switch turns everything off. Other settings "
                   "that cannot help on your GPU fall back to the normal path.")
    CATEGORY = category("Utility")
    FUNCTION = "apply"
    RETURN_TYPES = ("MODEL", "BOOLEAN")
    RETURN_NAMES = ("model", "speedup_enabled")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "A MiniMax H3 diffusion model."}),
                "first_block_cache": ("BOOLEAN", {"default": True, "tooltip": "Skip most blocks when block 0 barely changed since the last step. The main speed-up."}),
                "fbc_threshold": ("FLOAT", {"default": 0.08, "min": 0.0, "max": 1.0, "step": 0.005, "tooltip": "Total change allowed before a step is computed. 0.08 is near lossless; 0.15-0.20 is faster but softer."}),
                "fbc_start_percent": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Never skip before this fraction of the steps. Early steps set the global structure."}),
                "fbc_end_percent": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Never skip after this fraction of the steps. The last steps set the fine detail."}),
                "fbc_max_consecutive": ("INT", {"default": 3, "min": 1, "max": 50, "tooltip": "Most steps in a row that may be skipped."}),
                "sparse_attention": (["auto", "enabled", "disabled"], {"default": "auto", "tooltip": "Sparse attention. auto checks the result and speed on your GPU and keeps the faster way."}),
                "sparse_dense_steps_pct": ("FLOAT", {"default": 0.20, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "Fraction of the first steps that always use normal attention."}),
                "sparse_dense_layers": ("INT", {"default": 2, "min": 0, "max": 50, "tooltip": "The first N blocks always use normal attention."}),
            },
            "optional": {
                "sparse_tau": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 100.0, "step": 0.1, "tooltip": "Sparse attention threshold. 1.0 is the standard value; higher keeps fewer blocks."}),
                "sparse_min_video_rows": ("INT", {"default": 4096, "min": 0, "max": 1000000, "tooltip": "Use sparse attention only when the video part is longer than this. Short ones gain nothing."}),
                "fbc_cache_device": (["gpu", "cpu"], {"default": "gpu", "tooltip": "Where the saved data lives. cpu saves video memory but is slower."}),
                "verbose": ("BOOLEAN", {"default": True, "tooltip": "Write a short summary of skipped steps to the console after each run."}),
                "enable_speedup": ("BOOLEAN", {
                    "default": True,
                    "label_on": "ENABLED",
                    "label_off": "DISABLED (normal)",
                    "tooltip": "Master switch. Off passes the model through unchanged and returns False on speedup_enabled.",
                }),
            },
        }

    def apply(self, model, first_block_cache, fbc_threshold, fbc_start_percent, fbc_end_percent,
              fbc_max_consecutive, sparse_attention, sparse_dense_steps_pct, sparse_dense_layers,
              sparse_tau=1.0, sparse_min_video_rows=4096, fbc_cache_device="gpu", verbose=True,
              enable_speedup=True):
        if not enable_speedup:
            return (model, False)
        L.check_speed_options(first_block_cache, fbc_threshold, fbc_start_percent, fbc_end_percent,
                              fbc_max_consecutive, sparse_attention, sparse_dense_steps_pct, sparse_dense_layers,
                              sparse_tau, sparse_min_video_rows, fbc_cache_device)
        import comfy.patcher_extension

        diffusion_model = _diffusion_model(model)
        L.require_h3_model(type(diffusion_model).__name__, "H3SpeedOptimizer SY")
        if L.speed_is_noop(first_block_cache, sparse_attention):
            return (model, True)

        m = model.clone()
        opt = S.H3Optimizer(
            num_blocks=len(diffusion_model.blocks),
            fbc_enabled=first_block_cache,
            fbc_threshold=fbc_threshold,
            fbc_start_percent=fbc_start_percent,
            fbc_end_percent=fbc_end_percent,
            fbc_max_consecutive=fbc_max_consecutive,
            fbc_cache_device=fbc_cache_device,
            sparse_mode=sparse_attention,
            sparse_tau=sparse_tau,
            sparse_dense_steps_pct=sparse_dense_steps_pct,
            sparse_dense_layers=sparse_dense_layers,
            sparse_min_video_rows=sparse_min_video_rows,
            verbose=verbose,
        )

        def wrapper(executor, x, timestep, context, transformer_options={}, **kwargs):
            payload = kwargs.get("minimax_payload") or {}
            opt.observe(timestep, transformer_options, payload.get("layout"))
            return executor(x, timestep, context, transformer_options, **kwargs)

        m.add_wrapper_with_key(comfy.patcher_extension.WrappersMP.DIFFUSION_MODEL, "minimax_h3_speed", wrapper)
        for i in range(opt.num_blocks):
            m.set_model_patch_replace(opt.block_patch(i), "dit", "double_block", i)

        if sparse_attention != "disabled":
            to = m.model_options.setdefault("transformer_options", {})
            to["optimized_attention_override"] = S.chain_attention_override(opt, to.get("optimized_attention_override"))

        m.model_options["minimax_h3_speed_optimizer"] = opt
        return (m, True)


class SYH3LowVRAM:
    DESCRIPTION = ("Lowers the peak video memory of the MiniMax H3 model so a size or length that ran out of memory "
                   "can finish. The default keeps the result identical. Off by default.")
    CATEGORY = category("Utility")
    FUNCTION = "apply"
    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "A MiniMax H3 diffusion model."}),
                "enable_low_vram": ("BOOLEAN", {
                    "default": False,
                    "label_on": "ENABLED",
                    "label_off": "DISABLED (normal)",
                    "tooltip": "Master switch. Off passes the model through and changes nothing.",
                }),
            },
            "optional": {
                "exact_output": ("BOOLEAN", {
                    "default": True,
                    "label_on": "EXACT (same result, ~15% less)",
                    "label_off": "MAX SAVING (result differs, ~40% less)",
                    "tooltip": "EXACT keeps your normal result. MAX SAVING also splits attention in head groups; the video may differ.",
                }),
                "attention_head_groups": ("INT", {"default": 8, "min": 1, "max": 56, "tooltip": "MAX SAVING only. Split attention into this many head groups. Past 8 gains little."}),
                "feedforward_chunks": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "Split the feedforward step into this many parts. Same result, less memory. 1 turns it off."}),
                "min_tokens": ("INT", {"default": 4096, "min": 256, "max": 1048576, "step": 256, "tooltip": "Split only when the sequence is longer than this. Short ones gain nothing."}),
            },
        }

    def apply(self, model, enable_low_vram, exact_output=True, attention_head_groups=8,
              feedforward_chunks=4, min_tokens=4096):
        if not enable_low_vram:
            return (model,)
        mod_scale_shift, mod_gate = V.h3_helpers()
        if mod_scale_shift is None or mod_gate is None:
            raise RuntimeError("This ComfyUI version does not support MiniMax H3. Update ComfyUI to use H3LowVRAM SY.")

        diffusion_model = _diffusion_model(model)
        L.require_h3_model(type(diffusion_model).__name__, "H3LowVRAM SY")
        blocks = getattr(diffusion_model, "blocks", None)
        if not blocks:
            raise ValueError("H3LowVRAM SY could not find the MiniMax H3 transformer blocks in this model.")

        chunks, groups, min_tok = L.plan_low_vram(exact_output, attention_head_groups, feedforward_chunks,
                                                  min_tokens, blocks[0].attn.heads)
        if L.lowvram_is_noop(chunks, groups):
            return (model,)

        m = model.clone()
        # Read by the patched attention forward, so head grouping follows the model down either branch of a chain.
        transformer_options = m.model_options.setdefault("transformer_options", {})
        transformer_options[V.HEAD_GROUPS_KEY] = groups
        transformer_options[V.MIN_TOKENS_KEY] = min_tok

        mlp_forward = V.make_mlp_forward(chunks, min_tok)
        composed = 0
        for index, block in enumerate(blocks):
            block_key, mlp_key, attn_key = L.block_patch_keys(index)
            m.add_object_patch(block_key, types.MethodType(V.block_forward, block))
            m.add_object_patch(mlp_key, types.MethodType(mlp_forward, block.mlp))
            if attn_key in m.object_patches:
                # Another attention patch already owns this forward: keep it. It reads head grouping from
                # transformer_options, and the block-level buffer release still applies.
                composed += 1
                continue
            m.add_object_patch(attn_key, types.MethodType(V.attention_forward, block.attn))

        if composed:
            logging.info("[H3LowVRAM SY] composing with an existing attention patch on %d block(s); keeping its forward "
                         "and passing head grouping through." % composed)
        logging.info("[H3LowVRAM SY] enabled on %d blocks above %d tokens: %d feedforward chunk(s), %s"
                     % (len(blocks), min_tok, chunks,
                        "%d attention head group(s) (maximum saving, output may differ)" % groups if groups > 1
                        else "attention head grouping off (exact output)"))
        return (m,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3SpeedOptimizer", SYH3SpeedOptimizer)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3LowVRAM", SYH3LowVRAM)
