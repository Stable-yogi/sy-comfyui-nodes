import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_negative_prompt_presets as m


def run():
    n = 0
    assert len(m.PRESET_NAMES) == 10; n += 1
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
    return n
