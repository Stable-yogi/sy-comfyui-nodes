import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_character_sheet_prompt as m


def _raises(*args):
    try:
        m.build_character_sheet(*args)
    except ValueError:
        return True
    return False


def run():
    f = m.build_character_sheet
    d = {"front": True, "side": True, "back": True}
    t = f("a red-haired knight", d, "plain_white", "grid")
    assert "reference sheet of a red-haired knight." in t
    assert "front view, side view and back view" in t
    assert "neat grid" in t
    assert "same face" in t and "same outfit" in t
    assert "plain white background" in t
    assert "side by side in one row" in f("x", d, "none", "row")
    assert "background" not in f("x", d, "none", "row")
    assert "plain grey background" in f("x", d, "plain_grey", "grid")
    assert "looks transparent" in f("x", d, "transparent_look", "grid")
    one = f("x", {"face_close_up": True}, "none", "grid")
    assert "Show face close-up," in one
    assert "front view" not in one
    assert "three-quarter view" in f("x", {"three_quarter": True, "full_body": True}, "none", "grid")
    assert _raises("", d, "none", "grid")
    assert _raises("   ", d, "none", "grid")
    assert _raises("x", {}, "none", "grid")
    assert _raises("x", {"front": False}, "none", "grid")
    assert _raises("x", d, "blue", "grid")
    assert _raises("x", d, "none", "circle")
    assert m.SYCharacterSheetPrompt().run("x", True, False, False, False, False, False, "none", "grid")[0].count("front view") == 1
    return 19  # checks
