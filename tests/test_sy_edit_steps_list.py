import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_edit_steps_list as m


def _raises(steps, style):
    try:
        m.build_steps(steps, style)
    except ValueError:
        return True
    return False


def run():
    f = m.build_steps
    s = ["Remove the car.", "", "Fix the light", "", "Make it blue"]
    assert f(s, "numbered") == "1. Remove the car.\n2. Fix the light\n3. Make it blue"
    assert f(s, "bullets") == "- Remove the car.\n- Fix the light\n- Make it blue"
    assert f(s, "then_words") == "First, remove the car. Then, fix the light. Finally, make it blue."
    assert f(["Only one"], "then_words") == "First, only one."
    assert f(["a", "b"], "then_words") == "First, a. Finally, b."
    assert f(["a", None, " ", "b"], "numbered") == "1. a\n2. b"
    assert _raises(["", " ", None], "numbered")
    assert _raises([], "bullets")
    assert _raises(["a"], "poem")
    assert m.SYEditStepsList().run("bullets", "x", "", "y")[0] == "- x\n- y"
    assert len(m.SYEditStepsList.INPUT_TYPES()["optional"]) == 5
    return 11  # checks
