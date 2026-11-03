"""MOSS Speed Up SY: makes MOSS-Image pictures faster by skipping the big network on some steps.

Idea: Han, Shi, Li, Ye, Guo, Ermon, "Adaptive Spectral Feature Forecasting for Diffusion Sampling
Acceleration" (arXiv:2603.01623, MIT licence). On a skipped step the 42 blocks of the model do not run.
What the last block would give for the picture tokens is predicted from the steps that did run
(Chebyshev curves over the step position, ridge regression), and only the small output head runs.
Our own code, ported from the Stable Yogi Forge MOSS extension.

How it plugs in (no core edit): block replace patches on every block plus a model function wrapper.
The wrapper finds the step position from the sampler's own sigma list, so it works with every
sampler (er_sde, euler, dpmpp ...), and decides per call: run the blocks or forecast.
"""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PRESETS = ["off", "mild", "middle", "strong", "manual"]
# warm-up share of the steps, first window, window growth, tail steps
PRESET_VALUES = {
    "mild": (0.32, 2.0, 0.0, 2),
    "middle": (0.24, 2.0, 0.25, 2),
    "strong": (0.16, 2.0, 0.5, 2),
}
READOUT_STEPS = (20, 25, 30, 50)
TITLE = "MOSS Speed Up SY"


def build_plan(steps, warmup, window, growth, tail):
    """Pure function. One bool per step, True = the network runs.
    The first `warmup` and last `tail` steps always run. In between one step in every floor(window)
    runs, and the window grows by `growth` after each run."""
    steps = int(steps)
    if steps < 1:
        raise ValueError("steps must be 1 or more, got %r" % steps)
    real = [False] * steps
    for n in range(min(int(warmup), steps)):
        real[n] = True
    for n in range(max(steps - int(tail), 0), steps):
        real[n] = True
    gap, ws = 0, float(window)
    for n in range(int(warmup), steps):
        if real[n]:
            continue
        if (gap + 1) % max(math.floor(ws), 1) == 0:
            real[n] = True
            ws = round(ws + float(growth), 3)
            gap = 0
        else:
            gap += 1
    return real


def settings_for(preset, steps, warmup_steps=8, window=2.0, window_growth=0.25, tail_steps=2):
    """Pure function. The plan settings for one preset and step count. None for off.
    The presets scale the warm-up with the step count; manual uses the four numbers as given."""
    if preset not in PRESETS:
        raise ValueError("preset must be one of %s, got %r" % (", ".join(PRESETS), preset))
    if preset == "off":
        return None
    if preset == "manual":
        warmup, win, growth, tail = int(warmup_steps), float(window), float(window_growth), int(tail_steps)
    else:
        share, win, growth, tail = PRESET_VALUES[preset]
        warmup = max(2, int(round(int(steps) * share)))
    if warmup < 2:
        raise ValueError("warmup_steps must be 2 or more: the forecast needs two real steps to start from")
    if win < 1.0:
        raise ValueError("window must be 1.0 or more, got %r" % win)
    if growth < 0:
        raise ValueError("window_growth must be 0 or more, got %r" % growth)
    if tail < 1:
        raise ValueError("tail_steps must be 1 or more: the last step must run the full model")
    return {"warmup": warmup, "window": win, "growth": growth, "tail": tail}


def plan_for(preset, steps, **manual):
    """Pure function. The plan list for a preset (all True for off)."""
    s = settings_for(preset, steps, **manual)
    if s is None:
        return [True] * int(steps)
    return build_plan(steps, s["warmup"], s["window"], s["growth"], s["tail"])


def plan_picture(plan):
    """Pure function. R = the model runs, . = skipped (forecast)."""
    return "".join("R" if r else "." for r in plan)


def readout(preset, step_counts=READOUT_STEPS, **manual):
    """Pure function. The text the node shows before a run: how many steps each step count skips."""
    if preset == "off":
        return "Off: every step runs the full model. Nothing is skipped."
    lines = ["Preset %s. R = model runs, . = skipped." % preset]
    for steps in step_counts:
        p = plan_for(preset, steps, **manual)
        skip = len(p) - sum(p)
        lines.append("%d steps: %d skipped (%d%%)  %s" % (steps, skip, round(100.0 * skip / len(p)), plan_picture(p)))
    lines.append("After a run the real count shows here and in the console.")
    return "\n".join(lines)


def step_position(sigmas, sigma):
    """Pure function. Where `sigma` sits in the sampler's sigma list, as a step number (may be fractional
    for samplers that call the model between steps). None when it is outside the list."""
    if not sigmas or len(sigmas) < 2:
        return None
    for i in range(len(sigmas) - 1):
        hi, lo = float(sigmas[i]), float(sigmas[i + 1])
        if abs(sigma - hi) <= 1e-5 * max(1.0, abs(hi)):
            return float(i)
        if hi > sigma > lo:
            return i + (hi - sigma) / (hi - lo)
    return None


def run_summary(steps, steps_skipped, real, skipped):
    """Pure function. The line shown after a run. A step can have two model calls (with and without the prompt)."""
    total = real + skipped
    pct = round(100.0 * skipped / total) if total else 0
    return "%d steps: %d skipped, %d ran. Model calls: %d of %d skipped (%d%% fewer)." % (
        steps, steps_skipped, steps - steps_skipped, skipped, total, pct)


def _cheb(tau, degree):
    """(len(tau), degree+1) Chebyshev T0..Tdegree on tau in [-1, 1]."""
    import torch
    tau = tau.reshape(-1, 1)
    cols = [torch.ones_like(tau)]
    if degree >= 1:
        cols.append(tau)
    for _ in range(2, degree + 1):
        cols.append(2 * tau * cols[-1] - cols[-2])
    return torch.cat(cols[: degree + 1], dim=1)


def forecast(ts, hs, t_star, steps, degree=4, lam=0.1):
    """Predict the hidden state at step position t_star from the saved (ts, hs) pairs."""
    import torch
    end = max(int(steps) - 1, 1)
    tau = lambda v: 2.0 * torch.as_tensor(v, dtype=torch.float64) / end - 1.0
    X = _cheb(tau(list(ts)), degree)
    xs = _cheb(tau([float(t_star)]), degree)
    A = X.T @ X + float(lam) * torch.eye(X.shape[1], dtype=torch.float64)
    w = (xs @ torch.linalg.solve(A, X.T)).reshape(-1).tolist()
    out = None
    for wk, hk in zip(w, hs):
        term = hk.float() * wk
        out = term if out is None else out.add_(term)
    return out


class _Stream:
    """Saved hidden states of one cond / uncond stream."""

    def __init__(self):
        self.t, self.h, self.last = [], [], None


class SpeedState:
    """Lives on the patched model. Decides per model call and counts what ran."""

    def __init__(self, preset, manual, degree, lam, history, node_id=None):
        self.preset, self.manual = preset, manual
        self.degree, self.lam, self.history = int(degree), float(lam), int(history)
        self.node_id = node_id
        self.sig_key = None
        self.steps = 0
        self.plan = []
        self.streams = {}
        self.real = 0
        self.skipped = 0
        self.skipped_steps = set()
        self.finished = set()
        self.current = None  # set for the length of one model call
        self.last_summary = ""

    def _new_run(self, sig_key, steps):
        self.sig_key, self.steps = sig_key, steps
        self.plan = plan_for(self.preset, steps, **self.manual)
        self.streams, self.real, self.skipped = {}, 0, 0
        self.skipped_steps, self.finished = set(), set()
        self.last_summary = ""

    def decide(self, key, sigma, sigmas, batch, hw):
        """Returns ("real", stream, pos) or ("skip", prediction, pos)."""
        sig_key = tuple(round(float(s), 6) for s in sigmas) if sigmas else None
        steps = max((len(sigmas) - 1) if sigmas else 1, 1)
        if sig_key != self.sig_key:
            self._new_run(sig_key, steps)
        pos = step_position(sigmas, sigma)
        s = self.streams.setdefault(key, _Stream())
        if pos is not None and s.last is not None and pos < s.last - 1e-6:  # same sigmas sampled again from the start
            self._new_run(sig_key, steps)
            s = self.streams.setdefault(key, _Stream())
        if pos is None:  # no sigma list from the sampler: run the full model
            return ("real", s, None)
        s.last = pos
        idx = min(int(math.floor(pos + 1e-6)), len(self.plan) - 1)
        run_it = self.plan[idx] or len(s.h) < 2 or s.h[-1].shape[0] != batch or s.h[-1].shape[1] != hw
        if run_it:
            return ("real", s, pos)
        return ("skip", forecast(s.t, s.h, pos, self.steps, self.degree, self.lam), pos)

    def keep(self, s, pos, hidden):
        if pos is None:
            return
        s.t.append(float(pos))
        s.h.append(hidden)
        if len(s.h) > self.history:
            s.t, s.h = s.t[-self.history:], s.h[-self.history:]


def _report(state):
    """Print the run summary and show it on the node (best effort: the picture is never stopped by it)."""
    text = run_summary(state.steps, len(state.skipped_steps), state.real, state.skipped)
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


def _make_block(state, last):
    def block(args, extra):
        cur = state.current
        if cur is None:
            return extra["original_block"](args)
        if cur[0] == "skip":
            if not last:
                return {"img": args["img"]}
            img = args["img"].clone()
            img[:, : cur[2]] = cur[1].to(img.dtype)
            return {"img": img}
        out = extra["original_block"](args)
        if last:
            cur[3].append(out["img"][:, : cur[2]].detach().clone())
        return out
    return block


def _make_wrapper(state, prev):
    def wrapper(apply_model, args):
        x, ts, c = args["input"], args["timestep"], args["c"]
        topts = c.get("transformer_options", {})
        sig = topts.get("sample_sigmas")
        sigmas = [float(v) for v in sig.flatten().tolist()] if sig is not None else None
        hw = int(x.shape[-2]) * int(x.shape[-1])
        key = tuple(args.get("cond_or_uncond", ()))
        mode, obj, pos = state.decide(key, float(ts.flatten()[0]), sigmas, int(x.shape[0]), hw)
        grab = []
        state.current = ("skip", obj, hw) if mode == "skip" else ("real", None, hw, grab)
        try:
            out = prev(apply_model, args) if prev is not None else apply_model(x, ts, **c)
        finally:
            state.current = None
        if mode == "skip":
            state.skipped += 1
            state.skipped_steps.add(int(math.floor(pos + 1e-6)))
        else:
            state.real += 1
            if grab:
                state.keep(obj, pos, grab[0])
        if pos is not None and pos >= state.steps - 1 - 1e-6:
            state.finished.add(key)
            if len(state.finished) >= len(state.streams):  # every stream (with and without the prompt) is done
                _report(state)
        return out
    return wrapper


def _diffusion_model(model):
    return getattr(getattr(model, "model", None), "diffusion_model", None)


def is_moss(dm):
    """Pure check: the native ComfyUI MOSS-Image network (comfy/ldm/moss_image)."""
    return dm is not None and "moss_image" in type(dm).__module__ and hasattr(dm, "layers")


def patch_model(model, preset, manual, degree, lam, history, node_id=None):
    """Clone the model and add the speed-up. Off returns the model unchanged."""
    if preset == "off":
        return model
    settings_for(preset, 25, **manual)  # checks the numbers now, not halfway through sampling
    dm = _diffusion_model(model)
    if not is_moss(dm):
        raise ValueError("%s works with MOSS-Image models only (ComfyUI 0.43 or newer). "
                         "This model is %s. Set preset to off or remove the node." % (TITLE, type(dm).__name__ if dm is not None else "unknown"))
    m = model.clone()
    state = SpeedState(preset, manual, degree, lam, history, node_id)
    n = len(dm.layers)
    for i in range(n):
        m.set_model_patch_replace(_make_block(state, i == n - 1), "dit", "single_block", i)
    m.set_model_unet_function_wrapper(_make_wrapper(state, m.model_options.get("model_function_wrapper")))
    return m


class SYMossSpeedUp:
    DESCRIPTION = ("Makes MOSS-Image pictures faster. On some steps the big network is skipped and its result is "
                   "predicted from the steps before. mild changes the picture very little, strong is faster but can "
                   "change small details like letters. Works with every sampler, er_sde included.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "plan")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "A MOSS-Image model (ComfyUI 0.43 or newer)."}),
                "preset": (PRESETS, {"default": "mild", "tooltip": "off = normal speed. mild skips about 3 in 10 steps, middle about 4, strong about 5. manual uses the four numbers below."}),
                "warmup_steps": ("INT", {"default": 8, "min": 2, "max": 200, "tooltip": "manual only. The first steps always run: they set the shape of the picture."}),
                "window": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 8.0, "step": 0.25, "tooltip": "manual only. After the warm-up one step in this many runs. 2 = every other step."}),
                "window_growth": ("FLOAT", {"default": 0.25, "min": 0.0, "max": 4.0, "step": 0.05, "tooltip": "manual only. The window grows by this after each run, so later steps skip more."}),
                "tail_steps": ("INT", {"default": 2, "min": 1, "max": 50, "tooltip": "manual only. The last steps always run: they draw the fine detail."}),
            },
            "optional": {
                "curve_degree": ("INT", {"default": 4, "min": 1, "max": 8, "tooltip": "How bendy the prediction curve is. 4 works for most pictures."}),
                "smoothing": ("FLOAT", {"default": 0.1, "min": 0.001, "max": 10.0, "step": 0.01, "tooltip": "Higher = a calmer, more careful prediction."}),
                "history": ("INT", {"default": 8, "min": 2, "max": 32, "tooltip": "How many past real steps the prediction looks at."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    def run(self, model, preset, warmup_steps, window, window_growth, tail_steps,
            curve_degree=4, smoothing=0.1, history=8, unique_id=None):
        manual = {"warmup_steps": warmup_steps, "window": window, "window_growth": window_growth, "tail_steps": tail_steps}
        out = patch_model(model, preset, manual, curve_degree, smoothing, history, unique_id)
        return (out, readout(preset, **manual))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MossSpeedUp", SYMossSpeedUp)
NODE_DISPLAY_NAME_MAPPINGS["SYMossSpeedUp"] = TITLE
