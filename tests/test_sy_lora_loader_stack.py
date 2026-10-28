import os
import sys

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
    assert m.SYLoraLoaderStack.RETURN_TYPES == ("MODEL", "CLIP", "STRING")
    n += 1
    return n
