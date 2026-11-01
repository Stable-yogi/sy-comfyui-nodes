import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ltx_latent_bridge as m


def raises(*args, **kw):
    try:
        m.plan_bridge(*args, **kw)
    except ValueError:
        return True
    return False


def run():
    n = 0
    p = m.plan_bridge
    # a good clip is only rounded to the multiple, frames kept
    w, h, ids, note = p(1280, 704, 73)
    assert (w, h) == (1280, 704) and ids == list(range(73)) and "kept" in note; n += 1
    # size is rounded to 32
    w, h, ids, _ = p(1280, 720, 73)
    assert (w, h) == (1280, 736) or (w, h) == (1280, 704); n += 1
    assert w % 32 == 0 and h % 32 == 0; n += 1
    # trim cuts to the lower 8n+1, pad repeats the last frame up, nearest picks the closest
    assert p(640, 640, 75, policy="trim")[2] == list(range(73)); n += 1
    pad = p(640, 640, 75, policy="pad")[2]
    assert len(pad) == 81 and pad[:75] == list(range(75)) and set(pad[75:]) == {74}; n += 1
    assert len(p(640, 640, 75, policy="nearest")[2]) == 73; n += 1
    assert len(p(640, 640, 78, policy="nearest")[2]) == 81; n += 1
    # exact refuses a wrong count and says what to use
    assert raises(640, 640, 75, policy="exact"); n += 1
    assert len(p(640, 640, 73, policy="exact")[2]) == 73; n += 1
    # a very short clip: 5 frames trimmed gives 1
    assert p(64, 64, 5, policy="trim")[2] == [0]; n += 1
    # budget lowers the size and stays on the multiple
    w, h, _, note = p(1920, 1080, 9, max_megapixels=0.5)
    assert w * h <= 500000 and w % 32 == 0 and h % 32 == 0 and "->" in note; n += 1
    # bad input
    assert raises(0, 64, 9); n += 1
    assert raises(64, 64, 0); n += 1
    assert raises(64, 64, 9, policy="nonsense"); n += 1
    assert raises(64, 64, 9, frame_step=0); n += 1
    # the node itself, when torch is there
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        class Vae:
            def encode(self, x):
                b, hh, ww, c = x.shape
                return torch.zeros(1, 128, (b - 1) // 8 + 1, hh // 32, ww // 32)
        imgs = torch.rand(75, 100, 150, 4)
        lat, frames, count, w, h, info = m.SYLtxLatentBridge().run(imgs, Vae(), "trim", "stretch")
        assert count == 73 and frames.shape == (73, 96, 160, 3) and (w, h) == (160, 96); n += 1
        assert lat["samples"].shape == (1, 128, 10, 3, 5) and "75 -> 73" in info; n += 1
        _, fc, _, w2, h2, _ = m.SYLtxLatentBridge().run(imgs, Vae(), "trim", "crop")
        assert fc.shape == (73, 96, 160, 3) and float(fc.min()) >= 0.0 and float(fc.max()) <= 1.0; n += 1
    cls = m.SYLtxLatentBridge
    req = cls.INPUT_TYPES()
    assert cls.DESCRIPTION and m.NODE_DISPLAY_NAME_MAPPINGS["SYLtxLatentBridge"] == "LTX Latent Bridge SY"; n += 1
    return n
