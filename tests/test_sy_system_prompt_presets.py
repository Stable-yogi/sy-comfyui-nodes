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
    return n + _extra()


def _extra():
    n = 0
    base = m.PRESETS["translator"]
    assert m.system_prompt("translator", "", True) == base + " " + m.NO_CHATTER; n += 1
    assert m.system_prompt("translator", "", False, " German ") == base + " Reply in German."; n += 1
    assert m.system_prompt("translator", "", False, "", "Keep names.") == base + " Keep names."; n += 1
    assert m.system_prompt("translator", "Mine", True, "French", "Short.") == "Mine Short. Reply in French. " + m.NO_CHATTER; n += 1
    text, info = m.system_prompt_info("summariser", "", True)
    assert info.startswith("System prompt from preset 'summariser' plus no-chatter rule;") and "tokens" in info; n += 1
    assert m.system_prompt_info("x" if False else "translator", "Own")[1].startswith("System prompt from your custom text;"); n += 1
    try:
        m.system_prompt("translator", "", False, 5)
        raise SystemExit("bad language must raise")
    except ValueError:
        n += 1
    out = m.SYSystemPromptPresets().run("proofreader", "", True, "English")
    assert out[0].endswith(m.NO_CHATTER) and "Reply in English." in out[0] and len(out) == 2; n += 1
    assert m.SYSystemPromptPresets.RETURN_NAMES == ("system_prompt", "info"); n += 1
    return n
