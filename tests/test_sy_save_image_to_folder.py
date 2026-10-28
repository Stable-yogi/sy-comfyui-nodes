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
    assert m.SYSaveImageToFolder.RETURN_TYPES == ("STRING",); n += 1
    assert raises(sp.write_image, None, "x", "gif", 90); n += 1
    assert sp.workflow_chunks(None, None) == {}; n += 1
    assert sp.workflow_chunks({"a": 1}, {"workflow": {"b": 2}}) == {"prompt": "{\"a\": 1}", "workflow": "{\"b\": 2}"}; n += 1
    opt = m.SYSaveImageToFolder.INPUT_TYPES()["optional"]
    assert opt["output_mode"][0] == ["save", "preview"] and "date_folder" in opt and "model_name" in opt and "input_name" in opt; n += 1
    assert m.saved_summary([{}, {}, {}, {}], 960, 1440) == "960x1440 saved 4 images"; n += 1
    assert m.saved_summary([{}], 8, 8) == "8x8 saved 1 image"; n += 1
    return n
