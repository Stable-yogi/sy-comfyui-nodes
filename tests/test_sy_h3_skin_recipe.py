import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_skin_recipe as m

NAMES = [
    "other/random.safetensors",
    "h3/H3_Turbo_4Step_v1.safetensors",
    "h3\\h3_turbo_8step_v2.safetensors",
    "styles/People_Realism_v3.safetensors",
    "detail/H3_EMA_detail.safetensors",
]


def run():
    n = 0
    # pick_auto
    assert m.pick_auto(NAMES, "turbo", "balanced") == "h3\\h3_turbo_8step_v2.safetensors"
    assert m.pick_auto(NAMES, "turbo", "max skin") == "h3\\h3_turbo_8step_v2.safetensors"
    assert m.pick_auto(NAMES, "turbo", "fast") == "h3/H3_Turbo_4Step_v1.safetensors"
    assert m.pick_auto(NAMES, "people", "balanced") == "styles/People_Realism_v3.safetensors"
    assert m.pick_auto(NAMES, "detail", "max skin") == "detail/H3_EMA_detail.safetensors"
    n += 5
    # nothing matches -> none; a folder name alone must not match
    assert m.pick_auto(["x.safetensors"], "turbo", "fast") == "none"
    assert m.pick_auto([], "people", "balanced") == "none"
    assert m.pick_auto(["turbo_8step_folder/plain.safetensors"], "turbo", "balanced") == "none"
    assert m.pick_auto(["a/realism/plain.safetensors"], "people", "balanced") == "none"
    assert m.pick_auto(["people_only.safetensors", "realism.safetensors"], "people", "fast") == "people_only.safetensors"
    n += 5
    for bad in (("nope", "fast"), ("turbo", "huge")):
        try:
            m.pick_auto(NAMES, *bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    n += 2
    # tier plans
    p = m.tier_plan("fast", 1.2)
    assert (p["steps"], p["people_strength"], p["use_detail"], p["sampler"], p["scheduler"], p["cfg"]) == (4, 0.6, False, "euler", "beta", 1.0)
    p = m.tier_plan("balanced", 0.9)
    assert (p["steps"], p["people_strength"], p["use_detail"], p["sampler"], p["scheduler"], p["cfg"]) == (8, 0.9, False, "euler", "beta", 1.0)
    p = m.tier_plan("max skin", 0.5)
    assert (p["steps"], p["people_strength"], p["use_detail"], p["sampler"], p["scheduler"], p["cfg"]) == (10, 0.5, True, "euler", "beta", 1.0)
    assert "follow the prompt a little less" in p["note"]
    assert m.tier_plan("balanced")["note"] == ""
    n += 5
    # override wins
    assert m.tier_plan("fast", 0.75, 6)["steps"] == 6
    assert m.tier_plan("max skin", 0.75, 20)["steps"] == 20
    assert m.tier_plan("balanced", 0.75, 0)["steps"] == 8
    n += 3
    for bad in (("giant", 0.75, 0), ("fast", 0.75, -1)):
        try:
            m.tier_plan(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    n += 2
    # resolve_loras
    plan = m.tier_plan("balanced")
    out = m.resolve_loras(NAMES, "balanced", "auto", "auto", "auto", plan)
    assert out == [("turbo", "h3\\h3_turbo_8step_v2.safetensors"), ("people", "styles/People_Realism_v3.safetensors"), ("detail", "none")]
    plan = m.tier_plan("max skin")
    out = m.resolve_loras(NAMES, "max skin", "auto", "none", "auto", plan)
    assert out[1] == ("people", "none") and out[2] == ("detail", "detail/H3_EMA_detail.safetensors")
    out = m.resolve_loras(NAMES, "max skin", "other/random.safetensors", "auto", "none", plan)
    assert out[0] == ("turbo", "other/random.safetensors") and out[2] == ("detail", "none")
    out = m.resolve_loras(NAMES, "fast", "auto", "auto", "auto", m.tier_plan("fast"))
    assert out[0][1].endswith("4Step_v1.safetensors") and out[2] == ("detail", "none")
    n += 4
    try:
        m.resolve_loras(NAMES, "balanced", "missing/file.safetensors", "auto", "auto", m.tier_plan("balanced"))
        raise SystemExit("a missing file must raise")
    except ValueError as e:
        assert "missing/file.safetensors" in str(e) and "loras folder" in str(e)
    n += 1
    # info text mentions every LoRA
    loras = m.resolve_loras(NAMES, "max skin", "auto", "auto", "auto", m.tier_plan("max skin", 0.7))
    strengths = {"turbo": 1.0, "people": 0.7, "detail": 1.0}
    info = m.info_text("max skin", loras, strengths, 10, m.MAX_SKIN_NOTE)
    for _, name in loras:
        assert name in info
    assert "0.7" in info and "10" in info and "max skin" in info and "euler" in info and "beta" in info and "follow the prompt" in info
    info = m.info_text("fast", [("turbo", "none"), ("people", "none"), ("detail", "none")], strengths, 4, "")
    assert info.count("none") == 3 and "fast" in info
    n += 2
    # node class: outputs and input lists (comfy is not here, so the lora list is just auto + none)
    cls = m.SYH3SkinRecipe
    assert len(cls.RETURN_TYPES) == len(cls.RETURN_NAMES) == 9
    assert cls.RETURN_NAMES[:7] == ("model", "steps", "sampler_name", "scheduler", "cfg", "trigger_text", "info")
    assert isinstance(cls.RETURN_TYPES[7], list) and "euler" in cls.RETURN_TYPES[7]
    assert isinstance(cls.RETURN_TYPES[8], list) and "beta" in cls.RETURN_TYPES[8]
    req = cls.INPUT_TYPES()["required"]
    assert req["turbo_lora"][0][:2] == ["auto", "none"] and req["tier"][1]["default"] == "balanced"
    assert req["people_strength"][1]["default"] == 0.75 and req["people_strength"][1]["max"] == 1.5
    assert req["turbo_strength"][1]["max"] == 2.0 and req["steps_override"][1]["max"] == 60
    n += 6
    # run() with every LoRA "none" needs no model tools
    sentinel = object()
    res = cls().run(sentinel, "max skin", "none", "none", "none", 0.75, 1.0, 1.0, 0)
    assert res[0] is sentinel and res[1:6] == (10, "euler", "beta", 1.0, "") and "none" in res[6] and res[7:] == ("euler", "beta")
    res = cls().run(sentinel, "fast", "none", "none", "none", 0.75, 1.0, 1.0, 5)
    assert res[1] == 5
    try:
        cls().run(sentinel, "balanced", "nofile.safetensors", "none", "none")
        raise SystemExit("an unknown file must raise")
    except ValueError as e:
        assert "nofile.safetensors" in str(e)
    n += 4
    return n
