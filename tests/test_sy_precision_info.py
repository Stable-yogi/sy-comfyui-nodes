import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_precision_info as m


def run():
    n = 0
    assert m.size_gb(12, "fp16") == 24.0
    assert m.size_gb(12, "fp32") == 48.0
    assert m.size_gb(12, "fp8") == 12.0
    assert m.size_gb(12, "nf4") == 6.0
    n += 4
    t = m.table_text(7, m.ALL)
    assert "fp16" in t and "bf16" in t and "Q4_K_M (gguf)" in t and "7 billion" in t
    assert m.table_text(7, "fp8").count("\n") == 1
    n += 2
    for name, (bpp, note) in m.PRECISIONS.items():
        assert 0 < bpp <= 8 and note
        n += 1
    for bad in (lambda: m.size_gb(0, "fp16"), lambda: m.size_gb(1, "zzz")):
        try:
            bad()
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    out = m.SYPrecisionInfo().run(12.0, m.ALL)
    assert out[1] == 24.0
    n += 1
    return n
