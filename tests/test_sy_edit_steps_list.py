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
    assert len(m.SYEditStepsList.INPUT_TYPES()["optional"]) == 9
    assert f(["1. Remove the car", "2) Fix light", "- blue", "* more", "• dot"], "numbered") == "1. Remove the car\n2. Fix light\n3. blue\n4. more\n5. dot"
    assert f(["10 apples", "-5 degrees"], "bullets") == "- 10 apples\n- -5 degrees"
    assert m.strip_marker("3. x") == "x" and m.strip_marker("2.5 times") == "2.5 times"
    assert f(["Fix light.", "Make blue", "fix light"], "numbered", True) == "1. Fix light.\n2. Make blue"
    assert f(["Fix light.", "fix light"], "numbered") == "1. Fix light.\n2. fix light"
    assert f(["Remove car.", "", "Fix light"], "one_line") == "Remove car; Fix light."
    assert f(["Only"], "one_line") == "Only."
    assert f(["a", "b", "c", "d", "e", "f", "g", "h"], "numbered").endswith("8. h")
    assert _raises(["1.", "-"], "numbered")
    r = m.SYEditStepsList().run("numbered", "a", "b", "a", skip_duplicates=True)
    assert r == ("1. a\n2. b", 2)
    assert m.SYEditStepsList().run("then_words", "a", "b", "c") == ("First, a. Then, b. Finally, c.", 3)
    assert m.SYEditStepsList().run("one_line", "a", "a", "", "", "", "", "", "b", True) == ("a; b.", 2)
    assert m.SYEditStepsList.RETURN_NAMES == ("steps", "count")
    return 24  # checks
