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
    assert m.SYSamplerSettings.RETURN_TYPES == ("SY_SAMPLER_SETTINGS",)
    assert m.SYSamplerSettingsUnpack.INPUT_TYPES()["required"]["settings"][0] == "SY_SAMPLER_SETTINGS"
    out = m.SYSamplerSettings().run(10, 3.5, "euler", "simple")
    assert m.SYSamplerSettingsUnpack().run(out[0]) == (10, 3.5, "euler", "simple")
    n += 3
    return n
