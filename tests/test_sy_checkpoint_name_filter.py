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
    return n
