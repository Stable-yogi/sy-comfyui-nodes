import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_model_loader as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.is_none("(none)") and m.is_none("") and m.is_none(None) and not m.is_none("a.safetensors"); n += 1
    assert m.with_none(["a", "b"]) == ["a", "b", "(none)"]; n += 1
    assert m.with_none(["a", "(none)"], first=True) == ["(none)", "a"]; n += 1
    p = m.plan_load("Safetensors", "m.safetensors", "(none)", "t.safetensors", "(none)", "(none)", "v.safetensors", "(none)")
    assert p == {"format": "Safetensors", "model": "m.safetensors", "encoders": ["t.safetensors"], "vae": "v.safetensors", "audio_vae": None}, p; n += 1
    g = m.plan_load("GGUF", "m.safetensors", "m-Q4.gguf", "t.safetensors", "t-Q4.gguf", "t2.safetensors", "v.safetensors", "a.safetensors")
    assert g["model"] == "m-Q4.gguf" and g["encoders"] == ["t-Q4.gguf", "t2.safetensors"] and g["audio_vae"] == "a.safetensors"; n += 1
    g2 = m.plan_load("GGUF", "m.safetensors", "m-Q4.gguf", "t.safetensors", "(none)", "(none)", "(none)", "(none)")
    assert g2["encoders"] == ["t.safetensors"] and g2["vae"] is None; n += 1  # no gguf encoder: falls back to the normal one
    assert "no GGUF model" in must_raise(m.plan_load, "GGUF", "m.safetensors", "(none)", "t", "(none)", "(none)", "v", "(none)"); n += 1
    assert "no model is picked" in must_raise(m.plan_load, "Safetensors", "(none)", "m.gguf", "t", "(none)", "(none)", "v", "(none)"); n += 1
    assert "text encoder" in must_raise(m.plan_load, "Safetensors", "m", "(none)", "(none)", "(none)", "(none)", "v", "(none)"); n += 1
    assert ".gguf" in must_raise(m.plan_load, "GGUF", "m", "wrong.safetensors", "t", "(none)", "(none)", "v", "(none)"); n += 1
    assert "format" in must_raise(m.plan_load, "Other", "m", "m", "t", "t", "(none)", "v", "(none)"); n += 1
    txt = m.info_text(g, {"m-Q4.gguf": 1536})
    assert "Format: GGUF" in txt and "m-Q4.gguf (1.5 KB)" in txt and "Text encoder 2: t2.safetensors" in txt and "Audio VAE: a.safetensors" in txt; n += 1
    assert "VAE: none" in m.info_text(g2); n += 1
    assert m.SYModelLoader.RETURN_TYPES == ("MODEL", "CLIP", "VAE", "VAE", "STRING"); n += 1
    spec = m.SYModelLoader.INPUT_TYPES()
    assert spec["required"]["format"][0] == ["Safetensors", "GGUF"] and spec["optional"]["audio_vae"][1]["default"] == "(none)"; n += 1
    return n
