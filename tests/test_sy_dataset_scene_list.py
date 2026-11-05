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
    assert c.OUTPUT_IS_LIST == (True, True, True, False) and len(c.RETURN_TYPES) == len(c.RETURN_NAMES) == 4; n += 1
    out = c().run(char, 3, keep, "realistic photo", 7)
    assert len(out[0]) == 3 and out[1] == [7, 8, 9] and out[3].startswith("1. "); n += 1
    return n
