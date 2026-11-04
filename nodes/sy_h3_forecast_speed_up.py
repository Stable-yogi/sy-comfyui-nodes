"""H3 Forecast Speed Up SY: makes MiniMax H3 videos and H3 pictures faster by skipping the big network on some steps.

Same method as MOSS Speed Up SY (forecast of the last block from the steps that ran, Chebyshev curves over the
step position, ridge regression; idea: arXiv:2603.01623, MIT licence). Our own code; the plan, preset and forecast
functions are shared with sy_moss_speed_up.

What is different for H3 (ComfyUI 0.44 comfy/ldm/minimax):
- the 50 blocks are patched as ("double_block", i), the hidden state is 2D (tokens, width), batch is always 1;
- the tokens are packed [text | reference rows | audio | video]; the output head reads only audio and video,
  so that span (the last two segments of args["layout"]) is saved and forecast;
- the model input is a [video, audio] pair, so the token count is read from the layout at block 0, and a skip
  whose saved span no longer fits (new size or length) turns back into a real step there.
"""
import contextlib
import math

try:
    from ._sy_common import category, register
    from . import sy_moss_speed_up as F
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import sy_moss_speed_up as F

PRESETS = F.PRESETS
READOUT_STEPS = (4, 8, 20, 30)
TITLE = "H3 Forecast Speed Up SY"


def target_span(segments):
    """Pure function. (start, stop) of the audio + video rows: the rows the output head reads.
    `segments` is the layout list of (start, stop, kind). Raises ValueError when they are missing or not side by side."""
    spans = [(a, b) for a, b, kind in segments if kind in ("audio", "video")]
    if not spans:
        raise ValueError("the H3 layout has no audio or video rows")
    spans.sort()
    for (a0, b0), (a1, b1) in zip(spans, spans[1:]):
        if b0 != a1:
            raise ValueError("the audio and video rows are not side by side in the H3 layout")
    return spans[0][0], spans[-1][1]


class H3State(F.SpeedState):
    """F.SpeedState with the shape check moved to block 0, where the H3 layout is known."""

    def decide(self, key, sigma, sigmas, batch=1, hw=0):
        sig_key = tuple(round(float(s), 6) for s in sigmas) if sigmas else None
        steps = max((len(sigmas) - 1) if sigmas else 1, 1)
        if sig_key != self.sig_key:
            self._new_run(sig_key, steps)
        pos = F.step_position(sigmas, sigma)
        s = self.streams.setdefault(key, F._Stream())
        if pos is not None and s.last is not None and pos < s.last - 1e-6:  # same sigmas sampled again from the start
            self._new_run(sig_key, steps)
            s = self.streams.setdefault(key, F._Stream())
        if pos is None:
            return ("real", s, None)
        s.last = pos
        idx = min(int(math.floor(pos + 1e-6)), len(self.plan) - 1)
        if self.plan[idx] or len(s.h) < 2:
            return ("real", s, pos)
        return ("skip", s, pos)


def _outside_step_memory():
    """ComfyUI 0.44 plans the GPU memory of each block; tensors kept past the block (saved steps, the forecast)
    must be made with that plan paused, like ComfyUI's own H3 control patch does. Older ComfyUI: nothing to pause."""
    try:
        import comfy.model_prefetch as P
        return P.pause_malloc_graph()
    except (ImportError, AttributeError):
        return contextlib.nullcontext()


def _make_block(state, first, last):
    def block(args, extra):
        cur = state.current
        if cur is None:
            return extra["original_block"](args)
        if first:
            cur["span"] = target_span(args["layout"].segments)
            if cur["mode"] == "skip":
                s = cur["stream"]
                n = cur["span"][1] - cur["span"][0]
                if s.h[-1].shape[0] != n or s.h[-1].shape[1] != args["img"].shape[-1]:
                    cur["mode"] = "real"  # size or length changed since the saved steps
                else:
                    with _outside_step_memory():
                        cur["pred"] = F.forecast(s.t, s.h, cur["pos"], state.steps, state.degree, state.lam)
        a, b = cur["span"]
        if cur["mode"] == "skip":
            img = args["img"]
            if last:
                img[a:b] = cur["pred"].to(img.dtype)
            return {"img": img}
        out = extra["original_block"](args)
        if last:
            with _outside_step_memory():
                cur["grab"].append(out["img"][a:b].detach().clone())
        return out
    return block


def _make_wrapper(state, prev):
    def wrapper(apply_model, args):
        x, ts, c = args["input"], args["timestep"], args["c"]
        sig = c.get("transformer_options", {}).get("sample_sigmas")
        sigmas = [float(v) for v in sig.flatten().tolist()] if sig is not None else None
        key = tuple(args.get("cond_or_uncond", ()))
        mode, stream, pos = state.decide(key, float(ts.flatten()[0]), sigmas)
        cur = {"mode": mode, "stream": stream, "pos": pos, "grab": [], "span": None, "pred": None}
        state.current = cur
        try:
            out = prev(apply_model, args) if prev is not None else apply_model(x, ts, **c)
        finally:
            state.current = None
        if cur["mode"] == "skip":
            state.skipped += 1
            state.skipped_steps.add(int(math.floor(pos + 1e-6)))
        else:
            state.real += 1
            if cur["grab"]:
                if stream.h and stream.h[-1].shape != cur["grab"][0].shape:  # new size: the old steps cannot be mixed in
                    stream.t, stream.h = [], []
                state.keep(stream, pos, cur["grab"][0])
        if pos is not None and pos >= state.steps - 1 - 1e-6:
            state.finished.add(key)
            if len(state.finished) >= len(state.streams):
                _report(state)
        return out
    return wrapper


def _report(state):
    text = F.run_summary(state.steps, len(state.skipped_steps), state.real, state.skipped)
    if text == state.last_summary:
        return
    state.last_summary = text
    print("[SY] %s: %s" % (TITLE, text), flush=True)
    if state.node_id is None:
        return
    try:
        from server import PromptServer
        srv = PromptServer.instance
        srv.send_sync("executed", {"node": state.node_id, "display_node": state.node_id,
                                   "output": {"sy_text": [{"name": "last run", "text": text}]},
                                   "prompt_id": getattr(srv, "last_prompt_id", None)})
    except Exception as e:
        print("[SY] %s: could not show the count on the node: %s" % (TITLE, e))


def is_h3(dm):
    """Pure check: the native ComfyUI MiniMax H3 network (comfy/ldm/minimax)."""
    return dm is not None and "minimax" in type(dm).__module__ and hasattr(dm, "blocks")


def has_block_patches(model):
    """Pure check: another node already replaces the H3 blocks (for example H3 Speed Optimizer SY)."""
    reps = (getattr(model, "model_options", {}) or {}).get("transformer_options", {}).get("patches_replace", {})
    return any(k[0] == "double_block" for k in reps.get("dit", {}))


def patch_model(model, preset, manual, degree, lam, history, node_id=None):
    """Clone the model and add the speed-up. Off returns the model unchanged."""
    if preset == "off":
        return model
    F.settings_for(preset, 20, **manual)  # checks the numbers now, not halfway through sampling
    dm = F._diffusion_model(model)
    if not is_h3(dm):
        raise ValueError("%s works with MiniMax H3 models only (ComfyUI 0.44 or newer). "
                         "This model is %s. Set preset to off or remove the node." % (TITLE, type(dm).__name__ if dm is not None else "unknown"))
    if has_block_patches(model):
        raise ValueError("%s: another speed-up node (for example H3 Speed Optimizer SY) already changes the H3 blocks. "
                         "Use one of them, not both." % TITLE)
    m = model.clone()
    state = H3State(preset, manual, degree, lam, history, node_id)
    n = len(dm.blocks)
    for i in range(n):
        m.set_model_patch_replace(_make_block(state, i == 0, i == n - 1), "dit", "double_block", i)
    m.set_model_unet_function_wrapper(_make_wrapper(state, m.model_options.get("model_function_wrapper")))
    return m


class SYH3ForecastSpeedUp:
    DESCRIPTION = ("Makes MiniMax H3 videos and H3 pictures faster. On some steps the big network is skipped and its "
                   "result is predicted from the steps before. Use it with 20 or more steps: the 4-step fast mode has "
                   "nothing to skip. mild changes the result very little, strong is faster but can change small details.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "plan")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "A MiniMax H3 model (ComfyUI 0.44 or newer). Do not also use H3 Speed Optimizer SY."}),
                "preset": (PRESETS, {"default": "mild", "tooltip": "off = normal speed. mild skips about 3 in 10 steps, middle about 4, strong about 5. manual uses the four numbers below."}),
                "warmup_steps": ("INT", {"default": 6, "min": 2, "max": 200, "tooltip": "manual only. The first steps always run: they set the shape and motion."}),
                "window": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 8.0, "step": 0.25, "tooltip": "manual only. After the warm-up one step in this many runs. 2 = every other step."}),
                "window_growth": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 4.0, "step": 0.05, "tooltip": "manual only. The window grows by this after each run, so later steps skip more."}),
                "tail_steps": ("INT", {"default": 2, "min": 1, "max": 50, "tooltip": "manual only. The last steps always run: they draw the fine detail."}),
            },
            "optional": {
                "curve_degree": ("INT", {"default": 4, "min": 1, "max": 8, "tooltip": "How bendy the prediction curve is. 4 works for most videos."}),
                "smoothing": ("FLOAT", {"default": 0.1, "min": 0.001, "max": 10.0, "step": 0.01, "tooltip": "Higher = a calmer, more careful prediction."}),
                "history": ("INT", {"default": 8, "min": 2, "max": 32, "tooltip": "How many past real steps the prediction looks at. Each one keeps a copy of the video rows in memory."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    def run(self, model, preset, warmup_steps, window, window_growth, tail_steps,
            curve_degree=4, smoothing=0.1, history=8, unique_id=None):
        manual = {"warmup_steps": warmup_steps, "window": window, "window_growth": window_growth, "tail_steps": tail_steps}
        out = patch_model(model, preset, manual, curve_degree, smoothing, history, unique_id)
        return (out, F.readout(preset, READOUT_STEPS, **manual))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3ForecastSpeedUp", SYH3ForecastSpeedUp)
NODE_DISPLAY_NAME_MAPPINGS["SYH3ForecastSpeedUp"] = TITLE
