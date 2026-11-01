import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_pack as m

NOW = datetime(2026, 11, 1, 9, 5, 7)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    # token filling
    vals = m.token_values("my pic", 42, 20, 7.5, 512, 768, "png", 2, NOW)
    assert vals["date"] == "2026-11-01" and vals["time"] == "090507" and vals["cfg"] == "7.5" and vals["batch"] == "02"; n += 1
    t = m.stem_template("{date}_{name}_{seed}_{steps}_{cfg}_{width}x{height}_{format}_{batch}_{counter}", vals)
    assert t == "2026-11-01_my pic_42_20_7.5_512x768_png_02_" + m._MARK; n += 1
    assert m.token_values("x", -1, 0, 0, 1, 1, "png", 1, NOW)["seed"] == "noseed"; n += 1
    assert m.cfg_text(7.0) == "7" and m.cfg_text(0) == "0" and m.cfg_text(3.25) == "3.25"; n += 1
    # unknown token and bad patterns give a plain error that lists the valid tokens
    e = raises(m.check_pattern, "{date}_{nope}")
    assert e and "{nope}" in e and "{counter}" in e and "{date}" in e; n += 1
    assert raises(m.check_pattern, "a{date"); n += 1
    assert raises(m.check_pattern, "{counter}{counter}"); n += 1
    assert raises(m.check_pattern, "{counter}", allow_counter=False); n += 1
    assert raises(m.stem_template, "  ", vals); n += 1
    # name cleaning
    assert m.clean_text('a/b:c*d?"e') == "a_b_c_d__e"; n += 1
    assert m.clean_text("   ...  ") == "image" and m.clean_text("", fallback="x") == "x"; n += 1
    assert m.clean_text("nul") == "_nul"; n += 1
    assert len(m.clean_text("a" * 500)) == m.MAX_PART; n += 1
    st = m.stem_template("{name}_{counter}", m.token_values("b" * 400, 0, 0, 0, 1, 1, "png", 1, NOW))
    assert len(st.replace(m._MARK, "x" * 5)) <= m.MAX_STEM; n += 1
    assert len(m.stem_template("z" * 500, vals)) < m.MAX_STEM; n += 1
    # bad characters typed straight into the pattern are replaced
    assert "/" not in m.stem_template("a/b\\c", vals) and ":" not in m.stem_template("a:b", vals); n += 1
    # subfolder
    assert m.fill_subfolder("{date}/{name}", vals) == "2026-11-01/my pic"; n += 1
    assert m.fill_subfolder("", vals) == "" and m.fill_subfolder("  / ./ ", vals) == ""; n += 1
    assert raises(m.fill_subfolder, "../x", vals); n += 1
    assert raises(m.fill_subfolder, "C:/x", vals); n += 1
    assert raises(m.fill_subfolder, "{counter}", vals); n += 1
    assert raises(m.fill_subfolder, "{bad}", vals); n += 1
    assert m.fill_subfolder("a:b", vals) == "a_b"; n += 1
    # next free counter
    tmpl = "pic_" + m._MARK
    assert m.pick_name(tmpl, ".png", set(), "next number") == ("pic_00001", False); n += 1
    taken = {"pic_00001.png", "pic_00007.png", "other_00099.png"}
    assert m.pick_name(tmpl, ".png", taken, "next number") == ("pic_00008", False); n += 1
    assert m.pick_name(tmpl, ".png", {"pic_00001.txt"}, "next number")[0] == "pic_00002"; n += 1
    assert m.pick_name(tmpl, ".png", {"pic_00003.png"}, "skip")[0] == "pic_00004"; n += 1
    # plain name (no counter) when taken
    assert m.pick_name("plain", ".png", set(), "next number") == ("plain", False); n += 1
    assert m.pick_name("plain", ".png", {"plain.png"}, "next number") == ("plain_00001", False); n += 1
    assert m.pick_name("plain", ".png", {"plain.png", "plain_00001.png"}, "next number") == ("plain_00002", False); n += 1
    assert m.pick_name("plain", ".png", {"plain.txt"}, "next number")[0] == "plain_00001"; n += 1
    assert m.pick_name("plain", ".png", {"plain.png"}, "skip") == (None, True); n += 1
    assert raises(m.pick_name, "plain", ".png", set(), "overwrite"); n += 1
    # plan for a batch: no clashes, numbers go up
    plan = m.plan_saves(["x_00002.png"], "x_{counter}", ".png", 3, "n", 0, 0, 0, 8, 8, "png", "next number", NOW)
    assert [p[0] for p in plan] == ["x_00003", "x_00004", "x_00005"]; n += 1
    plan = m.plan_saves([], "same", ".png", 3, "n", 0, 0, 0, 8, 8, "png", "next number", NOW)
    assert [p[0] for p in plan] == ["same", "same_00001", "same_00002"]; n += 1
    plan = m.plan_saves([], "p_{batch}", ".png", 2, "n", 0, 0, 0, 8, 8, "png", "skip", NOW)
    assert [p[0] for p in plan] == ["p_01", "p_02"]; n += 1
    plan = m.plan_saves(["same.png"], "same", ".png", 2, "n", 0, 0, 0, 8, 8, "png", "skip", NOW)
    assert plan[0] == (None, True) and plan[1] == (None, True); n += 1
    # settings text
    t = m.settings_text("nm", 5, 20, 7.5, 64, 32, "jpeg", 80, 1, 2, "a prompt", NOW)
    for need in ("seed: 5", "steps: 20", "cfg: 7.5", "size: 64x32", "quality 80", "picture: 1 of 2", "2026-11-01 09:05:07", "a prompt"):
        assert need in t, need
        n += 1
    t = m.settings_text("nm", -1, 0, 0, 8, 8, "png", 95, 1, 1, "", NOW)
    assert "seed" not in t and "steps" not in t and "cfg" not in t and "quality" not in t; n += 1
    # setting checks
    ok = ("png", 95, 0, 0, 0.0, "next number", 1, "")
    m.check_settings(*ok); n += 1
    for idx, bad in ((0, "gif"), (1, 0), (1, 101), (2, -2), (3, 1001), (4, 101.0), (5, "x"), (6, 0)):
        args = list(ok)
        args[idx] = bad
        assert raises(m.check_settings, *args), idx
        n += 1
    # info
    t = m.save_info(["a.png", "b.png"], 1, 8, 8, "jpeg", "SY", 4, 2)
    assert "Saved 2 pictures" in t and "Skipped 1 picture " in t and "alpha" in t and "2 settings text files" in t; n += 1
    assert "Nothing was saved" in m.save_info([], 2, 8, 8, "png", "", 3, 0); n += 1
    # node basics
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSavePack"] == "Save Pack SY" and m.SYSavePack.OUTPUT_NODE; n += 1
    assert m.SYSavePack.RETURN_NAMES == ("paths", "info"); n += 1
    # real saving with a temp folder (needs torch + PIL)
    try:
        import torch
        import PIL  # noqa: F401
    except ImportError:
        torch = None
    if torch is not None:
        import types
        out_dir = tempfile.mkdtemp(prefix="sy_savepack_")
        stub = types.ModuleType("folder_paths")
        stub.get_output_directory = lambda: out_dir
        stub.get_temp_directory = lambda: out_dir
        stub.get_input_directory = lambda: out_dir
        sys.modules["folder_paths"] = stub
        node = m.SYSavePack()
        img = torch.rand(2, 16, 24, 3)
        r = node.run(img, name="my pic", subfolder="{date}/sub", seed=7, steps=9, cfg=6.5, settings_text="hello prompt")
        paths, info = r["result"]
        plist = paths.split("\n")
        assert len(plist) == 2 and all(os.path.isfile(p) for p in plist); n += 1
        assert r["ui"]["images"][0]["subfolder"].endswith("/sub") and r["ui"]["images"][0]["type"] == "output"; n += 1
        assert os.path.basename(plist[0]) == "%s_my pic_00001.png" % datetime.now().strftime("%Y-%m-%d"); n += 1
        txt = open(os.path.splitext(plist[0])[0] + ".txt", encoding="utf-8").read()
        assert "seed: 7" in txt and "hello prompt" in txt and "size: 24x16" in txt; n += 1
        from PIL import Image
        im = Image.open(plist[0])
        assert im.size == (24, 16) and "hello prompt" in im.text.get("sy_settings", ""); n += 1
        # second run never overwrites
        before = {p: os.path.getsize(p) for p in plist}
        r2 = node.run(img, name="my pic", subfolder="{date}/sub", seed=7, steps=9, cfg=6.5)
        p2 = r2["result"][0].split("\n")
        assert not set(p2) & set(plist) and all(os.path.getsize(p) == s for p, s in before.items()); n += 1
        # no settings file
        r3 = node.run(img[:1], name="q", write_settings_file=False, format="webp", quality=50)
        p3 = r3["result"][0]
        assert p3.endswith(".webp") and not os.path.exists(os.path.splitext(p3)[0] + ".txt") and "Wrote" not in r3["result"][1]; n += 1
        r4 = node.run(torch.rand(1, 8, 8, 4), name="j", format="jpeg")
        assert r4["result"][0].endswith(".jpg") and "alpha" in r4["result"][1]; n += 1
        # skip when the plain name is taken
        node.run(img[:1], filename_pattern="fixed", subfolder="fx")
        r5 = node.run(img[:1], filename_pattern="fixed", subfolder="fx", on_exists="skip")
        assert r5["result"][0] == "" and "Nothing was saved" in r5["result"][1] and r5["ui"]["images"] == []; n += 1
        r6 = node.run(img[:1], filename_pattern="fixed", subfolder="fx")
        assert os.path.basename(r6["result"][0]) == "fixed_00001.png"; n += 1
        # refusals
        assert raises(node.run, img, filename_pattern="{wrong}"); n += 1
        assert raises(node.run, img, subfolder="../out"); n += 1
        assert raises(node.run, img, subfolder="C:/evil"); n += 1
        assert raises(node.run, img, quality=0); n += 1
        assert raises(node.run, torch.rand(0, 8, 8, 3)); n += 1
        assert raises(node.run, torch.rand(8, 8, 3)); n += 1
        # hidden prompt data goes into the png
        r7 = node.run(img[:1], name="w", prompt={"1": {"class_type": "X"}}, extra_pnginfo={"workflow": {"a": 1}})
        im = Image.open(r7["result"][0])
        assert "prompt" in im.text and "workflow" in im.text; n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
