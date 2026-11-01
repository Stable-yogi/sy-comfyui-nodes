import json
import os
import struct
import sys
import tempfile
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_power_lora as m
import _sy_lora_preview_api as api


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def row(**k):
    d = {"on": True, "name": "a.safetensors", "strength": 1.0, "strength_clip": None, "triggers": ""}
    d.update(k)
    return d


def write_st(path, meta=None, tensors=True):
    header = {}
    if meta is not None:
        header["__metadata__"] = meta
    if tensors:
        header["w"] = {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}
    raw = json.dumps(header).encode("utf-8")
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(raw)))
        f.write(raw)
        f.write(b"\x00\x00\x00\x00")


def run():
    n = 0
    # ---- parse_rows: good input
    assert m.parse_rows("") == [] and m.parse_rows(None) == [] and m.parse_rows("[]") == []; n += 1
    r = m.parse_rows('[{"name": "x.safetensors"}]')[0]
    assert r == {"on": True, "name": "x.safetensors", "strength": 1.0, "strength_clip": None, "triggers": ""}; n += 1
    r = m.parse_rows('[{"on": false, "name": " f/x.safetensors ", "strength": 0.8, "strength_clip": 0.5, "triggers": "a, b", "extra": 1}]')[0]
    assert r["on"] is False and r["name"] == "f/x.safetensors" and r["strength"] == 0.8 and r["strength_clip"] == 0.5; n += 1
    assert "extra" not in r and r["triggers"] == "a, b"; n += 1
    assert m.parse_rows('[{"strength": 2}]')[0]["strength"] == 2.0 and isinstance(m.parse_rows('[{"strength": 2}]')[0]["strength"], float); n += 1
    assert m.parse_rows('[{"triggers": null}]')[0]["triggers"] == ""; n += 1
    assert len(m.parse_rows(json.dumps([{"name": "a"}] * 64))) == 64; n += 1
    assert m.parse_rows('[{"strength": 10}, {"strength": -10}]')[1]["strength"] == -10.0; n += 1
    # ---- parse_rows: refusals
    assert "not readable" in refuses(m.parse_rows, "{bad"); n += 1
    assert "list of rows" in refuses(m.parse_rows, '{"a": 1}'); n += 1
    assert "list of rows" in refuses(m.parse_rows, '"text"'); n += 1
    msg = refuses(m.parse_rows, json.dumps([{"name": "a"}] * 65))
    assert msg and "65" in msg and "64" in msg; n += 1
    msg = refuses(m.parse_rows, '[{"name": "a"}, {"name": "b", "strength": 10.5}]')
    assert msg and "Row 2" in msg and "-10" in msg; n += 1
    msg = refuses(m.parse_rows, '[{"strength": -11}]')
    assert msg and "Row 1" in msg; n += 1
    msg = refuses(m.parse_rows, '[{"strength": 1, "strength_clip": 99}]')
    assert msg and "Row 1" in msg and "clip strength" in msg; n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"strength": "1"}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"strength": true}]'); n += 1
    assert "Row 3" in refuses(m.parse_rows, '[{}, {}, {"strength_clip": "x"}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"on": 1}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"on": "yes"}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"name": 5}]'); n += 1
    assert "Row 2" in refuses(m.parse_rows, '[{}, 7]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"triggers": ["a"]}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"strength": NaN}]'); n += 1
    assert "Row 1" in refuses(m.parse_rows, '[{"strength": Infinity}]'); n += 1
    # ---- check_rows
    assert m.check_rows([row()]) == [row()]; n += 1
    assert "list of rows" in refuses(m.check_rows, "x"); n += 1
    assert "most allowed" in refuses(m.check_rows, [row()] * 65); n += 1
    assert "Row 2" in refuses(m.check_rows, [row(), row(strength=-10.1)]); n += 1
    assert m.check_rows([row(strength_clip=None, strength=10)]) is not None; n += 1
    # ---- rows_to_json round trip
    rows = [row(name="f/a.safetensors", strength=0.5, strength_clip=0.25, triggers="x"), row(on=False)]
    assert m.parse_rows(m.rows_to_json(rows)) == rows; n += 1
    assert m.rows_to_json([]) == "[]"; n += 1
    # ---- clean_triggers
    assert m.clean_triggers(["a, b", "c"]) == "a, b, c"; n += 1
    assert m.clean_triggers(["a, b", "B, c, a"]) == "a, b, c"; n += 1
    assert m.clean_triggers(["a\nb\r\nc"], "newline") == "a\nb\nc"; n += 1
    assert m.clean_triggers(["a, b"], "space") == "a b"; n += 1
    assert m.clean_triggers(["  ", ",,", None, ""]) == ""; n += 1
    assert m.clean_triggers([" word one , two "]) == "word one, two"; n += 1
    assert m.clean_triggers([]) == ""; n += 1
    assert "trigger_join" in refuses(m.clean_triggers, ["a"], "dash"); n += 1
    # ---- resolve_name
    av = ["a.safetensors", "sub/b.safetensors", "x/c.safetensors", "y/c.safetensors", "style\\d.safetensors"]
    assert m.resolve_name("a.safetensors", av) == "a.safetensors"; n += 1
    assert m.resolve_name("sub/b.safetensors", av) == "sub/b.safetensors"; n += 1
    assert m.resolve_name("b.safetensors", av) == "sub/b.safetensors"; n += 1
    msg = refuses(m.resolve_name, "c.safetensors", av, 3)
    assert msg and "row 3" in msg and "more than one" in msg and "x/c.safetensors" in msg; n += 1
    msg = refuses(m.resolve_name, "zzz.safetensors", av, 2)
    assert msg == "LoRA 'zzz.safetensors' (row 2) was not found. Pick it again in the list."; n += 1
    assert "was not found" in refuses(m.resolve_name, "", av, 1); n += 1
    assert m.resolve_name("style/d.safetensors", av) == "style\\d.safetensors"; n += 1
    assert m.resolve_name("d.safetensors", av) == "style\\d.safetensors"; n += 1
    assert "(row" not in refuses(m.resolve_name, "q", av); n += 1
    assert "was not found" in refuses(m.resolve_name, "a.safetensors", []); n += 1
    assert m.resolve_name("a.safetensors", av + ["b/a.safetensors"]) == "a.safetensors"; n += 1  # exact wins over suffix
    assert "was not found" in refuses(m.resolve_name, "ub/b.safetensors", av); n += 1  # no half-folder match
    # ---- rows_to_info
    rows = [row(name="one.safetensors", strength=0.8), row(name="two.safetensors", on=False),
            row(name="three.safetensors", strength=0.5, strength_clip=0.25), row(name=""), row(name="z", strength=0)]
    info = m.rows_to_info(rows, {0, 2})
    lines = info.split("\n")
    assert lines[0] == "1. one.safetensors x0.80 (clip x0.80) on"; n += 1
    assert lines[1] == "2. two.safetensors off"; n += 1
    assert lines[2] == "3. three.safetensors x0.50 (clip x0.25) on"; n += 1
    assert "skipped" in lines[3] and "no LoRA picked" in lines[3]; n += 1
    assert lines[4] == "5. z skipped (strength 0)"; n += 1
    assert m.rows_to_info([], set()) == "No LoRA rows."; n += 1
    assert m.rows_to_info([row()], {0}, {0: "hello"}).endswith(" - hello"); n += 1
    # ---- cache
    c = m.LoraCache(2)
    calls = []
    for k in ("a", "b", "a", "c", "b"):
        c.get(k, lambda k=k: calls.append(k) or k.upper())
    assert calls == ["a", "b", "c", "b"]; n += 1
    assert list(c.items) == ["c", "b"]; n += 1
    assert m.CACHE_SIZE == 8 and len(m.LoraCache().items) == 0; n += 1
    # ---- apply loop with stand-ins (no torch)
    log = []

    def load(real):
        log.append(("load", real))
        return "T:" + real

    def apply(mo, cl, t, sm, sc):
        log.append(("apply", t, sm, sc))
        return mo + [t], (None if cl is None else cl + [t])

    rows = [row(name="a.safetensors", strength=0.5, triggers="alpha, beta"),
            row(name="b.safetensors", on=False, triggers="never"),
            row(name="sub/b.safetensors", strength=0.0, strength_clip=0.0, triggers="zero"),
            row(name="", triggers="empty"),
            row(name="b.safetensors", strength=1.0, strength_clip=0.3, triggers="beta, gamma")]
    mo, cl, trig, info = m.apply_rows(rows, [], [], av, load, apply)
    assert mo == ["T:a.safetensors", "T:sub/b.safetensors"] and cl == mo; n += 1
    assert trig == "alpha, beta, gamma"; n += 1
    assert log[1] == ("apply", "T:a.safetensors", 0.5, 0.5) and log[3] == ("apply", "T:sub/b.safetensors", 1.0, 0.3); n += 1
    assert "never" not in trig and "zero" not in trig and "empty" not in trig; n += 1
    assert info.split("\n")[1] == "2. b.safetensors off"; n += 1
    # no clip connected
    log.clear()
    mo, cl, trig, info = m.apply_rows([row(name="a.safetensors", strength=0.7, triggers="t")], [], None, av, load, apply)
    assert cl is None and mo == ["T:a.safetensors"] and log[1] == ("apply", "T:a.safetensors", 0.7, 0.0); n += 1
    assert "no clip connected" in info and trig == "t"; n += 1
    mo, cl, trig, info = m.apply_rows([row(name="a.safetensors", strength=0.0, strength_clip=0.9, triggers="t")], [], None, av, load, apply)
    assert mo == [] and trig == "" and "nothing to apply" in info; n += 1
    # model strength 0 but clip strength set is still applied
    mo, cl, trig, info = m.apply_rows([row(name="a.safetensors", strength=0.0, strength_clip=0.9)], [], [], av, load, apply)
    assert mo == ["T:a.safetensors"]; n += 1
    # missing file stops the run with the row number
    msg = refuses(m.apply_rows, [row(), row(name="nope.safetensors")], [], [], av, load, apply)
    assert msg and "row 2" in msg and "nope.safetensors" in msg; n += 1
    # separator and no applied rows
    mo, cl, trig, info = m.apply_rows([row(name="a.safetensors", triggers="p, q")], [], [], av, load, apply, "newline")
    assert trig == "p\nq"; n += 1
    mo, cl, trig, info = m.apply_rows([], [], [], av, load, apply)
    assert mo == [] and trig == "" and info == "No LoRA rows."; n += 1
    # ---- node class
    spec = m.SYPowerLoraLoader.INPUT_TYPES()
    assert list(spec["required"]) == ["model", "lora_rows", "all_on", "trigger_join"] and list(spec["optional"]) == ["clip"]; n += 1
    assert m.SYPowerLoraLoader.RETURN_TYPES == ("MODEL", "CLIP", "STRING", "STRING"); n += 1
    assert m.SYPowerLoraLoader.RETURN_NAMES == ("model", "clip", "trigger_words", "info"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPowerLoraLoader"] == "Power Lora Loader SY"; n += 1
    assert m.SYPowerLoraLoader.CATEGORY == "SY/Utility"; n += 1
    assert spec["required"]["trigger_join"][0] == ["comma", "newline", "space"]; n += 1
    assert spec["required"]["lora_rows"][1]["default"] == "[]" and spec["required"]["lora_rows"][1]["multiline"] is False; n += 1
    # master switch off and empty list never touch ComfyUI
    node = m.SYPowerLoraLoader()
    out = node.run("M", '[{"name": "a.safetensors"}]', False, "comma", "C")
    assert out[0] == "M" and out[1] == "C" and out[2] == "" and "Master switch is off" in out[3] and "1. a.safetensors off" in out[3]; n += 1
    out = node.run("M", "[]", True, "comma")
    assert out == ("M", None, "", "No LoRA rows."); n += 1
    out = node.run("M", '[{"name": "a", "on": false}]', True, "comma", "C")
    assert out[0] == "M" and out[1] == "C" and "off" in out[3]; n += 1
    assert "Row 1" in refuses(node.run, "M", '[{"strength": 50}]', True, "comma"); n += 1
    assert "trigger_join" in refuses(node.run, "M", "[]", True, "dash"); n += 1
    # the full node path with fake ComfyUI modules
    tmp = tempfile.mkdtemp(prefix="sy_pl_")
    fa = os.path.join(tmp, "a.safetensors")
    write_st(fa)
    fake_fp = types.ModuleType("folder_paths")
    fake_fp.get_filename_list = lambda kind: ["a.safetensors"]
    fake_fp.get_full_path = lambda kind, name: fa if name == "a.safetensors" else None
    fake_comfy = types.ModuleType("comfy")
    fake_sd = types.ModuleType("comfy.sd")
    fake_ut = types.ModuleType("comfy.utils")
    loads = []
    fake_ut.load_torch_file = lambda p, safe_load=False: loads.append(p) or {"p": p}
    fake_sd.load_lora_for_models = lambda mo, cl, t, sm, sc: ((mo, "lora", sm), (cl, "lora", sc))
    fake_comfy.sd, fake_comfy.utils = fake_sd, fake_ut
    saved = {k: sys.modules.get(k) for k in ("folder_paths", "comfy", "comfy.sd", "comfy.utils")}
    sys.modules.update({"folder_paths": fake_fp, "comfy": fake_comfy, "comfy.sd": fake_sd, "comfy.utils": fake_ut})
    try:
        txt = '[{"name": "a.safetensors", "strength": 0.6, "triggers": "hi, there"}]'
        out = node.run("M", txt, True, "space", "C")
        assert out[0] == ("M", "lora", 0.6) and out[1] == ("C", "lora", 0.6) and out[2] == "hi there"; n += 1
        assert out[3] == "1. a.safetensors x0.60 (clip x0.60) on"; n += 1
        node.run("M", txt, True, "space", "C")
        assert len(loads) == 1; n += 1  # second run comes from the cache
        assert "was not found" in refuses(node.run, "M", '[{"name": "gone.safetensors"}]', True, "comma", "C"); n += 1
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    # ---- helper: names
    assert api.check_lora_name("a.safetensors") == "a.safetensors" and api.check_lora_name("sub/a b.safetensors"); n += 1
    for bad in ("../x", "a/../x", "a\\..\\x", "/etc/x", "\\x", "C:/x", "c:\\x", "", "   ", None, 5, "a\x00b"):
        assert refuses(api.check_lora_name, bad) is not None; n += 1
    assert api.check_lora_name("a..b.safetensors") == "a..b.safetensors"; n += 1
    # ---- helper: path guard
    root = os.path.join(tmp, "loras")
    os.makedirs(os.path.join(root, "sub"))
    inner = os.path.join(root, "sub", "k.safetensors")
    write_st(inner)
    assert api.inside_roots(inner, [root]) is True; n += 1
    assert api.inside_roots(fa, [root]) is False; n += 1
    assert api.inside_roots(os.path.join(root, "..", "a.safetensors"), [root]) is False; n += 1
    assert api.inside_roots(root, [root]) is False; n += 1
    assert api.inside_roots(inner, []) is False; n += 1
    got = lambda name: os.path.join(root, name.replace("/", os.sep))  # noqa: E731
    assert api.lora_path("sub/k.safetensors", got, [root]) == got("sub/k.safetensors"); n += 1
    assert "not found" in refuses(api.lora_path, "sub/none.safetensors", got, [root]); n += 1
    assert "outside" in refuses(api.lora_path, "x", lambda nm: fa, [root]); n += 1
    assert refuses(api.lora_path, "../a.safetensors", got, [root]) is not None; n += 1
    # ---- helper: preview picture
    assert api.find_preview(inner, [root]) is None; n += 1
    pic = os.path.join(root, "sub", "k.jpg")
    open(pic, "wb").write(b"x")
    assert api.find_preview(inner, [root]) == pic; n += 1
    pre = os.path.join(root, "sub", "k.preview.png")
    open(pre, "wb").write(b"x")
    assert api.find_preview(inner, [root]) == pre; n += 1  # .preview.png comes first
    open(pre, "wb").write(b"x" * (api.MAX_PREVIEW_BYTES + 1))
    assert api.find_preview(inner, [root]) == pic; n += 1  # too big is skipped
    open(pic, "wb").write(b"x" * (api.MAX_PREVIEW_BYTES + 1))
    assert api.find_preview(inner, [root]) is None; n += 1
    assert api.mime_of("a.PNG") == "image/png" and api.mime_of("a.webp") == "image/webp" and api.mime_of("a.txt") == "application/octet-stream"; n += 1
    # ---- helper: top_tags
    tf = json.dumps({"d1": {"cat": 5, "dog": 9, "bird": 1}, "d2": {"cat": 6, " ": 3, "x": "no", "y": True}})
    assert api.top_tags(tf, 2) == ["cat", "dog"]; n += 1  # cat = 11 beats dog = 9
    assert api.top_tags(tf, 10) == ["cat", "dog", "bird"]; n += 1
    assert api.top_tags(tf, 0) == []; n += 1
    assert api.top_tags("", 5) == [] and api.top_tags(None, 5) == [] and api.top_tags("[1]", 5) == []; n += 1
    assert api.top_tags("{bad", 5) == []; n += 1
    assert api.top_tags({"a": {"t1": 2, "t2": 2}}, 5) == ["t1", "t2"]; n += 1  # ties keep first-seen order
    assert api.top_tags({"a": "oops", "b": {"z": 1}}, 5) == ["z"]; n += 1
    many = {"a": {"t%d" % i: i for i in range(30)}}
    assert api.top_tags(many)[:3] == ["t29", "t28", "t27"] and len(api.top_tags(many)) == 10; n += 1
    # ---- helper: safetensors header reader
    meta = {"ss_tag_frequency": tf, "modelspec.trigger_phrase": "magic, word"}
    f1 = os.path.join(tmp, "h.safetensors")
    write_st(f1, meta)
    h = api.read_st_header(f1)
    assert h["__metadata__"]["modelspec.trigger_phrase"] == "magic, word" and "w" in h; n += 1
    info = api.lora_info(f1)
    assert info["tags"] == ["cat", "dog", "bird"] and info["triggers"] == ["magic", "word"]; n += 1
    f2 = os.path.join(tmp, "nometa.safetensors")
    write_st(f2, None)
    assert api.lora_info(f2) == {"tags": [], "triggers": []}; n += 1
    f3 = os.path.join(tmp, "short.safetensors")
    open(f3, "wb").write(b"abc")
    assert "too short" in refuses(api.read_st_header, f3); n += 1
    f4 = os.path.join(tmp, "huge.safetensors")
    open(f4, "wb").write(struct.pack("<Q", 9 * 1024 * 1024) + b"{}")
    assert "larger than 8 MB" in refuses(api.read_st_header, f4); n += 1
    assert "larger" in refuses(api.read_st_header, f4, 1000); n += 1
    f5 = os.path.join(tmp, "cut.safetensors")
    open(f5, "wb").write(struct.pack("<Q", 50) + b"{}")
    assert "cut off" in refuses(api.read_st_header, f5); n += 1
    f6 = os.path.join(tmp, "junk.safetensors")
    open(f6, "wb").write(struct.pack("<Q", 4) + b"nope")
    assert "not readable" in refuses(api.read_st_header, f6); n += 1
    f7 = os.path.join(tmp, "list.safetensors")
    open(f7, "wb").write(struct.pack("<Q", 2) + b"[]")
    assert "not readable" in refuses(api.read_st_header, f7); n += 1
    f8 = os.path.join(tmp, "zero.safetensors")
    open(f8, "wb").write(struct.pack("<Q", 0))
    assert refuses(api.read_st_header, f8) is not None; n += 1
    # the reader reads only the header: a big body after it is never touched
    f9 = os.path.join(tmp, "big.safetensors")
    write_st(f9, {"k": "v"})
    with open(f9, "ab") as fh:
        fh.write(b"\x00" * 100000)
    assert api.read_st_header(f9)["__metadata__"] == {"k": "v"}; n += 1
    assert api.register_routes() in (True, False); n += 1
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return n


if __name__ == "__main__":
    print(run())
