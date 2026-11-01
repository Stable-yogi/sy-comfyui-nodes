import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_edit_preset_pick as m


def run():
    n = 0
    assert len(m.PRESETS) == 12
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
    assert list(m.PRESETS)[:8] == ["remove_object", "fix_lighting", "colourise_black_and_white", "make_it_daytime", "make_it_night", "remove_background_to_white", "sharpen_and_clean", "change_season_to_winter"]
    assert m.SYEditPresetPick.RETURN_TYPES == ("STRING", "STRING")
    assert m.pick_with_info("fix_lighting") == (m.PRESETS["fix_lighting"], "Used preset fix_lighting."); n += 1
    t, i = m.pick_with_info("fix_lighting", " mine ")
    assert t == "mine" and i == "Used your own text (preset fix_lighting ignored)."; n += 1
    t, i = m.pick_with_info("make_it_night", "", "Keep the dog unchanged")
    assert t == m.PRESETS["make_it_night"] + " Keep the dog unchanged." and i == "Used preset make_it_night. Added your extra sentence."; n += 1
    assert m.pick_with_info("make_it_night", "", "Stop!")[0].endswith(" Stop!"); n += 1
    assert m.pick_with_info("make_it_night", "", "  ")[0] == m.PRESETS["make_it_night"]; n += 1
    assert m.pick_with_info("blur_background", "own.", "more")[0] == "own. more."; n += 1
    assert m.SYEditPresetPick().run("blur_background", "", "x") == (m.PRESETS["blur_background"] + " x.", "Used preset blur_background. Added your extra sentence."); n += 1
    assert m.SYEditPresetPick.RETURN_NAMES == ("text", "info"); n += 1
    return n + 6  # checks
