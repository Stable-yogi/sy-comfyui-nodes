import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sampler_preset as m

SAMP = ["euler", "er_sde", "heun"]
SCHED = ["normal", "simple", "beta"]


def _raises(fn, *args, text=""):
    try:
        fn(*args)
    except ValueError as e:
        assert text in str(e), str(e)
        return
    raise SystemExit("expected ValueError")


def run():
    n = 0
    labels = m.pair_labels(m.PAIRS)
    assert labels[0] == "MOSS: er_sde + normal"; n += 1
    assert len(labels) == 9 and len(set(labels)) == 9; n += 1
    assert m.parse_label("Krea 2 Turbo: euler + simple") == ("Krea 2 Turbo", "euler", "simple"); n += 1
    for lab in labels:  # round trip
        f, s, c = m.parse_label(lab)
        assert "%s: %s + %s" % (f, s, c) == lab
        n += 1
    _raises(m.parse_label, "nonsense", text="Pick one"); n += 1
    _raises(m.parse_label, "MOSS: euler", text="Pick one"); n += 1
    out = m.pick("MOSS", "MOSS: euler + simple", 0, SAMP, SCHED)
    assert out[:4] == ("euler", "simple", 25, 4.0); n += 1
    assert out[4].startswith("MOSS: euler + simple, 25 steps, cfg 4."); n += 1
    out = m.pick("Krea 2 Turbo", "Krea 2 Turbo: euler + simple", 12, SAMP, SCHED)
    assert out[2] == 12 and out[3] == 1.0 and "Official Turbo".lower() in out[4].lower(); n += 1
    _raises(m.pick, "MOSS", "Krea 2 Turbo: euler + simple", 0, SAMP, SCHED, text="This pair is for Krea 2 Turbo. Pick a pair that starts with MOSS."); n += 1
    _raises(m.pick, "Nope", "MOSS: euler + simple", 0, SAMP, SCHED, text="unknown family"); n += 1
    _raises(m.pick, "MOSS", "MOSS: euler + normal", 0, SAMP, SCHED, text="no tested pair"); n += 1
    _raises(m.pick, "MOSS", "MOSS: er_sde + normal", 0, ["euler"], SCHED, text="er_sde"); n += 1
    _raises(m.pick, "MOSS", "MOSS: er_sde + normal", 0, SAMP, ["simple"], text="Update ComfyUI"); n += 1
    _raises(m.pick, "MOSS", "MOSS: euler + simple", -1, SAMP, SCHED, text="0 or more"); n += 1
    assert m.pick("MOSS", labels[0], 0, None, None)[0] == "er_sde"; n += 1
    assert set(m.NOTES) == set(m.PAIRS); n += 1
    spec = m.SYSamplerPreset.INPUT_TYPES()["required"]
    assert spec["pair"][1]["default"] == labels[0] and list(spec) == ["family", "pair", "steps_override"]; n += 1
    assert len(m.SYSamplerPreset().run("MOSS", "MOSS: euler + simple", 0)) == len(m.SYSamplerPreset.RETURN_TYPES); n += 1
    return n
