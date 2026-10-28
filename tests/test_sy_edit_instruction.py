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
    assert m.SYEditInstruction.RETURN_TYPES == ("STRING",)
    return n + 3  # checks
