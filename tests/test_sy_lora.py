import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lora as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.plan_lora("a.safetensors", True, 1.0, 0.5, True) == (True, 1.0, 0.5, ""); n += 1
    assert m.plan_lora("a.safetensors", True, 1.0, 0.5, False) == (True, 1.0, 0.0, ""); n += 1  # no clip: text strength dropped
    assert m.plan_lora("a.safetensors", False, 1.0, 1.0, True)[0] is False and m.plan_lora("a", False, 1, 1, True)[3] == "switched off"; n += 1
    assert m.plan_lora("None", True, 1.0, 1.0, True)[3] == "no LoRA picked"; n += 1
    assert m.plan_lora("a", True, 0, 0, True)[3] == "strength is 0"; n += 1
    assert m.plan_lora("a", True, 0, 0.7, False)[3] == "strength is 0"; n += 1  # clip strength is useless without a clip
    assert m.plan_lora("a", True, 0, 0.7, True)[0] is True; n += 1  # text-only LoRA is fine
    assert "between" in must_raise(m.plan_lora, "a", True, 25, 1, True); n += 1
    P = m.POSITIONS
    assert m.merge_prompt("a cat", ["zenstyle"], P[0]) == "zenstyle, a cat"; n += 1
    assert m.merge_prompt("a cat", ["zenstyle"], P[1]) == "a cat, zenstyle"; n += 1
    assert m.merge_prompt("a cat, ZenStyle", ["zenstyle"], P[0]) == "a cat, ZenStyle"; n += 1  # no double words
    assert m.merge_prompt("", ["x", "y"], P[0]) == "x, y"; n += 1
    assert m.merge_prompt(None, [], P[0]) == ""; n += 1
    assert m.merge_prompt("p", ["a", "a", " b  c "], P[1]) == "p, a, b c"; n += 1
    assert "position" in must_raise(m.merge_prompt, "p", ["a"], "Middle"); n += 1
    assert m.info_text("a", False, 1, 1, "switched off", []) == "LoRA not applied (switched off)"; n += 1
    t = m.info_text("a.safetensors", True, 1.0, 0.5, "", ["zen"])
    assert t.startswith("a.safetensors (model 1") and t.endswith("trigger words: zen"); n += 1
    assert m.SYLora.RETURN_NAMES == ("model", "clip", "prompt", "info"); n += 1
    return n
