import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_forecast_speed_up as m


def _raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


class _Layout:
    def __init__(self, text, ref, audio, video):
        a = text + ref
        self.segments = [(0, text, "text")] + ([(text, a, "ref_img")] if ref else []) + [(a, a + audio, "audio"), (a + audio, a + audio + video, "video")]


def _fake_sampling(steps, preset, video=12, audio=4, width=8, size_change_at=None):
    """A stand-in for MiniMax H3 and a sampler: 2D hidden state, packed [text | ref | audio | video], blocks change
    rows in place like the real ones, the output head reads only audio + video."""
    import torch

    Net = type("MiniMaxH3Model", (), {"__module__": "comfy.ldm.minimax.model"})
    net = Net()
    net.blocks = list(range(5))

    class Patcher:
        def __init__(self, opts=None):
            self.model = type("M", (), {})()
            self.model.diffusion_model = net
            self.model_options = dict(opts or {"transformer_options": {}})

        def clone(self):
            return Patcher({"transformer_options": {"patches_replace": {}}})

        def set_model_patch_replace(self, patch, name, block_name, number):
            self.model_options["transformer_options"].setdefault("patches_replace", {}).setdefault(name, {})[(block_name, number)] = patch

        def set_model_unet_function_wrapper(self, fn):
            self.model_options["model_function_wrapper"] = fn

    real_runs = []

    def forward(x, t, patches, vid):
        layout = _Layout(3, 2, audio, vid)
        n = layout.segments[-1][1]
        h = torch.zeros(n, width)
        for i in range(len(net.blocks)):
            def orig(args, i=i):
                real_runs.append(i)
                args["img"].add_(float(t) * 0.1)  # in place, like the real blocks
                return {"img": args["img"]}
            h = patches[("double_block", i)]({"img": h, "layout": layout}, {"original_block": orig})["img"]
        a, b = m.target_span(layout.segments)
        return h[a:b].clone()

    p = m.patch_model(Patcher(), preset, {}, 4, 0.1, 8, None)
    wrap = p.model_options["model_function_wrapper"]
    patches = p.model_options["transformer_options"]["patches_replace"]["dit"]
    sigmas = torch.linspace(1.0, 0.0, steps + 1)
    outs = []
    for i in range(steps):
        vid = video if size_change_at is None or i < size_change_at else video + 6
        args = {"input": [torch.ones(1, 2), torch.ones(1, 2)], "timestep": sigmas[i].reshape(1), "cond_or_uncond": [0],
                "c": {"transformer_options": {"sample_sigmas": sigmas}}}
        outs.append(wrap(lambda a, b, **c: forward(a, b, patches, vid), args))
    return outs, real_runs, net


def run():
    n = 0
    # the audio + video span from the packed layout
    assert m.target_span(_Layout(3, 2, 4, 12).segments) == (5, 21); n += 1
    assert m.target_span(_Layout(7, 0, 2, 9).segments) == (7, 18); n += 1
    assert _raises(m.target_span, [(0, 4, "text")]); n += 1
    assert _raises(m.target_span, [(0, 4, "audio"), (5, 9, "video")]); n += 1
    # presets and readout come from the shared MOSS functions; 4 steps (fast mode) skips nothing
    for k in ("mild", "middle", "strong"):
        q = m.F.plan_for(k, 4)
        assert all(q), (k, q); n += 1
    r = m.F.readout("mild", m.READOUT_STEPS)
    assert "4 steps: 0 skipped (0%)" in r and "20 steps:" in r; n += 1
    # off leaves the model alone; a model that is not H3 is refused; MOSS is refused too
    marker = object()
    assert m.patch_model(marker, "off", {}, 4, 0.1, 8) is marker; n += 1
    assert _raises(m.patch_model, type("P", (), {"model": None})(), "mild", {}, 4, 0.1, 8); n += 1
    moss = type("MOSSImage", (), {"__module__": "comfy.ldm.moss_image.model"})()
    moss.layers = [0]
    assert not m.is_h3(moss) and not m.is_h3(None); n += 1
    # another node already patches the H3 blocks: refused with a clear message
    busy = type("P", (), {})()
    busy.model_options = {"transformer_options": {"patches_replace": {"dit": {("double_block", 0): None}}}}
    assert m.has_block_patches(busy); n += 1
    assert not m.has_block_patches(type("P", (), {"model_options": {}})()); n += 1
    # node shape
    it = m.SYH3ForecastSpeedUp.INPUT_TYPES()
    assert it["required"]["preset"][0] == m.PRESETS and it["required"]["preset"][1]["default"] == "mild"; n += 1
    assert m.SYH3ForecastSpeedUp.RETURN_TYPES == ("MODEL", "STRING"); n += 1
    assert "SYH3ForecastSpeedUp" in m.NODE_CLASS_MAPPINGS; n += 1

    try:
        import torch
    except ImportError:
        return n
    # a fake H3 run: the blocks run on the planned steps only, skipped steps still give finite output of the right size
    outs, runs, net = _fake_sampling(20, "mild")
    plan = m.F.plan_for("mild", 20)
    assert len(runs) == sum(plan) * len(net.blocks), (len(runs), sum(plan)); n += 1
    assert all(torch.isfinite(o).all() and o.shape == (16, 8) for o in outs); n += 1
    _, runs2, _ = _fake_sampling(20, "strong")
    assert len(runs2) == sum(m.F.plan_for("strong", 20)) * 5; n += 1
    # the length changes halfway: the first skip after the change runs the full model instead
    outs3, runs3, _ = _fake_sampling(20, "strong", size_change_at=10)
    assert len(runs3) > len(runs2) and outs3[-1].shape == (22, 8); n += 1
    return n
