import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_edit_preset_pick as m


def run():
    n = 0
    assert len(m.PRESETS) == 8
    n += 1
    for key, text in m.PRESETS.items():
        assert m.pick_preset(key) == text and text.endswith(".") and text.count(". ") == 0
        n += 1
    assert m.pick_preset("fix_lighting", "  my own  ") == "my own"
    assert m.pick_preset("fix_lighting", "   ") == m.PRESETS["fix_lighting"]
    assert m.pick_preset("fix_lighting", None) == m.PRESETS["fix_lighting"]
    try:
        m.pick_preset("nope")
        raise SystemExit("bad preset must raise")
    except ValueError:
        pass
    assert m.SYEditPresetPick().run("make_it_night")[0] == m.PRESETS["make_it_night"]
    assert m.SYEditPresetPick.RETURN_TYPES == ("STRING",)
    return n + 6  # checks
