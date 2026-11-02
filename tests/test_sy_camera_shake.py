import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_camera_shake as m


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit("camera shake: " + msg)

    a = m.shake_offsets(30, 6.0, 0.4, 1.0, 7)
    b = m.shake_offsets(30, 6.0, 0.4, 1.0, 7)
    c = m.shake_offsets(30, 6.0, 0.4, 1.0, 8)
    ok(len(a) == 30 and a == b, "same seed same shake")
    ok(a != c, "other seed other shake")
    ok(all(abs(dx) <= 6.0 and abs(dy) <= 6.0 and abs(ang) <= 0.4 for dx, dy, ang in a), "within limits")
    ok(any(abs(dx) > 0.5 for dx, _, _ in a), "it really moves")
    ok(max(abs(a[i + 1][0] - a[i][0]) for i in range(29)) < 6.0, "smooth, no jumps")
    z = m.shake_offsets(10, 0.0, 0.0, 1.0, 1)
    ok(all(t == (0.0, 0.0, 0.0) for t in z), "zero strength is still")
    ok(len(m.shake_offsets(1, 3.0, 1.0, 2.0, 0)) == 1, "single frame")
    fast = m.shake_offsets(40, 6.0, 0.4, 4.0, 3)
    slow = m.shake_offsets(40, 6.0, 0.4, 0.25, 3)
    ok(sum(abs(fast[i + 1][0] - fast[i][0]) for i in range(39)) > sum(abs(slow[i + 1][0] - slow[i][0]) for i in range(39)), "speed changes wobble")
    ok(raises(m.shake_offsets, 0, 6.0, 0.4, 1.0, 0), "no frames")
    ok(raises(m.shake_offsets, 5, -1.0, 0.4, 1.0, 0), "negative strength")
    ok(raises(m.shake_offsets, 5, 1.0, 0.4, 0.0, 0), "zero speed")
    ok(raises(m.check_edge, "wrap"), "bad edge")
    ok(m.crop_zoom_factor(100, 100, 0.0, 0.0) == 1.0, "no zoom when still")
    ok(m.crop_zoom_factor(100, 100, 6.0, 0.4) > 1.12, "zoom covers shift")
    th = m.shake_theta(0.0, 0.0, 0.0, 100, 50, 1.0)
    ok(th == [[1.0, -0.0, 0.0], [0.0, 1.0, 0.0]], "identity matrix")
    ok(abs(m.shake_theta(10.0, -5.0, 0.0, 100, 50)[0][2] - 0.2) < 1e-9 and abs(m.shake_theta(10.0, -5.0, 0.0, 100, 50)[1][2] + 0.2) < 1e-9, "shift in unit coordinates")
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYCameraShake"] == "Camera Shake SY", "display name")

    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        g = torch.linspace(0, 1, 32).view(1, 1, 32, 1).expand(6, 24, 32, 3).contiguous()
        node = m.SYCameraShake()
        for edge in m.EDGES:
            out, info = node.run(g, 4.0, 1.0, 1.0, 5, edge)
            ok(out.shape == g.shape and out.dtype == g.dtype, "shape " + edge)
            ok(float(out.min()) >= 0.0 and float(out.max()) <= 1.0, "range " + edge)
            ok(not torch.equal(out, g), "changed " + edge)
        o1, _ = node.run(g, 4.0, 1.0, 1.0, 5, "reflect")
        o2, _ = node.run(g, 4.0, 1.0, 1.0, 5, "reflect")
        ok(torch.equal(o1, o2), "repeatable")
        still, _ = node.run(g, 0.0, 0.0, 1.0, 5, "reflect")
        ok(torch.allclose(still, g, atol=1e-5), "zero shake keeps the picture")
        try:
            node.run(g, 4.0, 1.0, 1.0, 5, "wrap")
            ok(False, "should raise")
        except ValueError:
            ok(True)
    return n
