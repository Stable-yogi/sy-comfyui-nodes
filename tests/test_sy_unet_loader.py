import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_unet_loader as m

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
    ok(m.unet_options("default") == {"dtype": None, "fp8_fast": False})
    ok(m.unet_options("fp8_e4m3fn") == {"dtype": "float8_e4m3fn", "fp8_fast": False})
    ok(m.unet_options("fp8_e4m3fn_fast") == {"dtype": "float8_e4m3fn", "fp8_fast": True})
    ok(m.unet_options("fp8_e5m2") == {"dtype": "float8_e5m2", "fp8_fast": False})
    raises(m.unet_options, "fp16")
    raises(m.SYUnetLoader().run, "a.safetensors", "bf4")
    raises(m.SYUnetLoader().run, "../a.safetensors", "default")
    ok(m.SYUnetLoader.RETURN_TYPES == ("MODEL",))
    return N[0]
