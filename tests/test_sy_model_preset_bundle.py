import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_model_preset_bundle as m
from _sy_sampler_names import FALLBACK_SAMPLERS, FALLBACK_SCHEDULERS


def run():
    n = 0
    assert len(m.PRESETS) >= 14
    n += 1
    for want in ("Krea 2", "Qwen Image 2.1", "Flux", "SDXL (old)", "Z-Image", "Wan 2.2 video", "LTX video",
                 "H3", "MiniMax image", "MiniMax video", "HunyuanVideo", "Qwen edit", "SD 1.5"):
        assert want in m.PRESETS, want
        n += 1
    for name in m.PRESETS:
        p = m.get_preset(name, FALLBACK_SAMPLERS, FALLBACK_SCHEDULERS)
        assert p["steps"] > 0 and p["cfg"] >= 0, name
        assert p["width"] % 16 == 0 and p["height"] % 16 == 0 and p["width"] > 0 and p["height"] > 0, name
        assert p["sampler_name"] in FALLBACK_SAMPLERS, name
        assert p["scheduler"] in FALLBACK_SCHEDULERS, name
        assert p["note"] and len(p["note"]) > 5, name
        n += 5
    # fallback when a name is missing from the valid list
    p = m.get_preset("Z-Image", ["euler", "heun"], ["normal"])
    assert p["sampler_name"] == "euler" and p["scheduler"] == "normal"
    p = m.get_preset("SD 1.5", ["heun"], ["exponential"])
    assert p["sampler_name"] == "heun" and p["scheduler"] == "exponential"
    n += 4
    try:
        m.get_preset("nope")
        raise SystemExit("unknown preset must raise")
    except ValueError:
        n += 1
    t = m.SYModelPresetBundle.INPUT_TYPES()
    assert t["required"]["preset"][0] == list(m.PRESETS)
    assert len(m.SYModelPresetBundle.RETURN_TYPES) == len(m.SYModelPresetBundle.RETURN_NAMES) == 9
    n += 2
    out = m.SYModelPresetBundle().run("Flux")
    assert out[0] == 20 and out[1] == 1.0 and out[4] == 1024
    n += 1
    # aspect option: same pixel budget in a new shape, still on the size step
    assert m.preset_size("Flux") == (1024, 1024) and m.preset_size("Flux", "preset") == (1024, 1024)
    n += 1
    w, h = m.preset_size("Flux", "16:9")
    assert (w, h) == (1360, 768) and w % 16 == 0 and h % 16 == 0 and abs(w * h - 1024 * 1024) / (1024 * 1024) < 0.05, (w, h)
    n += 1
    assert m.preset_size("Flux", "9:16") == (768, 1360)
    assert m.preset_size("Flux", "1:1") == (1024, 1024)
    n += 2
    for name in m.PRESETS:
        for asp in m.ASPECTS:
            w, h = m.preset_size(name, asp)
            step = m.size_multiple(name)
            assert w % step == 0 and h % step == 0 and w >= step and h >= step, (name, asp, w, h)
            n += 1
    assert m.size_multiple("LTX video") == 32 and m.size_multiple("Flux") == 16
    n += 1
    for bad in (("nope", "1:1"), ("Flux", "7:3")):
        try:
            m.preset_size(*bad)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    p = m.get_preset("Flux", FALLBACK_SAMPLERS, FALLBACK_SCHEDULERS)
    txt = m.preset_info("Flux", p)
    assert txt.startswith("Flux: 20 steps, cfg 1, euler / simple, 1024x1024 (1.05 MP, 1:1)") and "reshaped" not in txt
    assert "reshaped to 16:9" in m.preset_info("Flux", p, "16:9")
    n += 2
    out = m.SYModelPresetBundle().run("Flux", "16:9")
    assert out[4] == 1360 and out[5] == 768 and abs(out[7] - 1.04448) < 1e-6 and "Flux:" in out[8]
    assert m.SYModelPresetBundle().run("Flux")[:7] == m.SYModelPresetBundle().run("Flux", "preset")[:7]
    n += 2
    t2 = m.SYModelPresetBundle.INPUT_TYPES()
    assert list(t2["optional"]) == ["aspect"] and t2["optional"]["aspect"][1]["default"] == "preset"
    assert m.SYModelPresetBundle.RETURN_NAMES[:7] == ("steps", "cfg", "sampler_name", "scheduler", "width", "height", "note")
    n += 2
    return n
