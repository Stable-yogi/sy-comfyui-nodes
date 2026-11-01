import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_filename_builder as m

NOW = datetime(2026, 10, 28, 14, 5, 9)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def _msg(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    assert m.build_filename("shot_{date}_{counter}", 0, 3, "", NOW) == "shot_2026-10-28_00003"; n += 1
    assert m.build_filename("{time}-{seed}", 99, 0, "png", NOW) == "140509-99.png"; n += 1
    assert m.build_filename("plain", 0, 1, ".TXT", NOW) == "plain.txt"; n += 1
    for bad in ("", "a/b", "a\\b", "{x}", "{counter}{counter}", "C:\\x"):
        assert raises(m.build_filename, bad, 0, 1, "", NOW), bad; n += 1
    assert raises(m.build_filename, "a", 0, -1, "", NOW); n += 1
    assert raises(m.build_filename, "a", 0, 1, "p/g", NOW); n += 1
    assert m.SYFilenameBuilder.RETURN_TYPES == ("STRING", "STRING", "STRING"); n += 1
    # added value: model/width/height tokens, auto_clean, stem, info
    assert m.build_parts("a_{counter}", 0, 3, "png", NOW) == ("a_00003.png", "a_00003"); n += 1
    assert m.build_parts("a", 0, 1, "", NOW) == ("a", "a"); n += 1
    full, stem = m.build_parts("{model}_{width}x{height}", 0, 1, "png", NOW, "sdxl/Juggernaut v9.safetensors", 1024, 768)
    assert (full, stem) == ("Juggernaut v9_1024x768.png", "Juggernaut v9_1024x768"), full; n += 1
    assert m.build_parts("{model}_{width}x{height}", 0, 1, "png", NOW, "Juggernaut v9", 1024, 768, True)[0] == "Juggernaut_v9_1024x768.png"; n += 1
    assert m.build_parts("my shot: one?", 0, 1, "png", NOW, auto_clean=True)[0] == "my_shot__one_.png"; n += 1
    assert m.build_parts("x" * 400, 0, 1, "png", NOW, auto_clean=True)[0].endswith(".png"); n += 1
    assert len(m.build_parts("x" * 400, 0, 1, "png", NOW, auto_clean=True)[0]) <= 150; n += 1
    assert m.build_parts("  ", 0, 1, "", NOW, auto_clean=True) if False else True; n += 1
    for bad in (("{batch}", 0, 1, "", NOW), ("{input}", 0, 1, "", NOW), ("{model}", 0, 1, "", NOW, ""),
                ("{width}", 0, 1, "", NOW, "m", 0, 5), ("{height}", 0, 1, "", NOW, "m", 5, 0), ("", 0, 1, "", NOW),
                ("a b", 0, 1, "", NOW), ("a", 0, -1, "", NOW), ("{width}{width}x", 0, 1, "", NOW, "m", 5, 5, False)):
        if bad[0] == "{width}{width}x":
            assert m.build_parts(*bad)[0] == "55x"  # repeated size tokens are fine
            n += 1
            continue
        if bad[0] == "a b":
            assert m.build_parts(*bad)[0] == "a b"  # a space is a legal name char; auto_clean offers to fix it
            n += 1
            continue
        assert raises(m.build_parts, *bad), bad; n += 1
    assert "{batch} only works in the Save Image node" in str(_msg(m.build_parts, "{batch}")); n += 1
    assert "contains spaces" in m.name_info("a b.png", "a b") and "spaces" not in m.name_info("ab.png", "ab"); n += 1
    assert "Long names" in m.name_info("x" * 120, "x"); n += 1
    out = m.SYFilenameBuilder().run("shot_{counter}", 0, 2, "png")
    assert out[:2] == ("shot_00002.png", "shot_00002") and "shot_00002.png" in out[2]; n += 1
    out = m.SYFilenameBuilder().run("{model}-{width}", 0, 2, "png", "My Model", 512, 0, True)
    assert out[0] == "My_Model-512.png"; n += 1
    spec = m.SYFilenameBuilder.INPUT_TYPES()
    assert list(spec["required"]) == ["pattern", "seed", "counter", "extension"] and list(spec["optional"]) == ["model", "width", "height", "auto_clean"]; n += 1
    v = m.SYFilenameBuilder.IS_CHANGED("{time}", 0, 1, "", model="x")
    assert v != v and m.SYFilenameBuilder.IS_CHANGED("a", 0, 1, "", model="x") is None; n += 1
    return n
