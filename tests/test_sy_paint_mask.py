import base64
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_paint_mask as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise AssertionError("expected ValueError")


def tiny_png_b64():
    """A real 2x2 PNG made with the standard library only: left column white, right column black."""
    import struct
    import zlib

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    raw = b"\x00\xff\x00" + b"\x00\xff\x00"  # filter byte + 2 gray pixels per row
    png = (m.PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    return base64.b64encode(png).decode("ascii")


def run():
    n = 0
    # strip / decode
    assert m.strip_data_url("data:image/png;base64, AB CD\n") == "ABCD"; n += 1
    assert m.strip_data_url("") == "" and m.strip_data_url(None) == ""; n += 1
    assert "comma" in raises(m.strip_data_url, "data:image/png;base64"); n += 1
    assert m.decode_mask_bytes("") == b"" and m.decode_mask_bytes("   ") == b""; n += 1
    b64 = tiny_png_b64()
    assert m.decode_mask_bytes(b64).startswith(m.PNG_SIGNATURE); n += 1
    assert m.decode_mask_bytes("data:image/png;base64," + b64) == m.decode_mask_bytes(b64); n += 1
    assert "base64" in raises(m.decode_mask_bytes, "not*base64!!"); n += 1
    assert "PNG" in raises(m.decode_mask_bytes, base64.b64encode(b"hello world").decode()); n += 1
    # size maths
    assert m.fit_side(512, 256, 1024) == (512, 256); n += 1
    assert m.fit_side(4096, 2048, 1024) == (1024, 512); n += 1
    assert m.fit_side(1000, 4000, 1024) == (256, 1024); n += 1
    assert m.fit_side(1, 5000, 1024) == (1, 1024); n += 1
    raises(m.fit_side, 0, 10, 1024); n += 1
    raises(m.fit_side, 10, 10, 0); n += 1
    # coverage
    assert m.coverage_percent([]) == 0.0; n += 1
    assert m.coverage_percent([[0.0, 0.0], [0.0, 0.0]]) == 0.0; n += 1
    assert m.coverage_percent([[1.0, 1.0], [0.0, 0.0]]) == 50.0; n += 1
    assert abs(m.coverage_percent([[0.25, 0.75]]) - 50.0) < 1e-9; n += 1
    # process order and limits
    box = [[0.0] * 5 for _ in range(5)]
    box[2][2] = 1.0
    same = m.process_mask(box, 0, 0, False)
    assert same == box; n += 1
    grown = m.process_mask(box, 1, 0, False)
    assert grown[2][3] == 1.0 and grown[1][2] == 1.0 and grown[0][0] == 0.0; n += 1
    inv = m.process_mask(box, 0, 0, True)
    assert inv[2][2] == 0.0 and inv[0][0] == 1.0; n += 1
    soft = m.process_mask(box, 0, 1, False)
    assert 0.0 < soft[2][3] < 1.0 and soft[2][2] < 1.0; n += 1
    shrunk = m.process_mask(grown, -1, 0, False)
    assert shrunk[2][2] == 1.0 and shrunk[2][3] == 0.0; n += 1
    raises(m.process_mask, box, 100000, 0, False); n += 1
    raises(m.process_mask, box, 0, -1, False); n += 1
    raises(m.process_mask, box, 0, 100000, False); n += 1
    # node shape
    spec = m.SYPaintMask.INPUT_TYPES()["required"]
    assert set(spec) == {"image", "mask_data", "grow", "feather", "invert"}; n += 1
    assert spec["mask_data"][1]["multiline"] is False; n += 1
    assert m.SYPaintMask.RETURN_TYPES == ("MASK", "IMAGE", "FLOAT"); n += 1
    assert m.SYPaintMask.CATEGORY == "SY/Editors"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPaintMask"] == "Paint Mask SY"; n += 1
    # PIL part (only where PIL exists; the plain selftest python has none)
    try:
        import PIL  # noqa: F401
    except ImportError:
        return n
    rows = m.decode_mask_rows(b64)
    assert rows == [[1.0, 0.0], [1.0, 0.0]]; n += 1
    big = m.decode_mask_rows(b64, 4, 4)
    assert len(big) == 4 and len(big[0]) == 4 and big[0][0] == 1.0 and big[0][3] == 0.0; n += 1
    empty = m.decode_mask_rows("", 3, 2)
    assert empty == [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]; n += 1
    raises(m.decode_mask_rows, "", None, None); n += 1
    return n
