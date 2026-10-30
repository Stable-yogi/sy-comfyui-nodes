import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_latent_upscaler as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def near(a, b):
    return len(a) == len(b) and all(abs(x - y) < 1e-9 for x, y in zip(a, b))


def run():
    n = 0
    assert m.plan_target(40, 22, "scale by multiplier", scale=1.5) == (60, 32, 1.5); n += 1
    assert m.plan_target(40, 22, "scale by multiplier", scale=1.0) == (40, 22, 1.0); n += 1
    assert m.plan_target(40, 22, "target dimensions", width=1280, height=704) == (80, 44, 2.0); n += 1
    w, h, eff = m.plan_target(40, 22, "megapixels", megapixels=1.0)
    assert (w * 16) % 32 == 0 and (h * 16) % 32 == 0 and w > 40 and h > 22 and eff > 1.0; n += 1
    w, h, _ = m.plan_target(40, 22, "scale by multiplier", scale=2.0, align=1)
    assert (w, h) == (80, 44); n += 1
    assert raises(m.plan_target, 40, 22, "target dimensions", width=320, height=176); n += 1
    assert raises(m.plan_target, 40, 22, "zoom"); n += 1
    assert raises(m.plan_target, 0, 22, "scale by multiplier"); n += 1
    ranges = m.chunk_ranges(70, 5)
    assert ranges == [(0, 32, 0, 37, 0, 42), (32, 64, 27, 69, 22, 74), (64, 70, 59, 70, 54, 75)], ranges; n += 1
    assert m.chunk_ranges(20, 5) == [(0, 20, 0, 20, 0, 25)]; n += 1
    covered = set()
    for _s0, _s1, o0, o1, _lo, _hi in ranges:
        covered.update(range(o0, o1))
    assert covered == set(range(70)); n += 1
    assert near(m.blend_weights(4, 0, 0), [1, 1, 1, 1]); n += 1
    assert near(m.blend_weights(5, 2, 2), [1 / 3, 2 / 3, 1, 2 / 3, 1 / 3]); n += 1
    assert near(m.blend_weights(3, 0, 2), [1, 2 / 3, 1 / 3]); n += 1
    shapes = {"conv_in.weight": (512, 24, 3, 3, 3), "in_blocks.0.in_layers.0.weight": (512,),
              "in_blocks.1.dwconv.weight": (512, 1, 5, 1, 1), "in_blocks.2.in_layers.0.weight": (512,),
              "out_blocks.0.in_layers.0.weight": (512,)}
    cfg = m.detect_arch(shapes)
    assert cfg["channels"] == 512 and cfg["in_channels"] == 24 and cfg["in_blocks"] == 2 and cfg["out_blocks"] == 1; n += 1
    assert cfg["temporal_every"] == 2 and cfg["temporal_kernel"] == 5; n += 1
    assert m.detect_arch({"conv_in.weight": (64, 24, 3, 3, 3)})["temporal_every"] == 0; n += 1
    assert len(m.LATENTS_MEAN) == 24 and len(m.LATENTS_STD) == 24; n += 1
    cls = m.SYH3LatentUpscaler
    assert cls.RETURN_TYPES == ("LATENT",) and cls.CATEGORY == "SY/Resize"; n += 1
    assert m.NODE_CLASS_MAPPINGS == {"SYH3LatentUpscaler": cls}; n += 1
    return n
