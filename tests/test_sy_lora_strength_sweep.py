import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lora_strength_sweep as m


def refuses(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    assert m.parse_strengths("0, 0.6, 0.8, 1.0") == [0.0, 0.6, 0.8, 1.0]; n += 1
    assert m.parse_strengths("1\n0.5;0.25  2") == [1.0, 0.5, 0.25, 2.0]; n += 1
    assert m.parse_strengths("-1, 0") == [-1.0, 0.0]; n += 1
    assert "at least one" in refuses(m.parse_strengths, " , "); n += 1
    assert "not a number" in refuses(m.parse_strengths, "0.6, abc"); n += 1
    assert "between -20 and 20" in refuses(m.parse_strengths, "25"); n += 1
    assert "between -20 and 20" in refuses(m.parse_strengths, "nan"); n += 1
    assert "at most 12" in refuses(m.parse_strengths, ",".join(["1"] * 13)); n += 1
    assert m.strength_label(0) == "no LoRA" and m.strength_label(0.6).startswith("LoRA 0.6"); n += 1
    assert "4 strengths" in m.sweep_info("a.safetensors", [0, 0.6, 0.8, 1.0], 1.0); n += 1
    sentinel = object()
    models, main, labels, info = m.SYLoraStrengthSweep().run(sentinel, "None", "0, 1", 1.0)
    assert models == [sentinel, sentinel] and main is sentinel and labels.split("\n")[0] == "no LoRA" and labels.split("\n")[1].startswith("LoRA 1"); n += 1
    assert "no LoRA picked" in info; n += 1
    assert m.SYLoraStrengthSweep.OUTPUT_IS_LIST == (True, False, False, False); n += 1
    assert list(m.SYLoraStrengthSweep.INPUT_TYPES()["required"]) == ["model", "lora", "strengths", "main_strength"]; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLoraStrengthSweep"] == "LoRA Strength Sweep SY"; n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
