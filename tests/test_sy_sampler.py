import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sampler as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.pick_steps(False, 20, 4) == 20 and m.pick_steps(True, 20, 4) == 4; n += 1
    assert "fast_steps" in must_raise(m.pick_steps, True, 20, 0); n += 1
    assert "steps" in must_raise(m.pick_steps, False, 0, 4); n += 1
    assert m.needs_cfg_guider(True, 4.0) is True; n += 1
    assert m.needs_cfg_guider(True, 1.0) is False and m.needs_cfg_guider(False, 4.0) is False; n += 1
    assert m.check_seed(5) == 5 and m.check_seed(m.MAX_SEED) == m.MAX_SEED; n += 1
    assert "seed" in must_raise(m.check_seed, -1) and "seed" in must_raise(m.check_seed, m.MAX_SEED + 1); n += 1
    t = m.settings_text(7, 4, True, 1.0, "euler", "simple", 1.0, "basic")
    assert t.splitlines() == ["mode: fast", "steps: 4", "cfg: 1 (basic guider)", "sampler: euler", "scheduler: simple", "denoise: 1", "seed: 7"], t; n += 1
    assert "mode: quality" in m.settings_text(1, 20, False, 4.5, "dpmpp_2m", "karras", 0.5, "CFG"); n += 1
    assert m.SYSampler.RETURN_NAMES == ("latent", "denoised", "settings", "seed"); n += 1
    spec = m.SYSampler.INPUT_TYPES()
    assert spec["required"]["fast_mode"][0] == "BOOLEAN" and "negative" in spec["optional"]; n += 1
    assert m.SYSampler.FUNCTION == "run" and hasattr(m.SYSampler, "run"); n += 1
    return n
