import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_checkpoint_name_filter as m


def run():
    n = 0
    names = ["sdxl_base.safetensors", "Flux/flux_dev.safetensors", "Krea2_Muse.safetensors", "flux_schnell.safetensors"]
    assert m.filter_names(names, "FLUX") == ["Flux/flux_dev.safetensors", "flux_schnell.safetensors"]
    assert m.pick_first(names, "krea") == "Krea2_Muse.safetensors"
    assert m.pick_first(names, " sdxl ") == "sdxl_base.safetensors"
    assert m.pick_first(names, "") == "Flux/flux_dev.safetensors"  # empty text matches all
    n += 4
    for bad in ((names, "zzz"), ([], "a")):
        try:
            m.pick_first(*bad)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    try:
        m.SYCheckpointNameFilter().run("x")  # no comfy here, so the list is empty
        raise SystemExit("must raise")
    except ValueError:
        n += 1
    # more value: several words, exclude, index, lists, info
    c, k, lst, info = m.pick_match(names, "flux dev")
    assert c == "Flux/flux_dev.safetensors" and k == 1 and lst == c and "1 of 4" in info; n += 1
    c, k, lst, info = m.pick_match(names, "flux")
    assert k == 2 and lst == "Flux/flux_dev.safetensors" + chr(10) + "flux_schnell.safetensors"; n += 1
    assert m.pick_match(names, "flux", index=1)[0] == "flux_schnell.safetensors"; n += 1
    assert m.pick_match(names, "flux", index=2)[0] == "Flux/flux_dev.safetensors"; n += 1  # wraps
    assert m.pick_match(names, "flux", exclude="dev")[0] == "flux_schnell.safetensors"; n += 1
    assert m.pick_match(names, "  KREA   muse ")[0] == "Krea2_Muse.safetensors"; n += 1
    assert m.pick_match(names, "")[1] == 4; n += 1
    for bad in ((names, "flux", "flux"), (names, "zzz"), ([], "a")):
        try:
            m.pick_match(*bad)
            raise SystemExit("must raise")
        except ValueError as e:
            assert "checkpoint" in str(e)
        n += 1
    spec = m.SYCheckpointNameFilter.INPUT_TYPES()
    assert list(spec["required"]) == ["contains"] and list(spec["optional"]) == ["exclude", "index"]; n += 1
    assert m.SYCheckpointNameFilter.RETURN_TYPES == ("STRING", "INT", "STRING", "STRING"); n += 1
    assert m.SYCheckpointNameFilter.RETURN_NAMES[:2] == ("name", "match_count"); n += 1
    return n
