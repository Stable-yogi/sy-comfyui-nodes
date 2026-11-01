import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_image_to_folder as m
import _sy_safe_paths as sp


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert sp.FORMATS == {"png": ".png", "jpg": ".jpg", "webp": ".webp"}; n += 1
    spec = m.SYSaveImageToFolder.INPUT_TYPES()
    assert spec["required"]["format"][0] == ["png", "jpg", "webp"]; n += 1
    assert m.SYSaveImageToFolder.OUTPUT_NODE is True; n += 1
    assert m.SYSaveImageToFolder.RETURN_TYPES[0] == "STRING"; n += 1
    assert raises(sp.write_image, None, "x", "gif", 90); n += 1
    assert sp.workflow_chunks(None, None) == {}; n += 1
    assert sp.workflow_chunks({"a": 1}, {"workflow": {"b": 2}}) == {"prompt": "{\"a\": 1}", "workflow": "{\"b\": 2}"}; n += 1
    opt = m.SYSaveImageToFolder.INPUT_TYPES()["optional"]
    assert opt["output_mode"][0] == ["save", "preview"] and "date_folder" in opt and "model_name" in opt and "input_name" in opt; n += 1
    assert m.saved_summary([{}, {}, {}, {}], 960, 1440) == "960x1440 saved 4 images"; n += 1
    assert m.saved_summary([{}], 8, 8) == "8x8 saved 1 image"; n += 1
    # --- value pass A2: sidecar text, batch check, info line
    from datetime import datetime
    now = datetime(2026, 11, 1, 9, 30, 5)
    assert m.sidecar_texts("off", "", 2, 1, "", "", 8, 8, "png", 95) is None; n += 1
    side = m.sidecar_texts("settings", "", 2, 77, "models/flux1.safetensors", " src  a.png ", 960, 1440, "jpg", 90, now)
    assert len(side) == 2 and side[0].split("\n")[:4] == ["saved: 2026-11-01 09:30:05", "seed: 77", "size: 960x1440", "format: jpg"]; n += 1
    assert "quality: 90" in side[0] and "input: src a.png" in side[0] and side[1].endswith("picture: 2 of 2"); n += 1
    assert "quality" not in m.sidecar_texts("settings", "", 1, 1, "", "", 8, 8, "png", 95, now)[0] and "model:" not in m.sidecar_texts("settings", "", 1, 1, "", "", 8, 8, "png", 95, now)[0]; n += 1
    assert m.sidecar_texts("custom text", "a cat", 3, 0, "", "", 8, 8, "png", 95) == ["a cat"] * 3; n += 1
    assert raises(m.sidecar_texts, "custom text", "  ", 1, 0, "", "", 8, 8, "png", 95); n += 1
    assert raises(m.sidecar_texts, "custom text", "x" * (m.MAX_SIDECAR_CHARS + 1), 1, 0, "", "", 8, 8, "png", 95); n += 1
    assert raises(m.sidecar_texts, "both", "x", 1, 0, "", "", 8, 8, "png", 95); n += 1
    assert raises(m.check_batch, (0, 8, 8, 3)) and raises(m.check_batch, (8, 8, 3)); n += 2
    assert m.check_batch((2, 8, 8, 3)) is None; n += 1
    ui = [{"filename": "a_00001.png", "subfolder": "SY/2026-11-01"}, {"filename": "a_00002.png", "subfolder": "SY/2026-11-01"}]
    t = m.save_info(ui, 64, 32, "png", 3, True, 0, False)
    assert t == "Saved 2 pictures (png, 64x32) to SY/2026-11-01: a_00001.png ... a_00002.png"; n += 1
    assert "Wrote 2 text files" in m.save_info(ui, 64, 32, "png", 3, True, 2, False); n += 1
    j = m.save_info(ui[:1], 64, 32, "jpg", 4, True, 0, False)
    assert "alpha channel was dropped" in j and "only embedded in png" in j and "Saved 1 picture " in j; n += 1
    assert m.save_info(ui, 64, 32, "png", 3, True, 0, True).startswith("Preview only: 2 pictures shown"); n += 1
    assert m.save_info([], 1, 1, "png", 3, True, 0, False) == "nothing was saved"; n += 1
    assert m.SYSaveImageToFolder.RETURN_NAMES == ("saved_paths", "info", "folder") and len(m.SYSaveImageToFolder.RETURN_TYPES) == 3; n += 1
    assert opt["sidecar"][0] == m.SIDECARS and opt["sidecar"][1]["default"] == "off" and "sidecar_text" in opt; n += 1
    return n
