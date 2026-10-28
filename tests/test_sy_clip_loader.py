import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_clip_loader as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    L = m.CLIP_TYPES
    ok("stable_diffusion" in L and "wan" in L and "flux2" in L)
    ok(len(set(L)) == len(L))
    ok(m.check_choice("cpu", m.CLIP_DEVICES, "device") == "cpu")
    raises(m.check_choice, "gpu", m.CLIP_DEVICES, "device")
    node = m.SYCLIPLoader()
    raises(node.run, "a.safetensors", "not_a_type", "default")
    raises(node.run, "a.safetensors", "wan", "gpu")
    raises(node.run, "../a.safetensors", "wan", "default")
    spec = m.SYCLIPLoader.INPUT_TYPES()["required"]
    ok(spec["type"][0] == L)
    ok("minimax" in L and "ideogram4" in L)
    ok(m.clip_types() == L)
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYCLIPLoader"] == "CLIP Loader SY")
    return N[0]
