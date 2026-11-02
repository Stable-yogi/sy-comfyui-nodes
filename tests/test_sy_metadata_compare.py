import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_metadata_compare as m


def run():
    n = 0
    a1111 = ("a cat\nNegative prompt: blurry\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: 7, "
             "Seed: 123, Size: 512x768, Model: base")
    sa = m.settings_from_info({"parameters": a1111})
    assert sa["prompt"] == "a cat" and sa["negative prompt"] == "blurry", sa
    assert sa["steps"] == "20" and sa["cfg"] == "7" and sa["sampler"] == "Euler a", sa
    assert sa["scheduler"] == "Karras" and sa["seed"] == "123" and sa["size"] == "512x768" and sa["model"] == "base", sa
    n += 8
    assert m.settings_from_info({}) == {} and m.settings_from_info(None) == {}
    assert m.settings_from_info({"other": "x"}) == {}
    n += 3
    # ComfyUI prompt json
    graph = ('{"1":{"inputs":{"text":"dog"}},"2":{"inputs":{"text":"ugly"}},'
             '"3":{"inputs":{"positive":["1",0],"negative":["2",0],"seed":5,"steps":9,"cfg":3.5,'
             '"sampler_name":"euler","scheduler":"simple"}},"4":{"inputs":{"ckpt_name":"m.safetensors"}}}')
    sc = m.settings_from_info({"prompt": graph}, (64, 32))
    assert sc["prompt"] == "dog" and sc["negative prompt"] == "ugly" and sc["seed"] == "5", sc
    assert sc["sampler"] == "euler" and sc["scheduler"] == "simple" and sc["model"] == "m.safetensors" and sc["size"] == "64x32", sc
    n += 6
    rows = m.compare_settings(sa, dict(sa))
    assert [r[0] for r in rows] == list(m.FIELDS) and all(r[3] for r in rows)
    n += 2
    sb = dict(sa, steps="30", cfg="7.0", seed="124")
    diff = {r[0] for r in m.compare_settings(sa, sb) if not r[3]}
    assert diff == {"steps", "seed"}, diff   # 7 and 7.0 are the same number
    n += 1
    rows = m.compare_settings(sa, {})
    assert rows[0][2] == m.MISSING and not rows[0][3]
    assert m.compare_settings({}, {})[0][3]       # missing on both sides is not a difference
    n += 2
    rep, ident, cnt = m.build_report(m.compare_settings(sa, sb), True, "", "")
    assert not ident and cnt == 2 and "| steps | 20 | 30 | different |" in rep and "| cfg |" not in rep
    assert "2 of 9" in rep
    n += 4
    rep, ident, cnt = m.build_report(m.compare_settings(sa, sb), False)
    assert "| cfg | 7 | 7.0 | same |" in rep
    n += 1
    rep, ident, cnt = m.build_report(m.compare_settings(sa, dict(sa)), True)
    assert ident and cnt == 0 and "Nothing differs" in rep
    n += 2
    rep, _, _ = m.build_report(m.compare_settings(sa, {}), True, "", "b.png holds no generation data.")
    assert "b.png holds no generation data." in rep and "(missing)" in rep
    n += 1
    rep, _, _ = m.build_report(m.compare_settings({"prompt": "a|b\nc"}, {"prompt": "x" * 500}), True)
    assert "a\\|b c" in rep and "..." in rep
    n += 2
    assert m.SYMetadataCompare.RETURN_TYPES == ("STRING", "BOOLEAN", "INT")
    n += 1
    for bad in ("", "../x.png", "/etc/x.png", "C:\\x.png", "x.jpg"):
        try:
            m._read_one(bad)
            raise SystemExit("must raise for %r" % bad)
        except ValueError:
            pass
    n += 5
    return n
