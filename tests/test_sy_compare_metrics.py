import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_compare_metrics as m


def run():
    n = 0
    assert m.mean_abs_diff([0, 0, 0], [0, 0, 0]) == 0.0
    n += 1
    assert abs(m.mean_abs_diff([0, 1], [1, 0]) - 1.0) < 1e-9
    n += 1
    assert abs(m.mean_abs_diff([0.5, 0.5], [0.25, 0.75]) - 0.25) < 1e-9
    n += 1
    assert m.mean_abs_diff([], []) == 0.0
    n += 1
    try:
        m.mean_abs_diff([1], [1, 2])
        raise SystemExit("length mismatch must raise")
    except ValueError:
        n += 1
    assert m.check_same_shape((1, 4, 4, 3), [1, 4, 4, 3]) == (1, 4, 4, 3)
    n += 1
    try:
        m.check_same_shape((1, 4, 4, 3), (1, 4, 5, 3))
        raise SystemExit("size mismatch must raise")
    except ValueError as e:
        assert "same size" in str(e)
        n += 1
    assert m.amplify_clamp(0.1, 4.0) == 0.4
    n += 1
    assert m.amplify_clamp(0.5, 4.0) == 1.0
    n += 1
    assert m.amplify_clamp(0.3, 0.0) == 0.0
    n += 1
    try:
        import torch
    except Exception:
        return n  # tensor path skipped: torch not installed
    a = torch.zeros(2, 4, 4, 3)
    b = torch.full((2, 4, 4, 3), 0.1)
    score, img, top, psnr, info = m.SYCompareMetrics().run(a, b, 4.0)
    assert abs(score - 0.1) < 1e-6
    n += 1
    assert img.shape == a.shape and abs(float(img.max()) - 0.4) < 1e-6
    n += 1
    assert abs(top - 0.1) < 1e-6 and abs(psnr - 20.0) < 1e-4 and "PSNR" in info
    n += 1
    try:
        m.SYCompareMetrics().run(a, torch.zeros(2, 4, 5, 3))
        raise SystemExit("tensor size mismatch must raise")
    except ValueError:
        n += 1
    assert m.psnr_from_mean_sq(0.0) == 99.0; n += 1
    assert abs(m.psnr_from_mean_sq(0.01) - 20.0) < 1e-9; n += 1
    assert abs(m.psnr_from_mean_sq(1.0)) < 1e-9; n += 1
    assert m.psnr_from_mean_sq(1e-20) == 99.0; n += 1
    try:
        m.psnr_from_mean_sq(-1.0)
        raise SystemExit("expected ValueError")
    except ValueError:
        n += 1
    assert m.verdict(0.0) == "identical" and m.verdict(0.005) == "almost identical"; n += 1
    assert m.verdict(0.03) == "small differences" and m.verdict(0.1) == "clear differences" and m.verdict(0.5) == "very different"; n += 1
    assert m.SYCompareMetrics.RETURN_NAMES == ("diff_score", "diff_image", "max_diff", "psnr", "info"); n += 1
    assert list(m.SYCompareMetrics.INPUT_TYPES()["optional"]) == ["mask", "resize_b"]; n += 1
    return n
