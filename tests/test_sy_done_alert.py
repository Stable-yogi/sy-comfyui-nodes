import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_done_alert as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    d = m.clean_settings()
    assert d["message"] == "Your workflow is finished." and d["sound"] == "chime"; n += 1
    assert d["show_message"] is True and d["desktop_notice"] is False; n += 1
    assert d["volume"] == 0.4 and d["only_when_idle"] is True; n += 1
    assert set(d) == {"message", "sound", "show_message", "desktop_notice", "volume", "only_when_idle"}; n += 1
    assert m.clean_settings(volume=2)["volume"] == 1.0; n += 1
    assert m.clean_settings(volume=-3)["volume"] == 0.0; n += 1
    assert m.clean_settings(volume=0)["volume"] == 0.0; n += 1
    assert m.clean_settings(volume=1)["volume"] == 1.0; n += 1
    assert m.clean_settings(volume=0.12345)["volume"] == 0.123; n += 1
    assert isinstance(m.clean_settings(volume=1)["volume"], float); n += 1
    assert "Volume" in refuses(m.clean_settings, volume="loud"); n += 1
    assert "Volume" in refuses(m.clean_settings, volume=None); n += 1
    assert "Volume" in refuses(m.clean_settings, volume=True); n += 1
    assert "Volume" in refuses(m.clean_settings, volume=float("nan")); n += 1
    for s in m.SOUNDS:
        assert m.clean_settings(sound=s)["sound"] == s; n += 1
    assert "Sound must be one of" in refuses(m.clean_settings, sound="siren"); n += 1
    assert "Sound" in refuses(m.clean_settings, sound=None); n += 1
    assert m.clean_settings(message="")["message"] == m.DEFAULT_MESSAGE; n += 1
    assert m.clean_settings(message="   \n ")["message"] == m.DEFAULT_MESSAGE; n += 1
    assert m.clean_settings(message=None)["message"] == m.DEFAULT_MESSAGE; n += 1
    assert m.clean_settings(message="  All   done\nnow ")["message"] == "All done now"; n += 1
    assert len(m.clean_settings(message="x" * 500)["message"]) == m.MAX_MESSAGE; n += 1
    assert "message" in refuses(m.clean_settings, message=5).lower(); n += 1
    assert "show_message" in refuses(m.clean_settings, show_message="yes"); n += 1
    assert "desktop_notice" in refuses(m.clean_settings, desktop_notice=1); n += 1
    assert "only_when_idle" in refuses(m.clean_settings, only_when_idle=None); n += 1
    assert m.clean_settings(show_message=False)["show_message"] is False; n += 1
    assert m.clean_settings(desktop_notice=True)["desktop_notice"] is True; n += 1
    # payload
    p = m.alert_payload("Hi", "beep", True, True, 0.7, False)
    assert list(p) == ["sy_alert"] and len(p["sy_alert"]) == 1 and isinstance(p["sy_alert"][0], str); n += 1
    j = json.loads(p["sy_alert"][0])
    assert j == {"message": "Hi", "sound": "beep", "show_message": True, "desktop_notice": True, "volume": 0.7, "only_when_idle": False}; n += 1
    assert json.loads(m.alert_payload()["sy_alert"][0]) == m.clean_settings(); n += 1
    assert refuses(m.alert_payload, sound="x") is not None; n += 1
    # class contract
    c = m.SYDoneAlert
    it = c.INPUT_TYPES()
    assert list(it["required"]) == ["anything", "message", "sound", "show_message", "desktop_notice", "volume", "only_when_idle"]; n += 1
    assert not it.get("optional"); n += 1
    for k, v in it["required"].items():
        tip = v[1].get("tooltip")
        assert isinstance(tip, str) and 0 < len(tip) <= 120, k; n += 1
    assert it["required"]["anything"][0] == "*" and not (it["required"]["anything"][0] != "*"); n += 1
    assert it["required"]["message"][1]["default"] == "Your workflow is finished."; n += 1
    assert it["required"]["sound"][0] == list(m.SOUNDS) and it["required"]["sound"][1]["default"] == "chime"; n += 1
    assert it["required"]["show_message"][1]["default"] is True; n += 1
    assert it["required"]["desktop_notice"][1]["default"] is False; n += 1
    assert "permission" in it["required"]["desktop_notice"][1]["tooltip"]; n += 1
    vol = it["required"]["volume"][1]
    assert vol["default"] == 0.4 and vol["min"] == 0.0 and vol["max"] == 1.0; n += 1
    assert it["required"]["only_when_idle"][1]["default"] is True; n += 1
    assert len(c.RETURN_TYPES) == 1 and c.RETURN_TYPES[0] == "*" and c.RETURN_NAMES == ("anything",); n += 1
    assert c.OUTPUT_NODE is True and c.FUNCTION == "run" and c.CATEGORY == "SY/Utility"; n += 1
    assert c.DESCRIPTION.strip(); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYDoneAlert"] == "Done Alert SY"; n += 1
    assert m.NODE_CLASS_MAPPINGS["SYDoneAlert"] is c; n += 1
    # run
    obj = object()
    out = c().run(obj)
    assert out["result"][0] is obj; n += 1
    assert json.loads(out["ui"]["sy_alert"][0])["sound"] == "chime"; n += 1
    out = c().run(5, "Done!", "none", False, False, 0.0, False)
    assert out["result"] == (5,) and json.loads(out["ui"]["sy_alert"][0])["message"] == "Done!"; n += 1
    assert refuses(c().run, 1, "x", "bad") is not None; n += 1
    return n


if __name__ == "__main__":
    print(run())
