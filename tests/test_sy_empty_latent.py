import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_empty_latent as m


def _raises(*args):
    try:
        m.latent_shape(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.latent_shape(1024, 1024, 1, "standard 4ch /8") == (1, 4, 128, 128); n += 1
    assert m.latent_shape(1024, 512, 2, "flux 16ch /8") == (2, 16, 64, 128); n += 1
    assert m.latent_shape(8, 8, 1, "standard 4ch /8") == (1, 4, 1, 1); n += 1
    assert m.latent_shape(1020, 1020, 1, "standard 4ch /8") == (1, 4, 127, 127); n += 1  # non-multiple floors
    assert m.latent_shape(16384, 16384, 1, "flux 16ch /8") == (1, 16, 2048, 2048); n += 1
    for bad in ((0, 512, 1, "standard 4ch /8"), (512, 0, 1, "standard 4ch /8"), (7, 512, 1, "standard 4ch /8"),
                (99999, 512, 1, "standard 4ch /8"), (512, 512, 0, "standard 4ch /8"),
                (512, 512, 99999, "standard 4ch /8"), (512, 512, 1, "nope")):
        assert _raises(*bad), bad
        n += 1
    assert m.SYEmptyLatent.RETURN_TYPES == ("LATENT",); n += 1
    return n
