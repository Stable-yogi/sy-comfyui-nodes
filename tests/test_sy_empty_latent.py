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


def _plan_raises(*args):
    try:
        m.plan_latent(*args)
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
    assert m.SYEmptyLatent.RETURN_TYPES == ("LATENT", "INT", "INT", "STRING"); n += 1
    assert m.SYEmptyLatent.RETURN_NAMES == ("latent", "width", "height", "info"); n += 1
    # added value: snap_to, real picture size, info text
    shape, pw, ph, info = m.plan_latent(1024, 1024, 1, "standard 4ch /8")
    assert shape == (1, 4, 128, 128) and (pw, ph) == (1024, 1024) and "1.05 MP" in info and "Warning" not in info; n += 1
    shape, pw, ph, info = m.plan_latent(1020, 1020, 1, "standard 4ch /8")
    assert shape == (1, 4, 127, 127) and (pw, ph) == (1016, 1016) and "not a multiple of 8" in info and "snap_to" in info; n += 1
    shape, pw, ph, info = m.plan_latent(1020, 1020, 1, "standard 4ch /8", "64")
    assert (pw, ph) == (1024, 1024) and "Snapped 1020x1020 to 1024x1024" in info and "not a multiple" not in info; n += 1
    assert m.plan_latent(1000, 700, 1, "flux 16ch /8", "16")[1:3] == (1008, 704); n += 1
    assert m.plan_latent(1000, 700, 1, "flux 16ch /8", "32", "down")[1:3] == (992, 672); n += 1
    assert m.plan_latent(1000, 700, 1, "flux 16ch /8", "32", "up")[1:3] == (1024, 704); n += 1
    assert m.plan_latent(8, 8, 1, "standard 4ch /8", "64", "up")[1:3] == (64, 64); n += 1  # never below one step
    assert m.plan_latent(16384, 16384, 1, "standard 4ch /8", "64", "up")[1:3] == (16384, 16384); n += 1
    assert m.plan_latent(16380, 16380, 1, "standard 4ch /8", "64", "up")[1:3] == (16384, 16384); n += 1
    assert "Warning: 16.8 MP is large" in m.plan_latent(4096, 4096, 1, "standard 4ch /8")[3]; n += 1
    assert "pictures at once" in m.plan_latent(2048, 2048, 4, "standard 4ch /8")[3]; n += 1
    assert "pictures at once" not in m.plan_latent(512, 512, 4, "standard 4ch /8")[3]; n += 1
    assert m.plan_latent(1024, 512, 2, "flux 16ch /8")[0] == (2, 16, 64, 128); n += 1
    assert _plan_raises(0, 512, 1, "standard 4ch /8", "64"); n += 1
    assert _plan_raises(512, 512, 1, "standard 4ch /8", "100"); n += 1
    assert _plan_raises(512, 512, 1, "standard 4ch /8", "16", "sideways"); n += 1
    assert _plan_raises(512, 512, 0, "standard 4ch /8", "16"); n += 1
    assert _plan_raises(512, 512, 1, "nope", "16"); n += 1
    spec = m.SYEmptyLatent.INPUT_TYPES()
    assert list(spec["required"]) == ["width", "height", "batch", "latent_type"] and list(spec["optional"]) == ["snap_to", "snap_direction"]; n += 1
    assert spec["optional"]["snap_to"][1]["default"] == "off" and spec["optional"]["snap_direction"][1]["default"] == "nearest"; n += 1
    return n
