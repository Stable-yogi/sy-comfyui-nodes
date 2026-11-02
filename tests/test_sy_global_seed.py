import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_global_seed as m


def run():
    n = 0
    top = m.MAX_SEED
    assert m.clamp_seed(-5) == 0 and m.clamp_seed("x") == 0 and m.clamp_seed(None) == 0 and m.clamp_seed(2 ** 70) == top; n += 1
    assert m.clamp_seed("42") == 42 and m.clamp_seed(7.9) == 7 and m.clamp_seed(float("inf")) == 0; n += 1
    assert m.next_seed(5, "fixed") == 5 and m.next_seed(5, "nonsense") == 5; n += 1
    assert m.next_seed(5, "increment") == 6 and m.next_seed(top, "increment") == 0; n += 1
    assert m.next_seed(5, "decrement") == 4 and m.next_seed(0, "decrement") == top; n += 1
    assert m.next_seed(1, "random", 0.0) == 0 and m.next_seed(1, "random", 0.5) == (top + 1) // 2; n += 1
    assert 0 <= m.next_seed(1, "random") <= top; n += 1
    assert m.next_seed(1, " Random ", 0.999999999) <= top; n += 1
    assert m.fit_seed(10, 20) == 10 and m.fit_seed(25, 20) == 4 and m.fit_seed(25, "bad") == 25 and m.fit_seed(25, -1) == 25; n += 1
    assert m.is_seed_name("seed") and m.is_seed_name(" Noise_Seed ") and not m.is_seed_name("steps") and not m.is_seed_name(None); n += 1
    assert m.parse_words(" Face, Hands ,,") == ["face", "hands"] and m.parse_words(None) == []; n += 1
    assert m.skip_by_title("Face Detailer", ["face"]) and not m.skip_by_title("Sampler", ["face"]) and not m.skip_by_title("x", []); n += 1
    cls = m.SYGlobalSeed
    assert cls().run(-3)[0] == 0 and cls().run(12, "random")[0] == 12; n += 1
    assert cls.DESCRIPTION and m.NODE_DISPLAY_NAME_MAPPINGS["SYGlobalSeed"] == "Global Seed SY"; n += 1
    return n
