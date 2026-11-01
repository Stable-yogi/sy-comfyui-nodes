import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_edit_instruction as m


def _raises(*args, **kw):
    try:
        m.build_edit_instruction(*args, **kw)
    except ValueError:
        return True
    return False


def run():
    f = m.build_edit_instruction
    n = 0
    cases = [
        (("replace", "hat", "a red cap", False), "Replace the hat with a red cap."),
        (("remove", "car", "", False), "Remove the car."),
        (("remove", "car"), "Remove the car. Keep everything else exactly the same."),
        (("add", "table", "a vase"), "Add a vase to the table. Keep everything else exactly the same."),
        (("recolour", "shirt", "blue", False), "Change the colour of the shirt to blue."),
        (("restyle", "photo", "oil painting", False), "Change the style of the photo to oil painting."),
        (("change_background", "man", "a beach", False), "Change the background behind the man to a beach."),
        (("fix_lighting", "face", "", False), "Fix the lighting on the face."),
        (("remove", "car", "", False, "Also the shadow"), "Remove the car. Also the shadow."),
        (("replace", "  hat. ", " cap. ", False), "Replace the hat with cap."),
        (("remove", "dog", "ignored", False), "Remove the dog."),
    ]
    for args, want in cases:
        assert f(*args) == want, (args, f(*args))
        n += 1
    assert _raises("remove", "")
    assert _raises("remove", "   ")
    n += 2
    for a in m.NEEDS_VALUE:
        assert _raises(a, "x", "")
        n += 1
    assert _raises("dance", "x")
    assert m.SYEditInstruction().run("remove", "car", False)[0] == "Remove the car."
    assert m.SYEditInstruction.RETURN_TYPES == ("STRING", "STRING")
    assert f("replace", "the hat", "a cap", False) == "Replace the hat with a cap."; n += 1
    assert f("remove", "An old car", "", False) == "Remove the old car."; n += 1
    assert f("remove", "theme park", "", False) == "Remove the theme park."; n += 1
    assert f("recolour", "shirt", "blue", False, "", "the face and the pose") == "Change the colour of the shirt to blue. Keep the face and the pose exactly the same."; n += 1
    assert f("remove", "car", "", True, "", " the face. ") == "Remove the car. Keep the face exactly the same. Keep everything else exactly the same."; n += 1
    assert f("remove", "car", "", True, "", "") == "Remove the car. Keep everything else exactly the same."; n += 1
    assert m.instruction_notes("remove", "car", "x") == "to_value was ignored: 'remove' does not need it."; n += 1
    assert m.instruction_notes("replace", "the hat", "cap") == "The word 'the' at the start of target was dropped."; n += 1
    assert m.instruction_notes("replace", "hat", "cap") == "OK: no warnings."; n += 1
    assert "70 words long" in m.instruction_notes("remove", "car", "", "word " * 70); n += 1
    out = m.SYEditInstruction().run("remove", "car", False, "gone", "", "")
    assert out == ("Remove the car.", "to_value was ignored: 'remove' does not need it."); n += 1
    assert m.SYEditInstruction.RETURN_NAMES == ("instruction", "notes"); n += 1
    return n + 3  # checks
