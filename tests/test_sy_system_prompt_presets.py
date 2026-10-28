import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_system_prompt_presets as m


def run():
    n = 0
    assert len(m.PRESET_NAMES) == 12; n += 1
    for name in m.PRESET_NAMES:
        assert m.system_prompt(name) == m.PRESETS[name] and len(m.PRESETS[name]) > 20
        n += 1
    assert m.system_prompt("translator", "  My own  ") == "My own"; n += 1
    assert m.system_prompt("translator", "   ") == m.PRESETS["translator"]; n += 1
    for bad in (("nope", ""), ("translator", 3)):
        try:
            m.system_prompt(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYSystemPromptPresets().run("summariser")[0] == m.PRESETS["summariser"]; n += 1
    return n
