import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_scene_cut_finder as m


def run():
    n = 0
    assert m.pair_score([0, 0, 0, 0], [1, 1, 1, 1]) == 1.0; n += 1
    assert m.pair_score([0.5, 0.5], [0.5, 0.5]) == 0.0; n += 1
    assert abs(m.pair_score([0.0, 1.0], [0.5, 0.5]) - 0.5) < 1e-9; n += 1
    assert m.find_cuts([0.01, 0.9, 0.02, 0.8], 0.25) == [2, 4]; n += 1
    assert m.find_cuts([], 0.25) == []; n += 1
    assert m.find_cuts([0.9], 0.25) == []; n += 1          # frame 1 is only 1 after frame 0
    assert m.find_cuts([0.9], 0.25, 1) == [1]; n += 1
    assert m.find_cuts([0.0, 0.9, 0.9, 0.9], 0.25) == [2, 4]; n += 1   # min_gap blocks frame 3
    assert m.find_cuts([0.25, 0.25, 0.25], 0.25) == []; n += 1          # equal is not above
    assert m.find_cuts([1.0, 1.0, 1.0, 1.0], 0.01, 2) == [2, 4]; n += 1
    assert m.format_cuts([48, 121]) == "0,48,121"; n += 1
    assert m.format_cuts([]) == "0"; n += 1
    assert m.format_scores([0.5, 0.25]) == "0.5000,0.2500"; n += 1
    for call, text in ((lambda: m.find_cuts([0.5], 0), "sensitivity must be above 0"),
                       (lambda: m.find_cuts([0.5], 0.2, 0), "min_gap must be at least 1"),
                       (lambda: m.pair_score([1], [1, 2]), "different sizes"),
                       (lambda: m.pair_score([], []), "empty")):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert text in str(e)
        n += 1
    assert m.SYSceneCutFinder.RETURN_TYPES == ("STRING", "INT", "STRING"); n += 1
    return n
