import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_face_parts_mask as m

ID2LABEL = {"0": "background", "1": "skin", "2": "nose", "3": "eye_g", "4": "l_eye", "5": "r_eye", "6": "l_brow",
            "7": "r_brow", "8": "l_ear", "9": "r_ear", "10": "mouth", "11": "u_lip", "12": "l_lip", "13": "hair",
            "14": "hat", "15": "ear_r", "16": "neck_l", "17": "neck", "18": "cloth"}


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    # ---- parts list
    assert len(m.PARTS) == 19 and len(set(m.PART_NAMES)) == 19; n += 1
    assert sorted(l for _, l, _ in m.PARTS) == sorted(ID2LABEL.values()); n += 1
    # ---- picked_labels
    assert m.picked_labels({"skin": True, "nose": False, "left_eye": True}) == ["skin", "l_eye"]; n += 1
    assert m.picked_labels({}) == []; n += 1
    assert m.picked_labels({k: True for k in m.PART_NAMES}) == [l for _, l, _ in m.PARTS]; n += 1
    assert "unknown face part" in refuses(m.picked_labels, {"eyes": True}); n += 1
    # ---- label_ids
    assert m.label_ids(ID2LABEL, ["skin", "l_eye", "r_eye"]) == [1, 4, 5]; n += 1
    assert m.label_ids(ID2LABEL, []) == []; n += 1
    assert m.label_ids({0: "background", 1: "skin"}, ["skin"]) == [1]; n += 1
    assert "has no part" in refuses(m.label_ids, {"0": "background"}, ["skin"]); n += 1
    # ---- preprocess_settings
    h, w, mean, std, norm = m.preprocess_settings({"size": {"height": 512, "width": 512}, "image_mean": [0.5, 0.5, 0.5],
                                                   "image_std": [0.25, 0.25, 0.25], "do_normalize": True})
    assert (h, w, mean, std, norm) == (512, 512, (0.5, 0.5, 0.5), (0.25, 0.25, 0.25), True); n += 1
    assert m.preprocess_settings({})[:2] == (512, 512) and m.preprocess_settings({})[2] == m.DEFAULT_MEAN; n += 1
    assert m.preprocess_settings({"size": 256})[:2] == (256, 256); n += 1
    assert m.preprocess_settings({"do_normalize": False})[4] is False; n += 1
    assert "outside" in refuses(m.preprocess_settings, {"size": 8}); n += 1
    assert "std above 0" in refuses(m.preprocess_settings, {"image_std": [0, 1, 1]}); n += 1
    assert "3 numbers" in refuses(m.preprocess_settings, {"image_mean": [0.5]}); n += 1
    # ---- palette
    p = m.palette(19)
    assert len(p) == 19 and p[0] == (0.0, 0.0, 0.0); n += 1
    assert all(0.0 <= c <= 1.0 for col in p for c in col); n += 1
    assert len(set(p)) == 19; n += 1
    # ---- missing_files
    with tempfile.TemporaryDirectory() as d:
        assert m.missing_files(d) == list(m.NEEDED); n += 1
        for f in m.NEEDED:
            open(os.path.join(d, f), "w").close()
        assert m.missing_files(d) == []; n += 1
    assert m.missing_files(None) == list(m.NEEDED); n += 1
    # ---- node shape
    it = m.SYFacePartsMask.INPUT_TYPES()["required"]
    assert list(it)[0] == "image" and list(it)[1:] == list(m.PART_NAMES); n += 1
    assert it["skin"][1]["default"] is True and it["hair"][1]["default"] is False; n += 1
    assert m.SYFacePartsMask.RETURN_TYPES == ("MASK", "IMAGE", "STRING"); n += 1
    assert "SYFacePartsMask" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYFacePartsMask"].endswith(" SY"); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
