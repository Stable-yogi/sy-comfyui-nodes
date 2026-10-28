import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lora_stack_text as m
import _sy_model_files as f


def run():
    n = 0
    summary, tags = m.stack_text([("a.safetensors", 0.8), ("None", 1), ("sub/b.safetensors", 1.0), ("", 1)])
    assert tags == "<lora:a:0.8> <lora:b:1>", tags
    assert "1. a.safetensors (strength 0.8)" in summary and "2. sub/b.safetensors" in summary
    n += 2
    assert m.stack_text([("None", 1)]) == ("No LoRAs selected.", "")
    n += 1
    try:
        m.stack_text([("a.safetensors", 50)])
        raise SystemExit("huge strength must raise")
    except ValueError:
        n += 1
    assert f.lora_stem("x/y\\z.safetensors") == "z"
    assert f.lora_stem("plain") == "plain"
    assert f.fmt_strength(0.80000001) == "0.8" and f.fmt_strength(1.0) == "1" and f.fmt_strength(-0.5) == "-0.5"
    n += 3
    for bad in ("", "  ", "../x.safetensors", "/abs/x", "C:/x", "a/../b", "..\\x"):
        try:
            f.check_relative(bad)
            raise SystemExit("must reject " + repr(bad))
        except ValueError:
            n += 1
    assert f.check_relative("sub/ok.safetensors") == "sub/ok.safetensors"
    n += 1
    out = m.SYLoraStackText().run(lora_1="a.safetensors", strength_1=0.5, lora_2="None", strength_2=1,
                                  lora_3="None", strength_3=1, lora_4="None", strength_4=1)
    assert out[1] == "<lora:a:0.5>"
    assert len(m.SYLoraStackText.INPUT_TYPES()["required"]) == 8
    n += 2
    return n
