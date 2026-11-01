import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_group_picker as m


def run():
    n = 0
    assert m.parse_words("") == [] and m.parse_words(None) == []; n += 1
    assert m.parse_words(" Image, MASK ,, ") == ["image", "mask"]; n += 1
    t = ["Anima", "SDXL Loaders", "Krea 2"]
    assert m.chosen_index(t, "sdxl loaders") == 1 and m.chosen_index(t, "  Krea 2 ") == 2; n += 1
    assert m.chosen_index(t, "SDXL") == -1 and m.chosen_index(t, "") == -1 and m.chosen_index(t, None) == -1; n += 1
    assert m.chosen_index([], "x") == -1; n += 1
    assert m.plan(t, "Anima") == ["on", "off", "off"]; n += 1
    assert m.plan(t, "Krea 2") == ["off", "off", "on"]; n += 1
    assert m.plan(t, "Nope") == [] and m.plan([], "x") == []; n += 1
    assert m.off_mode_for("Save Image", "mute", "image") == "bypass"; n += 1
    assert m.off_mode_for("KSampler", "mute", "image") == "mute"; n += 1
    assert m.off_mode_for("KSampler", "bypass", "") == "bypass"; n += 1
    assert m.off_mode_for(None, "mute", "image") == "mute" and m.off_mode_for("x", "bogus", "") == "bypass"; n += 1
    cls = m.SYGroupPicker
    assert cls().run("Anima") == ("Anima",) and cls().run(None) == ("",); n += 1
    assert cls.RETURN_TYPES == ("STRING",) and cls.RETURN_NAMES == ("choice",); n += 1
    assert "SYGroupPicker" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYGroupPicker"] == "Group Picker SY"; n += 1
    return n
