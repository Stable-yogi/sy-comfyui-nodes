import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_dataset_scene_list as m


def run():
    n = 0
    char, keep = "the person from <image1>", m.DEFAULT_KEEP
    p, s, names = m.scene_prompts(char, 40, keep, "realistic photo", 1)
    assert len(p) == len(s) == len(names) == 40; n += 1
    assert len(set(p)) == 40; n += 1
    assert all(char in x and keep in x for x in p); n += 1
    assert all(x.endswith(keep) and ", realistic photo." in x for x in p); n += 1
    assert s == list(range(1, 41)); n += 1
    assert len(set(names)) == 40 and all(re.fullmatch(r"\d{3}_[a-z]+_[A-Za-z0-9_-]+", x) for x in names), names; n += 1
    assert names[0] == "001_closeup_kitchen", names[0]; n += 1
    assert sum(1 for x in p if "close-up" in x) >= 6; n += 1
    assert sum(1 for x in names if "_studio_" in x) >= 4; n += 1
    assert len({k for k, _, _ in m.TEMPLATES}) == 12; n += 1
    assert all("{character}" in t for _, _, t in m.TEMPLATES) and len(m.TEMPLATES) == 40; n += 1
    p5, s5, n5 = m.scene_prompts("Mia", 5, "", "", 100)
    assert len(p5) == 5 and s5 == [100, 101, 102, 103, 104]; n += 1
    assert p5[0].endswith(".") and "Mia" in p5[0] and ", ." not in p5[0] and "  " not in p5[0]; n += 1
    assert p5 == m.scene_prompts("Mia", 40, "", "", 100)[0][:5]; n += 1
    for bad in (("", 5, "k", "s", 1), ("  ", 5, "k", "s", 1), ("Mia", 0, "k", "s", 1), ("Mia", 41, "k", "s", 1), ("Mia", 5, "k", "s", -1)):
        try:
            m.scene_prompts(*bad)
            raise SystemExit("bad args must raise: %r" % (bad,))
        except ValueError:
            n += 1
    assert m.safe_name("a b/c..d") == "a_b_c_d" and m.safe_name("///") == "scene"; n += 1
    assert m.numbered_text(["a", "b"]) == "1. a\n2. b"; n += 1
    c = m.SYDatasetSceneList
    assert c.OUTPUT_IS_LIST == (True, True, True, False, True) and len(c.RETURN_TYPES) == len(c.RETURN_NAMES) == 5; n += 1
    out = c().run(char, 3, keep, "realistic photo", 7)
    assert len(out[0]) == 3 and out[1] == [7, 8, 9] and out[3].startswith("1. "); n += 1
    assert out[0] == m.scene_prompts(char, 3, keep, "realistic photo", 7)[0]; n += 1  # no outfits: same prompts as before
    assert all(x.endswith(keep) and "wearing" not in x for x in out[0]); n += 1
    fits = "a red summer dress\n\n  a black leather jacket  \r\na white shirt"
    assert m.outfit_list(fits) == ["a red summer dress", "a black leather jacket", "a white shirt"] and m.outfit_list(" \n") == []; n += 1
    p4 = m.scene_prompts(char, 4, keep, "realistic photo", 1, fits)[0]
    assert "wearing a red summer dress," in p4[0] and "wearing a black leather jacket," in p4[1]; n += 1
    assert "wearing a white shirt," in p4[2] and "wearing a red summer dress," in p4[3]; n += 1  # the list starts again
    assert all(x.endswith(m.OUTFIT_KEEP) and "clothes" not in x for x in p4); n += 1  # the default line must not fight the outfit
    assert m.scene_prompts(char, 2, "My own line.", "", 1, fits)[0][0].endswith("My own line."); n += 1  # his own line stays
    cap = m.scene_captions("sks_woman", 4, "realistic photo", fits)
    assert cap[0] == "close-up portrait of sks_woman, wearing a red summer dress, in a kitchen with soft morning light from the window, realistic photo", cap[0]; n += 1
    assert len(cap) == 4 and not any("<image" in x or x.endswith(".") or "Keep" in x for x in cap); n += 1
    assert m.scene_captions("", 1, "", "")[0] == "close-up portrait of the person in a kitchen with soft morning light from the window"; n += 1
    out = c().run(char, 3, keep, "realistic photo", 7, fits, "sks_woman")
    assert len(out[4]) == 3 and "sks_woman" in out[4][1] and "wearing" in out[0][1]; n += 1
    return n
