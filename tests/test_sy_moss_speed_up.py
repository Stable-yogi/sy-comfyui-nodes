import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_moss_speed_up as m


def _raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def _fake_sampling(steps, preset, batch=2):
    """A stand-in for MOSS-Image and a sampler: every block adds a step-dependent amount to the picture tokens."""
    import torch

    class Layers(list):
        pass

    Net = type("MOSSImage", (), {"__module__": "comfy.ldm.moss_image.model"})
    net = Net()
    net.layers = Layers(range(6))

    class Patcher:
        def __init__(self, opts=None):
            self.model = type("M", (), {})()
            self.model.diffusion_model = net
            self.model_options = dict(opts or {"transformer_options": {}})

        def clone(self):
            p = Patcher({"transformer_options": {"patches_replace": {}}})
            return p

        def set_model_patch_replace(self, patch, name, block_name, number):
            self.model_options["transformer_options"].setdefault("patches_replace", {}).setdefault(name, {})[(block_name, number)] = patch

        def set_model_unet_function_wrapper(self, fn):
            self.model_options["model_function_wrapper"] = fn

    real_runs = []

    def forward(x, t, patches):
        # x: (B, C, H, W); tokens = H*W picture + 3 text
        B, C, H, W = x.shape
        tok = torch.cat([x.flatten(2).transpose(1, 2), torch.zeros(B, 3, C)], 1)
        for i in range(len(net.layers)):
            def orig(args, i=i):
                real_runs.append(i)
                return {"img": args["img"] + float(t) * 0.1}
            tok = patches[("single_block", i)]({"img": tok}, {"original_block": orig})["img"]
        return tok[:, : H * W].transpose(1, 2).reshape(B, C, H, W)

    p = m.patch_model(Patcher(), preset, {}, 4, 0.1, 8, None)
    wrap = p.model_options["model_function_wrapper"]
    patches = p.model_options["transformer_options"]["patches_replace"]["dit"]
    sigmas = torch.linspace(1.0, 0.0, steps + 1)
    outs = []
    for i in range(steps):
        x = torch.ones(batch, 4, 2, 2)
        t = sigmas[i].reshape(1)
        args = {"input": x, "timestep": t, "cond_or_uncond": [1, 0][:batch],
                "c": {"transformer_options": {"sample_sigmas": sigmas}}}
        outs.append(wrap(lambda a, b, **c: forward(a, b, patches), args))
    return outs, real_runs, net


def run():
    n = 0
    # plan
    p = m.build_plan(25, 8, 2.0, 0.0, 2)
    assert p[:8] == [True] * 8 and p[-2:] == [True, True]; n += 1
    assert len(p) - sum(p) == 8; n += 1
    assert m.plan_picture([True, False, True]) == "R.R"; n += 1
    assert m.build_plan(3, 8, 2.0, 0.0, 2) == [True, True, True]; n += 1
    assert _raises(m.build_plan, 0, 2, 2.0, 0.0, 1); n += 1
    # presets skip more as they get stronger, at every step count
    for steps in (12, 20, 25, 30, 50):
        skips = [len(q) - sum(q) for q in (m.plan_for(k, steps) for k in ("off", "mild", "middle", "strong"))]
        assert skips[0] == 0 and skips[0] < skips[1] < skips[2] < skips[3], (steps, skips); n += 1
    assert len(m.plan_for("mild", 25)) - sum(m.plan_for("mild", 25)) == 8; n += 1
    assert len(m.plan_for("strong", 25)) - sum(m.plan_for("strong", 25)) == 13; n += 1
    for k in ("mild", "middle", "strong"):
        q = m.plan_for(k, 25)
        assert q[0] and q[1] and q[-1]; n += 1
    # manual
    q = m.plan_for("manual", 10, warmup_steps=3, window=2.0, window_growth=0.0, tail_steps=1)
    assert m.plan_picture(q) == "RRR.R.R.RR"; n += 1
    assert _raises(m.settings_for, "manual", 10, warmup_steps=1); n += 1
    assert _raises(m.settings_for, "manual", 10, tail_steps=0); n += 1
    assert _raises(m.settings_for, "manual", 10, window=0.5); n += 1
    assert _raises(m.settings_for, "turbo", 10); n += 1
    assert m.settings_for("off", 10) is None; n += 1
    # readout
    r = m.readout("mild")
    assert "25 steps: 8 skipped (32%)" in r and "R = model runs" in r; n += 1
    assert "Nothing is skipped" in m.readout("off"); n += 1
    assert m.run_summary(25, 8, 34, 16) == "25 steps: 8 skipped, 17 ran. Model calls: 16 of 50 skipped (32% fewer)."; n += 1
    assert m.run_summary(0, 0, 0, 0).endswith("(0% fewer)."); n += 1
    # step position from the sigma list (works for any sampler)
    sig = [1.0, 0.75, 0.5, 0.25, 0.0]
    assert m.step_position(sig, 1.0) == 0.0 and m.step_position(sig, 0.5) == 2.0; n += 1
    assert abs(m.step_position(sig, 0.625) - 1.5) < 1e-9; n += 1
    assert m.step_position(sig, 2.0) is None and m.step_position(None, 0.5) is None and m.step_position([1.0], 1.0) is None; n += 1
    # off leaves the model alone; a model that is not MOSS-Image is refused
    marker = object()
    assert m.patch_model(marker, "off", {}, 4, 0.1, 8) is marker; n += 1
    assert _raises(m.patch_model, type("P", (), {"model": None})(), "mild", {}, 4, 0.1, 8); n += 1
    assert not m.is_moss(None); n += 1
    # node shape
    it = m.SYMossSpeedUp.INPUT_TYPES()
    assert it["required"]["preset"][0] == m.PRESETS and it["required"]["preset"][1]["default"] == "mild"; n += 1
    assert m.SYMossSpeedUp.RETURN_TYPES == ("MODEL", "STRING"); n += 1

    try:
        import torch
    except ImportError:
        return n
    # forecast: a straight-line hidden state is predicted almost exactly
    ts = [0, 1, 2, 3, 4, 5]
    hs = [torch.full((1, 4, 3), 2.0 + 0.5 * t) for t in ts]
    pred = m.forecast(ts, hs, 6.0, 25, degree=2, lam=1e-4)
    assert torch.allclose(pred, torch.full((1, 4, 3), 5.0), atol=0.1), pred.flatten()[:3]; n += 1
    # a fake MOSS run: the blocks run on the planned steps only, and skipped steps still give a sane picture
    outs, runs, net = _fake_sampling(25, "mild")
    plan = m.plan_for("mild", 25)
    assert len(runs) == sum(plan) * len(net.layers), (len(runs), sum(plan)); n += 1
    assert all(torch.isfinite(o).all() for o in outs); n += 1
    _, runs2, _ = _fake_sampling(25, "strong", batch=1)
    assert len(runs2) == sum(m.plan_for("strong", 25)) * 6; n += 1
    return n
