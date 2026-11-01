import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_guides as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.plan_guides(False, False, False, False, "(none)", False, False) == []; n += 1
    assert m.plan_guides(True, True, True, False, "None", True, True) == [("start", 0), ("end", -1), ("voice", 0)]; n += 1
    assert m.plan_guides(False, False, False, True, "depth.safetensors", True, False) == [("layout", None)]; n += 1
    assert "vae" in must_raise(m.plan_guides, True, False, False, False, "(none)", False, True); n += 1
    assert "audio_vae" in must_raise(m.plan_guides, False, False, True, False, "(none)", True, False); n += 1
    assert "layout model" in must_raise(m.plan_guides, False, False, False, True, "None", True, True); n += 1
    assert "layout model" in must_raise(m.plan_guides, False, False, False, True, "", True, True); n += 1
    assert "vae" in must_raise(m.plan_guides, False, False, False, True, "x.safetensors", False, True); n += 1
    assert "No guides" in m.info_text([], "(none)", 1.0); n += 1
    t = m.info_text([("start", 0), ("layout", None)], "depth.safetensors", 0.8)
    assert "start picture" in t and "depth.safetensors, strength 0.8" in t; n += 1
    spec = m.SYH3Guides.INPUT_TYPES()
    assert set(spec["optional"]) == {"vae", "audio_vae", "start_image", "end_image", "voice", "layout_video"}; n += 1
    assert m.SYH3Guides.RETURN_NAMES == ("model", "positive", "info"); n += 1
    # core() must pass a keyword called name on to the core node (the layout model loader takes name=)
    import types
    import _sy_core_call as cc

    class Fake:
        FUNCTION = "go"

        def go(self, name=None, **kw):
            return (name,)
    saved = sys.modules.get("nodes")
    fake = types.ModuleType("nodes")
    fake.NODE_CLASS_MAPPINGS = {"Fake": Fake}
    sys.modules["nodes"] = fake
    try:
        assert cc.core("Fake", "test", name="depth.safetensors") == ("depth.safetensors",); n += 1
        assert "no core node" in must_raise(cc.core, "Missing", "test"); n += 1
    finally:
        if saved is None:
            del sys.modules["nodes"]
        else:
            sys.modules["nodes"] = saved
    return n
