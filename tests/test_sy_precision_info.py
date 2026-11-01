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
    # --- value pass A2: fit check against the card memory
    f = m.fit_text(12, m.ALL, 24)
    assert "fp8" in f and "Q4_K_M (gguf)" in f and "fp32" not in f.split("Best")[0] and "Best quality that fits: Q8_0 (gguf)" in f; n += 1
    assert m.fit_text(12, "fp16", 48).startswith("fp16 fits in 48 GB"); n += 1
    no = m.fit_text(12, "fp16", 24)
    assert "does NOT fit" in no and "4.8 GB too much" in no and "Largest format that fits: Q8_0" in no; n += 1
    assert "Type your graphics card memory" in m.fit_text(12, "fp16", 0); n += 1
    assert m.fit_text(1000, m.ALL, 8).startswith("Nothing fits"); n += 1
    assert "No format fits" in m.fit_text(1000, "fp8", 8); n += 1
    for bad in (lambda: m.fit_text(12, "fp16", -1), lambda: m.fit_text(12, "zzz", 24), lambda: m.fit_text(0, "fp16", 24)):
        try:
            bad()
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    out3 = m.SYPrecisionInfo().run(7.0, "fp8", 24.0)
    assert len(out3) == 3 and out3[1] == 7.0 and "fits in 24 GB" in out3[2]; n += 1
    assert m.SYPrecisionInfo.RETURN_NAMES == ("text", "size_gb", "fit"); n += 1
    assert m.SYPrecisionInfo().run(12.0, m.ALL)[2].startswith("No card size"); n += 1
    return n
