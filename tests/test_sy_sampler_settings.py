import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sampler_settings as m


def run():
    n = 0
    s = m.build_settings(20, 5, "euler", "simple")
    assert s == {"steps": 20, "cfg": 5.0, "sampler_name": "euler", "scheduler": "simple"}
    assert m.unpack_settings(s) == (20, 5.0, "euler", "simple")
    n += 2
    s = m.build_settings(8, 1.0, "euler", "simple", ["euler"], ["simple"])
    assert m.unpack_settings(s)[0] == 8
    n += 1
    bad_calls = [
        lambda: m.build_settings(0, 5, "euler", "simple"),
        lambda: m.build_settings(5, -1, "euler", "simple"),
        lambda: m.build_settings(5, 5, "", "simple"),
        lambda: m.build_settings(5, 5, "euler", ""),
        lambda: m.build_settings(5, 5, "zzz", "simple", ["euler"], ["simple"]),
        lambda: m.build_settings(5, 5, "euler", "zzz", ["euler"], ["simple"]),
        lambda: m.unpack_settings("x"),
        lambda: m.unpack_settings({"steps": 1}),
    ]
    for f in bad_calls:
        try:
            f()
            raise SystemExit("bad input must raise")
        except ValueError:
            n += 1
    assert m.SYSamplerSettings.RETURN_TYPES[0] == "SY_SAMPLER_SETTINGS"
    assert m.SYSamplerSettingsUnpack.INPUT_TYPES()["required"]["settings"][0] == "SY_SAMPLER_SETTINGS"
    out = m.SYSamplerSettings().run(10, 3.5, "euler", "simple")
    assert m.SYSamplerSettingsUnpack().run(out[0])[:4] == (10, 3.5, "euler", "simple")
    n += 3
    # --- value pass A2: denoise in the bundle, hints and info line
    s = m.build_settings(20, 5, "euler", "simple", denoise=0.6)
    assert s["denoise"] == 0.6 and m.unpack_settings(s) == (20, 5.0, "euler", "simple"); n += 2
    assert "denoise" not in m.build_settings(20, 5, "euler", "simple"); n += 1
    for bad in (-0.1, 1.5, float("nan")):
        try:
            m.build_settings(20, 5, "euler", "simple", denoise=bad)
            raise SystemExit("bad denoise must raise")
        except ValueError:
            n += 1
    old = {"steps": 20, "cfg": 5.0, "sampler_name": "euler", "scheduler": "simple"}  # bundle saved before denoise existed
    assert m.SYSamplerSettingsUnpack().run(old) == (20, 5.0, "euler", "simple", 1.0, "20 steps, cfg 5, euler / simple, denoise 1"); n += 1
    assert m.settings_hints(old) == []; n += 1
    assert "ignores your prompt" in m.settings_hints(dict(old, cfg=0))[0]; n += 1
    assert "skips the negative prompt" in m.settings_hints(dict(old, cfg=1))[0]; n += 1
    assert "burn" in m.settings_hints(dict(old, cfg=15))[0]; n += 1
    assert any("turbo" in t for t in m.settings_hints(dict(old, steps=4))); n += 1
    assert any("a lot" in t for t in m.settings_hints(dict(old, steps=150))); n += 1
    assert any("fresh noise" in t for t in m.settings_hints(dict(old, sampler_name="euler_ancestral"))); n += 1
    assert any("fresh noise" in t for t in m.settings_hints(dict(old, sampler_name="dpmpp_2m_sde"))); n += 1
    assert any("keeps part" in t for t in m.settings_hints(dict(old, denoise=0.5))); n += 1
    assert m.info_text(dict(old, cfg=1, denoise=0.5)).split("\n")[0] == "20 steps, cfg 1, euler / simple, denoise 0.5"; n += 1
    out = m.SYSamplerSettings().run(10, 3.5, "euler", "simple", 0.8)
    assert len(out) == 2 and out[0]["denoise"] == 0.8 and out[1].startswith("10 steps"); n += 1
    assert m.SYSamplerSettings.RETURN_NAMES == ("settings", "info") and m.SYSamplerSettingsUnpack.RETURN_NAMES[-2:] == ("denoise", "info"); n += 1
    assert len(m.SYSamplerSettingsUnpack.RETURN_TYPES) == len(m.SYSamplerSettingsUnpack.RETURN_NAMES) == 6; n += 1
    return n
