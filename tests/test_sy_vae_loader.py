import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_vae_loader as m

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
    raises(m.SYVAELoader().run, "../x.safetensors")
    raises(m.SYVAELoader().run, "/abs/path.safetensors")
    raises(m.SYVAELoader().run, "")
    ok(m.SYVAELoader.RETURN_TYPES == ("VAE",))
    ok("tooltip" in m.SYVAELoader.INPUT_TYPES()["required"]["vae_name"][1])
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYVAELoader"] == "VAE Loader SY")
    return N[0]
