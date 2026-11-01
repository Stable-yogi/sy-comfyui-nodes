import json
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lora_loader_stack as m


def _slots(**over):
    kw = {"lora_1": "None", "strength_1": 1, "lora_2": "None", "strength_2": 1,
          "lora_3": "None", "strength_3": 1, "lora_4": "None", "strength_4": 1}
    kw.update(over)
    return kw


def run():
    n = 0
    assert m.plan_loras([("a", 0.5), ("None", 1), ("b", 0), ("", 1), ("c", -1)]) == [("a", 0.5), ("c", -1.0)]
    assert m.plan_loras([("None", 1)] * 4) == []
    n += 2
    try:
        m.plan_loras([("a", 99)])
        raise SystemExit("huge strength must raise")
    except ValueError:
        n += 1
    assert m.summarize([]) == "No LoRAs applied."
    assert m.summarize([("a.safetensors", 0.8)]) == "a.safetensors (strength 0.8)"
    n += 2
    # nothing to apply: inputs pass through untouched and comfy is never imported
    model, clip = object(), object()
    out = m.SYLoraLoaderStack().run(model, clip, **_slots(lora_2="a", strength_2=0))
    assert out[0] is model and out[1] is clip and out[2] == "No LoRAs applied."
    n += 1
    try:
        m.SYLoraLoaderStack().run(model, clip, **_slots(lora_1="../evil.safetensors"))
        raise SystemExit("path must be refused")
    except ValueError:
        n += 1
    assert m.SYLoraLoaderStack.RETURN_TYPES == ("MODEL", "CLIP", "STRING", "STRING", "STRING")
    assert m.SYLoraLoaderStack.RETURN_NAMES == ("model", "clip", "applied", "info", "trigger_words")
    n += 2
    spec = m.SYLoraLoaderStack.INPUT_TYPES()
    assert list(spec["required"])[:2] == ["model", "clip"] and list(spec["optional"]) == ["bypass", "clip_scale"]
    assert len(spec["required"]) == 2 + 2 * m.SLOTS
    n += 2
    # bypass: everything passes through, even a bad file name is not opened
    out = m.SYLoraLoaderStack().run(model, clip, bypass=True, **_slots(lora_1="../evil.safetensors"))
    assert out[0] is model and out[1] is clip and out[2] == "No LoRAs applied." and "Bypassed" in out[3] and out[4] == ""
    n += 1
    # clip scale
    assert m.check_clip_scale(0) == 0.0 and m.check_clip_scale(1) == 1.0 and m.check_clip_scale("2.5") == 2.5
    n += 1
    for bad in (-0.1, 4.5, float("nan")):
        try:
            m.check_clip_scale(bad)
            raise SystemExit("bad clip_scale must raise")
        except ValueError:
            n += 1
    try:
        m.SYLoraLoaderStack().run(model, clip, clip_scale=9, **_slots())
        raise SystemExit("bad clip_scale must raise")
    except ValueError:
        n += 1
    # duplicates and info text
    assert m.duplicate_names([("a", 1.0), ("b", 1.0), ("a", 0.5), ("a", 0.2)]) == ["a"]
    assert m.duplicate_names([("a", 1.0), ("b", 1.0)]) == []
    n += 2
    t = m.build_info([("a.safetensors", 0.8)], 0.0, False, "", ["a.safetensors"])
    assert "a.safetensors (strength 0.8)" in t and "x 0" in t and "more than one slot" in t
    assert "x " not in m.build_info([("a", 1.0)], 1.0, False)
    n += 2
    # hints from a real (tiny) safetensors header
    meta = {"ss_base_model_version": "sdxl_base_v1-0", "ss_tag_frequency": json.dumps({"set1": {"1girl": 40, "red hair": 30, "solo": 40, "x": 1}, "set2": {"solo": 10}})}
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "l.safetensors")
        head = json.dumps({"__metadata__": meta, "w": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}}).encode()
        with open(path, "wb") as f:
            f.write(struct.pack("<Q", len(head)) + head + b"abcd")
        got = m.st_metadata(path)
        assert got["ss_base_model_version"] == "sdxl_base_v1-0"
        h = m.lora_hints(got)
        assert h["base"] == "sdxl_base_v1-0" and h["triggers"] == [] and h["tags"][:3] == ["solo", "1girl", "red hair"], h
        n += 2
        junk = os.path.join(d, "junk.safetensors")
        with open(junk, "wb") as f:
            f.write(b"nothing useful here")
        assert m.st_metadata(junk) == {} and m.st_metadata(os.path.join(d, "missing.safetensors")) == {}
        n += 1
    h2 = m.lora_hints({"modelspec.trigger_phrase": "zebra style, striped", "ss_tag_frequency": "not json"})
    assert h2["triggers"] == ["zebra style", "striped"] and h2["tags"] == []
    n += 1
    info, trig = m.hint_lines({"a.safetensors": h, "b.safetensors": h2, "c.safetensors": {"base": "", "triggers": [], "tags": []}})
    assert "a.safetensors was trained for: sdxl_base_v1-0" in info and "b.safetensors (trigger words): zebra style, striped" in trig
    assert "a.safetensors (most used training tags): solo, 1girl, red hair" in trig and "c.safetensors" not in trig + info
    n += 3
    return n
