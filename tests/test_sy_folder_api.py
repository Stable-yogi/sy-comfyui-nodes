import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_folder_api as api
import _sy_safe_paths as sp


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    tmp = tempfile.mkdtemp(prefix="sy_api_")
    out_dir, in_dir = os.path.join(tmp, "output"), os.path.join(tmp, "input")
    os.makedirs(os.path.join(out_dir, "SY", "2026-10-28"))
    os.makedirs(in_dir)
    open(os.path.join(out_dir, "SY", "a_00001.png"), "wb").close()
    open(os.path.join(out_dir, "SY", "note.txt"), "wb").close()
    real_root = api.root_folder
    api.root_folder = lambda r: {"output": out_dir, "input": in_dir}[r]   # no ComfyUI here: fake the two folders
    opened = []
    real_start = getattr(os, "startfile", None)
    os.startfile = lambda p: opened.append(p)                              # never open a real window in a test
    try:
        info = api.list_folder("output", "SY")
        assert info["dirs"] == ["2026-10-28"] and info["images"] == 1 and info["sub"] == "SY"; n += 1
        assert api.list_folder("output", "nope")["exists"] is False; n += 1
        assert raises(api.list_folder, "temp", ""); n += 1
        assert raises(api.list_folder, "output", ".."); n += 1
        assert raises(api.list_folder, "output", "C:/Windows"); n += 1
        now = datetime(2026, 10, 28, 9, 5, 7)
        plan = api.plan_save("SY", "k_{width}x{height}_{counter}", "png", 1, 960, 1440, 1, "", "", False, now)
        assert plan["filename"] == "k_960x1440_00001.png" and plan["sub"] == "SY"; n += 1
        plan = api.plan_save("SY", "{date}_{model}_{counter}", "jpg", 1, 0, 0, 1, "C:/m/Muse V3.safetensors", "", True, now)
        assert plan["filename"] == "2026-10-28_Muse V3_00001.jpg" and plan["sub"] == "SY/2026-10-28"; n += 1
        assert raises(api.plan_save, "SY", "x_{counter}", "gif"); n += 1
        assert raises(api.plan_save, "../x", "x_{counter}", "png"); n += 1
        assert api.open_target("output", "SY") == os.path.realpath(os.path.join(out_dir, "SY")) and len(opened) == 1; n += 1
        assert api.open_target("output", "SY", "a_00001.png").endswith("a_00001.png") and len(opened) == 2; n += 1
        assert raises(api.open_target, "output", "SY", "note.txt"); n += 1                # not a picture
        assert raises(api.open_target, "output", "SY", "..\a.png"); n += 1                # no folder part in a file name
        assert raises(api.open_target, "output", "..", None); n += 1                       # leaves the output folder
        assert raises(api.open_target, "output", "missing", None); n += 1
        assert raises(api.open_target, "output", "SY", "b.png"); n += 1                    # not there
        assert len(opened) == 2; n += 1                                                    # every refusal opened nothing
    finally:
        api.root_folder = real_root
        if real_start is None:
            del os.startfile
        else:
            os.startfile = real_start
    assert api.register_routes() is False; n += 1                                          # outside ComfyUI it does nothing
    # new tokens in the shared helpers
    assert sp.clean_token("D:/m/a<b>.safetensors") == "a_b_"; n += 1
    assert sp.expand_pattern("{width}x{height}-{batch}", extra={"width": 8, "height": 4, "batch": 2}) == "8x4-2"; n += 1
    assert raises(sp.expand_pattern, "{width}"); n += 1                                    # extra tokens are off by default
    assert sp.date_subfolder("", datetime(2026, 1, 2)) == "2026-01-02"; n += 1
    return n
