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
    assert len(m.SYModelPresetBundle.RETURN_TYPES) == len(m.SYModelPresetBundle.RETURN_NAMES) == 7
    n += 2
    out = m.SYModelPresetBundle().run("Flux")
    assert out[0] == 20 and out[1] == 1.0 and out[4] == 1024
    n += 1
    return n
