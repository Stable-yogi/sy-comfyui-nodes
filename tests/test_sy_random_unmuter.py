import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_random_unmuter as m


def run():
    n = 0
    assert m.split_words(" Cat, dog ,,CAT,Bird") == ["cat", "dog", "bird"]; n += 1
    assert m.split_words("") == [] and m.split_words(None) == [] and m.split_words(" , ,") == []; n += 1
    titles = ["Load Cat LoRA", "Load DOG lora", "Sampler", "bird", None]
    assert m.match_titles(titles, "cat,dog") == [0, 1]; n += 1
    assert m.match_titles(titles, "BIRD") == [3]; n += 1
    assert m.match_titles(titles, "") == [] and m.match_titles(titles, " ,") == []; n += 1
    assert m.match_titles(titles, "zzz") == [] and m.match_titles([], "cat") == []; n += 1
    # fixed vectors: the JavaScript copy must give the same numbers
    assert [m.mix32(s, c) for s, c in ((1, 0), (1, 1), (12345, 7), (2147483647, 99))] == [2980047484, 232174035, 1765200083, 594735504]; n += 1
    assert [m.pick_index(5, "random", s, c) for s, c in ((1, 0), (1, 1), (12345, 7), (2147483647, 99))] == [4, 0, 3, 4]; n += 1
    assert m.pick_index(0, "random", 0, 0) == -1 and m.pick_index(-3, "round_robin", 0, 0) == -1; n += 1
    assert [m.pick_index(3, "round_robin", 0, c) for c in range(7)] == [0, 1, 2, 0, 1, 2, 0]; n += 1
    assert m.pick_index(4, "random", 0, 0, 0.0) == 0 and m.pick_index(4, "random", 0, 0, 0.5) == 2; n += 1
    assert m.pick_index(4, "random", 0, 0, 0.9999) == 3 and m.pick_index(4, "random", 0, 0, 1.0) == 3; n += 1
    assert m.pick_index(1, "random", 77, 5) == 0 and m.pick_index(1, "round_robin", 0, 5) == 0; n += 1
    seen = {m.pick_index(6, "random", 9, c) for c in range(200)}
    assert seen == set(range(6)); n += 1  # a seeded sequence still reaches every candidate
    assert all(m.pick_index(6, "random", 9, c) == m.pick_index(6, "random", 9, c) for c in range(20)); n += 1
    assert m.plan_modes(3, 1, "Mute") == [2, 0, 2]; n += 1
    assert m.plan_modes(3, 0, "Bypass") == [0, 4, 4] and m.plan_modes(2, -1, "bypass") == [4, 4]; n += 1
    assert m.plan_modes(0, -1, "Mute") == []; n += 1
    cls = m.SYRandomUnmuter
    req = cls.INPUT_TYPES()["required"]
    assert list(req) == ["title_filter", "pick", "seed", "off_mode", "enabled"]; n += 1
    assert all("tooltip" in v[1] for v in req.values()) and cls().run() == (); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYRandomUnmuter"] == "RandomUnmuter SY" and cls.DESCRIPTION; n += 1
    return n
