import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_from_words as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    ALL, BIG, EACH = m.WHICH
    # ---- clean_words
    assert m.clean_words("  the   red\tdress \n") == "the red dress"; n += 1
    assert m.clean_words("person") == "person"; n += 1
    assert m.clean_words("") == "" and m.clean_words("   ") == "" and m.clean_words(None) == ""; n += 1
    assert len(m.clean_words("a" * 500)) == 200; n += 1
    assert m.clean_words("a " * 300) == ("a " * 100).strip(); n += 1
    assert m.clean_words("x" * 199 + " y") == "x" * 199; n += 1
    # ---- sam_prompt
    assert m.sam_prompt("person") == "person:30"; n += 1
    assert m.sam_prompt("the red dress", 5) == "the red dress:5"; n += 1
    assert m.sam_prompt("cat, dog ,, bird") == "cat:30, dog:30, bird:30"; n += 1
    assert m.sam_prompt("(cat): 9") == "cat 9:30"; n += 1
    assert "Type what to select" in refuses(m.sam_prompt, ""); n += 1
    assert "Type what to select" in refuses(m.sam_prompt, " , ( ) : "); n += 1
    assert refuses(m.sam_prompt, "cat", 0) is not None; n += 1
    # ---- pick_mask_index
    assert m.pick_mask_index([], ALL) == [] and m.pick_mask_index([], BIG) == [] and m.pick_mask_index([], EACH) == []; n += 1
    assert m.pick_mask_index([5, 9, 2], ALL) == [0, 1, 2]; n += 1
    assert m.pick_mask_index([5, 9, 2], BIG) == [1]; n += 1
    assert m.pick_mask_index([5, 9, 2], EACH) == [0, 1, 2]; n += 1
    assert m.pick_mask_index([7, 7], BIG) == [0]; n += 1
    assert m.pick_mask_index([4], BIG) == [0]; n += 1
    assert "which must be" in refuses(m.pick_mask_index, [1], "nope"); n += 1
    assert [m.combine_style(w) for w in m.WHICH] == ["union", "single", "each"]; n += 1
    # ---- numbers
    assert m.threshold_ok(0) == 0.0 and m.threshold_ok(1) == 1.0 and m.threshold_ok(0.5) == 0.5; n += 1
    assert "threshold" in refuses(m.threshold_ok, 1.1) and "threshold" in refuses(m.threshold_ok, -0.1); n += 1
    assert "threshold" in refuses(m.threshold_ok, "0.5") and "threshold" in refuses(m.threshold_ok, True); n += 1
    assert m.pixels_ok(-64, "grow", -64) == -64 and m.pixels_ok(64, "grow", -64) == 64 and m.pixels_ok(0, "feather", 0) == 0; n += 1
    assert "grow" in refuses(m.pixels_ok, 65, "grow", -64) and "grow" in refuses(m.pixels_ok, -65, "grow", -64); n += 1
    assert "feather" in refuses(m.pixels_ok, -1, "feather", 0) and "whole number" in refuses(m.pixels_ok, 1.5, "feather", 0); n += 1
    # ---- texts
    assert m.no_match_text("red dress") == "Nothing matched 'red dress'. Try other words or lower the threshold."; n += 1
    assert m.info_text("cat", 0, ALL, 1, 1) == m.no_match_text("cat"); n += 1
    t = m.info_text("cat", 3, ALL, 1, 1)
    assert "3 things" in t and "'cat'" in t and "joined into one mask" in t and "1 picture:" in t; n += 1
    t = m.info_text("cat", 1, BIG, 2, 2)
    assert "1 thing " in t and "biggest" in t and "2 pictures" in t; n += 1
    t = m.info_text("cat", 4, EACH, 4, 1)
    assert "one mask each" in t and "4 masks" in t; n += 1
    # ---- names and list
    assert m.model_choices([]) == [m.NO_MODEL] and m.model_choices(["b.pt", "a.pt"]) == ["a.pt", "b.pt"]; n += 1
    for bad in ("", None, "../x.pt", "/x", "C:/x.pt"):
        assert refuses(m.check_plain_name, bad) is not None, bad
    n += 1
    msg = refuses(m.resolve_model_path, m.NO_MODEL)
    assert msg and "models/sam3" in msg; n += 1
    assert refuses(m.resolve_model_path, "../x.pt") is not None; n += 1
    # ---- node shape
    c = m.SYMaskFromWords
    assert c.RETURN_TYPES == ("MASK", "IMAGE", "INT", "STRING") and c.RETURN_NAMES == ("mask", "cutout", "found", "info"); n += 1
    assert m.NODE_CLASS_MAPPINGS["SYMaskFromWords"] is c and m.NODE_DISPLAY_NAME_MAPPINGS["SYMaskFromWords"] == "Mask From Words SY"; n += 1
    assert c.CATEGORY == "SY/Image" and c.DESCRIPTION; n += 1
    spec = c.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "words", "model", "threshold", "which", "grow", "feather"]; n += 1
    assert spec["required"]["words"][1]["default"] == "person" and spec["required"]["threshold"][1]["default"] == 0.5; n += 1
    assert spec["required"]["which"][0] == list(m.WHICH) and spec["required"]["which"][1]["default"] == ALL; n += 1
    for k, d in spec["required"].items():
        assert 0 < len(d[1]["tooltip"]) <= 120, k
    n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = c()
        H, W = 12, 16

        def blob(y0, y1, x0, x1):
            t = torch.zeros(H, W)
            t[y0:y1, x0:x1] = 1.0
            return t

        small = blob(1, 3, 1, 3)       # 4 px
        big = blob(5, 10, 8, 14)       # 30 px
        empty = torch.zeros(H, W)
        calls = []

        def fake_detect(bundle, cond, frame, threshold):
            calls.append((cond, threshold, tuple(frame.shape)))
            key = int(round(float(frame[0, 0, 0, 0]) * 10))   # first pixel value picks the scenario
            return {0: [small, big], 1: [], 2: [big], 3: [empty, small]}[key]

        saved = (m._get_bundle, m._encode_words, m._detect, m._release, m.resolve_model_path)
        released = []
        encoded = []
        m._get_bundle = lambda path: ("model", "clip")
        m._encode_words = lambda bundle, prompt: (encoded.append(prompt), "COND")[1]
        m._detect = fake_detect
        m._release = lambda b: released.append(b)
        m.resolve_model_path = lambda name: "fake.pt"

        def pic(code, count=1):
            t = torch.rand(count, H, W, 3) * 0.05 + 0.01
            t[:, 0, 0, :] = code / 10.0
            return t

        try:
            # all together: union of both, found 2
            img = pic(0)
            mask, cut, found, info = node.run(img, "person", "x", 0.5, ALL, 0, 0)
            assert mask.shape == (1, H, W) and cut.shape == (1, H, W, 4) and found == 2; n += 1
            assert torch.equal(mask[0], torch.clamp(small + big, 0, 1)) and float(mask.sum()) == 34; n += 1
            assert torch.equal(cut[..., 3], mask) and torch.equal(cut[..., :3], img); n += 1
            assert "2 things" in info and "'person'" in info; n += 1
            assert encoded[-1] == "person:30" and calls[-1][0] == "COND" and calls[-1][1] == 0.5 and calls[-1][2] == (1, H, W, 3); n += 1
            assert released and released[-1] == ("model", "clip"); n += 1
            # words are cleaned; commas become several phrases
            node.run(img, "  red   dress , hat ", "x", 0.5, ALL, 0, 0)
            assert encoded[-1] == "red dress:30, hat:30"; n += 1
            # threshold reaches the detector
            node.run(img, "person", "x", 0.2, ALL, 0, 0)
            assert calls[-1][1] == 0.2; n += 1
            # biggest only
            mask, cut, found, info = node.run(img, "person", "x", 0.5, BIG, 0, 0)
            assert torch.equal(mask[0], big) and found == 2 and "biggest" in info; n += 1
            assert float(cut[0, 6, 9, 3]) == 1.0 and float(cut[0, 1, 1, 3]) == 0.0; n += 1
            # one at a time: a mask per find, cutouts line up
            mask, cut, found, info = node.run(img, "person", "x", 0.5, EACH, 0, 0)
            assert mask.shape == (2, H, W) and cut.shape == (2, H, W, 4) and found == 2; n += 1
            assert torch.equal(mask[0], small) and torch.equal(mask[1], big) and "one mask each" in info; n += 1
            assert torch.equal(cut[1, ..., :3], img[0]) and torch.equal(cut[1, ..., 3], big); n += 1
            # nothing matched: empty mask, found 0, plain note, no error
            none = pic(1)
            for w in (ALL, BIG, EACH):
                mask, cut, found, info = node.run(none, "unicorn", "x", 0.5, w, 0, 0)
                assert mask.shape == (1, H, W) and float(mask.sum()) == 0.0 and found == 0; n += 1
                assert info == "Nothing matched 'unicorn'. Try other words or lower the threshold." and cut.shape == (1, H, W, 4); n += 1
                assert float(cut[..., 3].sum()) == 0.0; n += 1
            # an all-zero find counts as nothing
            mask, cut, found, info = node.run(pic(3), "x", "x", 0.5, ALL, 0, 0)
            assert found == 1 and torch.equal(mask[0], small); n += 1
            # batch: picture 0 has two, 1 none, 2 one
            batch = torch.cat([pic(0), pic(1), pic(2)])
            mask, cut, found, info = node.run(batch, "person", "x", 0.5, ALL, 0, 0)
            assert mask.shape == (3, H, W) and found == 3 and float(mask[1].sum()) == 0.0 and float(mask[2].sum()) == 30; n += 1
            assert "3 pictures" in info; n += 1
            mask, cut, found, info = node.run(batch, "person", "x", 0.5, BIG, 0, 0)
            assert mask.shape == (3, H, W) and float(mask[0].sum()) == 30; n += 1
            mask, cut, found, info = node.run(batch, "person", "x", 0.5, EACH, 0, 0)
            assert mask.shape == (3, H, W) and found == 3; n += 1                     # 2 + 0 + 1 finds = 3 masks
            assert torch.equal(cut[0, ..., :3], batch[0]) and torch.equal(cut[1, ..., :3], batch[0]) and torch.equal(cut[2, ..., :3], batch[2]); n += 1
            mask, cut, found, info = node.run(torch.cat([pic(1), pic(1)]), "z", "x", 0.5, EACH, 0, 0)
            assert mask.shape == (2, H, W) and found == 0 and float(mask.sum()) == 0.0; n += 1
            # grow / shrink / feather on the result
            mask, _, _, _ = node.run(pic(2), "p", "x", 0.5, ALL, 1, 0)
            assert float(mask[0].sum()) == 7 * 8 and float(mask[0, 4, 7]) == 1.0; n += 1
            mask, _, _, _ = node.run(pic(2), "p", "x", 0.5, ALL, -1, 0)
            assert float(mask[0].sum()) == 3 * 4; n += 1
            mask, cut, _, _ = node.run(pic(2), "p", "x", 0.5, ALL, 0, 2)
            assert 0.0 < float(mask[0, 4, 10]) < 1.0 and float(mask.max()) <= 1.0 and torch.equal(cut[..., 3], mask); n += 1
            # RGBA input is accepted; cutout keeps its colour channels
            rgba = torch.cat([pic(2), torch.ones(1, H, W, 1)], dim=-1)
            mask, cut, found, _ = node.run(rgba, "p", "x", 0.5, ALL, 0, 0)
            assert cut.shape == (1, H, W, 4) and torch.equal(cut[..., :3], rgba[..., :3]) and found == 1; n += 1
            # refusals
            assert "'words' is empty" in refuses(node.run, img, "   ", "x", 0.5, ALL, 0, 0); n += 1
            assert "threshold" in refuses(node.run, img, "p", "x", 3.0, ALL, 0, 0); n += 1
            assert "which must" in refuses(node.run, img, "p", "x", 0.5, "some", 0, 0); n += 1
            assert "grow" in refuses(node.run, img, "p", "x", 0.5, ALL, 200, 0); n += 1
            assert "feather" in refuses(node.run, img, "p", "x", 0.5, ALL, 0, -3); n += 1
            assert "picture batch" in refuses(node.run, torch.zeros(4, 4), "p", "x", 0.5, ALL, 0, 0); n += 1
            assert "Type what to select" in refuses(node.run, img, " , ", "x", 0.5, ALL, 0, 0); n += 1
        finally:
            m._get_bundle, m._encode_words, m._detect, m._release, m.resolve_model_path = saved
        msg = refuses(node.run, torch.zeros(1, 4, 4, 3), "person", m.NO_MODEL)
        assert msg and "models/sam3" in msg; n += 1
        assert "'words' is empty" in refuses(node.run, torch.zeros(1, 4, 4, 3), "", m.NO_MODEL); n += 1
        assert refuses(node.run, torch.zeros(1, 4, 4, 3), "person", "nothing-here.pt") is not None; n += 1
    return n
