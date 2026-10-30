"""Speed engine of H3SpeedOptimizer SY: step skipping (first block cache) and sparse attention for MiniMax H3.

Ported from ComfyUI-TeaCache (Apache-2.0). Changed for the SY pack by Stable Yogi.
Licence copy: third_party/ComfyUI-TeaCache/LICENSE. Original idea: the sol-engine MiniMax H3 acceleration line.
Changes: the decisions are pure functions in _sy_h3_logic.py; torch is imported inside methods; the sparse
kernel is NOT bundled (see load_sol_attn).
"""
import logging
import sys
import time

try:
    from . import _sy_h3_logic as L
except ImportError:  # run as a plain file by the selftest
    import _sy_h3_logic as L

_SOL_ATTN = None
_SOL_ATTN_ERROR = None
TAG = "[H3SpeedOptimizer SY]"


def load_sol_attn():
    """Find the sparse attention kernel once. It is not bundled: it comes from an installed `sol_attn` package or
    from the ComfyUI-TeaCache pack when that is installed. Returns the function or None (then dense attention runs)."""
    global _SOL_ATTN, _SOL_ATTN_ERROR
    if _SOL_ATTN is not None or _SOL_ATTN_ERROR is not None:
        return _SOL_ATTN
    try:
        import importlib
        pkg = None
        if "sol_attn" in sys.modules:
            pkg = sys.modules["sol_attn"]
        else:
            for name in list(sys.modules):
                if name == "minimax_h3" or name.endswith(".minimax_h3"):
                    pkg = importlib.import_module(name + ".sol_attn")
                    break
            if pkg is None:
                pkg = importlib.import_module("sol_attn")
        # the kernel files import `sol_attn.*` absolutely: give the package its top-level name
        sys.modules.setdefault("sol_attn", pkg)
        _SOL_ATTN = pkg.sol_attn
    except Exception as e:  # any failure means dense attention
        _SOL_ATTN_ERROR = "%s: %s" % (type(e).__name__, e)
        logging.warning("%s sparse attention kernel not found, using dense attention: %s" % (TAG, _SOL_ATTN_ERROR))
    return _SOL_ATTN


def _dense_bthd(q, k, v):
    """Plain attention over contiguous [B, T, H, D], same layout out."""
    import torch.nn.functional as F
    out = F.scaled_dot_product_attention(
        q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2), dropout_p=0.0, is_causal=False)
    return out.transpose(1, 2)


class _CondCache:
    """Cache state for one cond/uncond stream."""

    __slots__ = ("prev_resid", "tail_resid", "h_b0", "skip", "accum", "consec")

    def __init__(self):
        self.prev_resid = None
        self.tail_resid = None
        self.h_b0 = None
        self.skip = False
        self.accum = 0.0
        self.consec = 0


class H3Optimizer:
    """Shared state + logic behind the wrapper, the block patches and the attention override."""

    def __init__(self, num_blocks, fbc_enabled, fbc_threshold, fbc_start_percent, fbc_end_percent,
                 fbc_max_consecutive, fbc_cache_device, sparse_mode, sparse_tau, sparse_dense_steps_pct,
                 sparse_dense_layers, sparse_min_video_rows, verbose):
        self.num_blocks = num_blocks
        self.last_block = num_blocks - 1
        self.fbc_enabled = fbc_enabled
        self.fbc_threshold = float(fbc_threshold)
        self.fbc_start_percent = float(fbc_start_percent)
        self.fbc_end_percent = float(fbc_end_percent)
        self.fbc_max_consecutive = int(fbc_max_consecutive)
        self.fbc_cache_device = fbc_cache_device
        self.sparse_mode = sparse_mode  # "auto" | "enabled" | "disabled"
        self.sparse_tau = float(sparse_tau)
        self.sparse_dense_steps_pct = float(sparse_dense_steps_pct)
        self.sparse_dense_layers = int(sparse_dense_layers)
        self.sparse_min_video_rows = int(sparse_min_video_rows)
        self.verbose = verbose

        # per-run state
        self.step_index = -1
        self.total_steps = 0
        self.layer = -1
        self.seq_len = None
        self.video_start = None
        self.cond_key = (0,)
        self.caches = {}
        self.fbc_skipped_steps = 0
        self.fbc_computed_steps = 0
        self._last_sigma = None

        # per-process sparse resolution: None = undecided, True/False = decided
        self.sparse_resolved = None if sparse_mode == "auto" else (sparse_mode == "enabled")
        self.sparse_failed_reason = None
        self.sparse_calls = 0
        self.dense_calls = 0
        self._gate_done = set()

    # ------------------------------------------------------------ run observation

    def observe(self, timestep, transformer_options, layout):
        sigma = float(timestep.flatten()[0].detach().float().item()) / 1000.0
        sigmas = transformer_options.get("sample_sigmas", None)
        if sigmas is not None and sigmas.numel() > 1:
            idx, total = L.nearest_step(sigma, sigmas.detach().float().cpu().tolist())
        else:
            idx, total = L.fallback_step(sigma, self._last_sigma, self.step_index, self.total_steps)
        self._last_sigma = sigma

        if idx == 0 and self.step_index != 0:
            self.reset_run()
        self.step_index = idx
        self.total_steps = total
        self.layer = -1
        self.cond_key = tuple(transformer_options.get("cond_or_uncond", [0]))

        if layout is not None:
            self.seq_len = layout.seq_len
            video_start = None
            for a, _b, kind in layout.segments:
                if kind == "video":
                    video_start = a
                    break
            self.video_start = video_start
        else:
            self.seq_len = None
            self.video_start = None

    def reset_run(self):
        if self.verbose and (self.fbc_skipped_steps or self.fbc_computed_steps):
            logging.info("%s run summary: %d skipped / %d computed block-stack steps, %d sparse / %d dense attention calls"
                         % (TAG, self.fbc_skipped_steps, self.fbc_computed_steps, self.sparse_calls, self.dense_calls))
        self.caches = {}
        self.fbc_skipped_steps = 0
        self.fbc_computed_steps = 0
        self.sparse_calls = 0
        self.dense_calls = 0

    # ------------------------------------------------------------ step skipping

    def _to_cache_device(self, t):
        if self.fbc_cache_device == "cpu":
            return t.to("cpu")
        return t

    def _from_cache_device(self, t, device):
        if t.device != device:
            return t.to(device)
        return t

    def fbc_window_open(self):
        return L.fbc_window_open(self.fbc_enabled, self.step_index, self.total_steps,
                                 self.fbc_start_percent, self.fbc_end_percent)

    def block_patch(self, index):
        def patch(args, extra):
            img = args["img"]
            original = extra["original_block"]
            self.layer = index
            if not self.fbc_enabled:
                return original(args)
            cache = self.caches.setdefault(self.cond_key, _CondCache())

            if index == 0:
                h_in = img.clone()
                out = original(args)["img"]
                resid = (out - h_in)
                del h_in
                skip = False
                if cache.prev_resid is not None and cache.tail_resid is not None and self.fbc_window_open():
                    prev = self._from_cache_device(cache.prev_resid, resid.device)
                    delta = ((resid - prev).abs().float().mean()
                             / prev.abs().float().mean().clamp_min(1e-8)).item()
                    self.accum_delta = delta
                    skip, cache.accum, cache.consec = L.fbc_decide(
                        delta, cache.accum, cache.consec, self.fbc_threshold, self.fbc_max_consecutive)
                cache.prev_resid = self._to_cache_device(resid)
                cache.skip = skip
                if skip:
                    self.fbc_skipped_steps += 1
                else:
                    self.fbc_computed_steps += 1
                    cache.h_b0 = out.clone()
                return {"img": out}

            if cache.skip:
                if index == self.last_block:
                    tail = self._from_cache_device(cache.tail_resid, img.device)
                    self._maybe_log_final_step()
                    return {"img": img.add_(tail.to(img.dtype))}
                return {"img": img}

            out = original(args)["img"]
            if index == self.last_block and cache.h_b0 is not None:
                cache.tail_resid = self._to_cache_device(out - cache.h_b0)
                cache.h_b0 = None
            if index == self.last_block:
                self._maybe_log_final_step()
            return {"img": out}

        return patch

    def _maybe_log_final_step(self):
        if self.verbose and self.step_index == self.total_steps - 1:
            logging.info("%s run done: skipped %d of %d block-stack evaluations, %d sparse / %d dense attention calls"
                         % (TAG, self.fbc_skipped_steps, self.fbc_skipped_steps + self.fbc_computed_steps,
                            self.sparse_calls, self.dense_calls))

    # ------------------------------------------------------------ sparse attention

    def _sparse_eligible(self, q, heads, kwargs):
        if self.sparse_resolved is False or self.sparse_failed_reason is not None:
            return False
        if not L.sparse_shape_ok(tuple(q.shape), heads, self.seq_len, kwargs.get("skip_reshape", False),
                                 kwargs.get("mask") is not None):
            return False
        return L.sparse_basic_eligible(self.layer, self.step_index, self.total_steps, self.sparse_dense_steps_pct,
                                       self.sparse_dense_layers, self.seq_len, self.video_start,
                                       self.sparse_min_video_rows)

    def _gate_and_bench(self, sol_attn, qb, kb, vb, incumbent):
        """Check the sparse kernel against dense attention and time it against the current backend.

        Runs once per (device, sequence length) pair, on the model's own tensors. A sparse setup that is wrong or
        slower than what the user already runs is switched off for the rest of the process."""
        import torch
        key = (qb.device.index, qb.shape[1])
        if key in self._gate_done:
            return True
        t_compile = time.perf_counter()
        got = sol_attn(qb, kb, vb, tau=-1000.0, thresh_type="diag")
        torch.cuda.synchronize(qb.device)
        compile_s = time.perf_counter() - t_compile
        want = _dense_bthd(qb, kb, vb)
        rel = (torch.linalg.vector_norm(got.float() - want.float())
               / torch.linalg.vector_norm(want.float()).clamp_min(1e-12)).item()
        del got, want
        if not L.sparse_gate_passed(rel):
            self.sparse_failed_reason = "correctness gate failed: route-all rel_l2 %.5f > %s" % (rel, L.SPARSE_GATE_REL_L2)
            logging.warning("%s %s; using dense attention" % (TAG, self.sparse_failed_reason))
            return False

        def run_sparse():
            return sol_attn(qb, kb, vb, tau=self.sparse_tau, thresh_type="diag",
                            sink_start=0, sink_tokens=self.video_start)

        def timeit(fn, n=3):
            fn()
            torch.cuda.synchronize(qb.device)
            t0 = time.perf_counter()
            for _ in range(n):
                fn()
            torch.cuda.synchronize(qb.device)
            return (time.perf_counter() - t0) / n

        t_sparse = timeit(run_sparse)
        t_incumbent = timeit(incumbent)
        speedup = t_incumbent / max(t_sparse, 1e-9)
        decided = L.sparse_keep(speedup, self.sparse_mode)
        logging.info("%s sparse attention gate on %s: rel_l2 %.5f, kernel compile %.1fs, sparse %.2f ms vs incumbent "
                     "%.2f ms (%.2fx) -> %s" % (TAG, torch.cuda.get_device_name(qb.device), rel, compile_s,
                                                t_sparse * 1000, t_incumbent * 1000, speedup,
                                                "ENABLED" if decided else "disabled (not faster on this GPU)"))
        if not decided:
            self.sparse_resolved = False
            return False
        self.sparse_resolved = True
        self._gate_done.add(key)
        return True

    def attention_override(self, func, q, k, v, heads, **kwargs):
        try:
            if self._sparse_eligible(q, heads, kwargs):
                sol_attn = load_sol_attn()
                if sol_attn is None:
                    self.sparse_failed_reason = _SOL_ATTN_ERROR or "sparse kernel import failed"
                else:
                    return self._sparse_attention(sol_attn, func, q, k, v, heads, kwargs)
        except Exception as e:  # never let the sparse path break sampling
            self.sparse_failed_reason = "%s: %s" % (type(e).__name__, e)
            logging.warning("%s sparse attention failed, falling back to dense for the rest of this process: %s"
                            % (TAG, self.sparse_failed_reason))
        self.dense_calls += 1
        return func(q, k, v, heads, **kwargs)

    def _sparse_attention(self, sol_attn, func, q, k, v, heads, kwargs):
        import torch
        # [1, H, S, D] -> contiguous bf16 [1, S, H, D] (the kernel contract)
        qb = q.transpose(1, 2).to(torch.bfloat16).contiguous()
        kb = k.transpose(1, 2).to(torch.bfloat16).contiguous()
        vb = v.transpose(1, 2).to(torch.bfloat16).contiguous()

        if self.sparse_resolved is not True or (qb.device.index, qb.shape[1]) not in self._gate_done:
            ok = self._gate_and_bench(sol_attn, qb, kb, vb,
                                      incumbent=lambda: func(q, k, v, heads, **kwargs))
            if not ok:
                self.dense_calls += 1
                return func(q, k, v, heads, **kwargs)

        out = sol_attn(qb, kb, vb, tau=self.sparse_tau, thresh_type="diag",
                       sink_start=0, sink_tokens=self.video_start)
        # The sink keeps the prefix exact as keys; its own query rows must be dense.
        vs = self.video_start
        out[:, :vs] = _dense_bthd(qb[:, :vs], kb, vb)
        self.sparse_calls += 1
        s = out.shape[1]
        return out.reshape(1, s, heads * 128).to(q.dtype)


def chain_attention_override(opt, previous):
    """Attention override that runs `opt` first and hands its dense fallback to the earlier override."""
    if previous is None:
        return opt.attention_override

    def chained(func, *args, **kw):
        def inner(q, k, v, heads, **kw2):
            return previous(func, q, k, v, heads, **kw2)
        return opt.attention_override(inner, *args, **kw)
    return chained
