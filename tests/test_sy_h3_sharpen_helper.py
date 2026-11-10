import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_sharpen_helper as m


def _refused(fn, *args, part=""):
    try:
        fn(*args)
    except ValueError as e:
        assert part in str(e), str(e)
        return
    raise SystemExit("expected ValueError")


def run():
    n = 0
    names = ["a.safetensors", "minimax_h3_open_regenerate_2k.safetensors", "open_style.safetensors"]
    assert m.pick_default(names, ("open_regenerate", "open")) == names[1]; n += 1
    assert m.pick_default(["x.safetensors"], ("open",)) == "x.safetensors"; n += 1
    assert m.pick_default([], ("open",)) == ""; n += 1
    assert m.sigma_text() == "0.909375, 0.857143, 0.666667, 0.0", m.sigma_text(); n += 1
    assert m.SHARPEN_SIGMAS[-1] == 0.0 and list(m.SHARPEN_SIGMAS) == sorted(m.SHARPEN_SIGMAS, reverse=True); n += 1
    assert m.check_inputs("open_h3.safetensors", "h3_ups.safetensors", 2.0, 1.0) == []; n += 1
    w = m.check_inputs("other.safetensors", "h3_ups.safetensors", 2.0, 0.8)
    assert len(w) == 2 and "open" in w[0] and "0.80" in w[1]; n += 1
    _refused(m.check_inputs, m.NO_LORA, "u", 2.0, 1.0, part="models/loras"); n += 1
    _refused(m.check_inputs, "open", m.NO_UPSCALER, 2.0, 1.0, part="latent_upscale_models"); n += 1
    _refused(m.check_inputs, "open", "u", 5.0, 1.0, part="between 1 and 4"); n += 1
    notes = m.build_notes(2560, 1408, 16, ["x"])
    assert "2560 x 1408" in notes and "faces can change" in notes and "NOTE x" in notes; n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
