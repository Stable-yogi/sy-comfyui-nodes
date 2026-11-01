import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_negative_prompt_presets as m


def _fails(fn, args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert len(m.PRESET_NAMES) == 13; n += 1
    for name in m.PRESET_NAMES:
        assert m.negative_prompt(name) == m.PRESETS[name] and "," in m.PRESETS[name]
        n += 1
    assert m.negative_prompt("minimal", "extra hands, ") == "blurry, lowres, watermark, extra hands"; n += 1
    assert m.negative_prompt("minimal", "only this", "replace preset") == "only this"; n += 1
    assert m.negative_prompt("minimal", "  ") == m.PRESETS["minimal"]; n += 1
    for call in (lambda: m.negative_prompt("nope"), lambda: m.negative_prompt("minimal", "", "replace preset"),
                 lambda: m.negative_prompt("minimal", "x", "bad mode"), lambda: m.negative_prompt("minimal", 4)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYNegativePromptPresets().run("minimal", "add after preset", "x")[0].endswith(", x"); n += 1
    h = m.negative_prompt
    assert h("minimal", "", "add after preset", "lowres") == "blurry, watermark"; n += 1
    assert h("minimal", "", "add after preset", " LowRes , nothing") == "blurry, watermark"; n += 1
    assert h("minimal", "Blurry, extra", "add after preset", "", True) == "blurry, lowres, watermark, extra"; n += 1
    assert h("minimal", "Blurry, extra") == "blurry, lowres, watermark, Blurry, extra"; n += 1
    assert h("minimal", "", "add after preset", "", False, 1.2) == "(blurry, lowres, watermark:1.2)"; n += 1
    assert h("minimal", "", "add after preset", "", False, 1.0) == "blurry, lowres, watermark"; n += 1
    assert h("minimal", "(a, b:1.1), c", "add after preset", "c", True) == "blurry, lowres, watermark, (a, b:1.1)"; n += 1
    assert h("minimal", "", "add after preset", "blurry, lowres, watermark") == ""; n += 1
    assert h("minimal", "", "add after preset", "", False, 0) == "blurry, lowres, watermark"; n += 1
    for bad_args in (("minimal", "", "add after preset", "", False, 2.5), ("minimal", "", "add after preset", "", False, -1), ("minimal", "", "add after preset", 5)):
        assert _fails(h, bad_args)
    assert m._split_terms("a, (b, c:1), d,,") == ["a", "(b, c:1)", "d"]; n += 1
    assert m.negative_info("minimal", "add after preset", "a, b, c") == "3 terms from preset 'minimal'."; n += 1
    assert m.negative_info("minimal", "replace preset", "a") == "1 term from your own words only."; n += 1
    assert "video" in m.PRESET_NAMES and "3d render" in m.PRESET_NAMES and "no text or logos" in m.PRESET_NAMES; n += 1
    assert m.SYNegativePromptPresets().run("minimal", "add after preset") == ("blurry, lowres, watermark", 3, "3 terms from preset 'minimal'."); n += 1
    assert m.SYNegativePromptPresets().run("minimal", "add after preset", "", "lowres", False, 0.0)[1] == 2; n += 1
    assert m.SYNegativePromptPresets.RETURN_NAMES == ("negative_prompt", "term_count", "info"); n += 1
    return n
