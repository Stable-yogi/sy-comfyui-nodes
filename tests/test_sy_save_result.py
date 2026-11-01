import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_result as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.clean_part("My Show", "x") == "My Show"; n += 1
    assert m.clean_part("../../evil", "x") == "evil"; n += 1
    assert m.clean_part("a/b\\c", "x") == "a_b_c"; n += 1
    assert m.clean_part('bad:name?"', "x") == "badname"; n += 1
    assert m.clean_part("  ...  ", "fallback") == "fallback"; n += 1
    assert m.clean_part(None, "fb") == "fb"; n += 1
    assert m.build_prefix("Karate", "clip", True, "2026-11-01") == "Karate/2026-11-01/clip"; n += 1
    assert m.build_prefix("Karate", "clip", False, "2026-11-01") == "Karate/clip"; n += 1
    assert m.build_prefix("", "", True, "2026-11-01") == "SY/2026-11-01/result"; n += 1
    assert "/../" not in m.build_prefix("..", "..", False, "d") and not m.build_prefix("/abs", "x", False, "d").startswith("/"); n += 1
    assert m.pick_kind(True, False, True) == ["image", "audio"]; n += 1
    assert "nothing to save" in must_raise(m.pick_kind, False, False, False); n += 1
    assert m.sidecar_path(os.path.join("a", "b_00001_.png")) == os.path.join("a", "b_00001_.txt"); n += 1
    assert m.saved_text(["x.png", "y.png"]) == "Saved x.png\ny.png" and m.saved_text([]) == "Saved nothing"; n += 1
    spec = m.SYSaveResult.INPUT_TYPES()
    assert set(spec["optional"]) == {"image", "video", "audio", "settings"} and m.SYSaveResult.OUTPUT_NODE is True; n += 1
    return n
