import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_checkpoint_loader_info as m

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
    ok(m.info_line("a.safetensors", 1536) == "a.safetensors (1.5 KB)")
    ok(m.info_line("b.ckpt", 6 * 1024 ** 3) == "b.ckpt (6.0 GB)")
    ok(m.info_line("c", 0) == "c (0 B)")
    raises(m.info_line, "x", -1)
    raises(m.SYCheckpointLoaderInfo().run, "../evil.ckpt")
    ok(m.SYCheckpointLoaderInfo.RETURN_TYPES == ("MODEL", "CLIP", "VAE", "STRING"))
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYCheckpointLoaderInfo"] == "Checkpoint Loader Info SY")
    return N[0]
