import base64
import json
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_scene3d as h
import sy_scene3d as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise AssertionError("expected ValueError")


def tiny_png_b64():
    """A real 2x1 gray PNG made with the standard library only: one white pixel, one black pixel."""
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    raw = b"\x00\xff\x00"
    png = (h.PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    return base64.b64encode(png).decode("ascii")


def scene_text(*kinds):
    return json.dumps({"camera": {"yaw": 1.0, "pitch": 0.3, "dist": 7},
                       "objects": [{"id": i + 1, "kind": k, "x": i, "y": 0, "z": -i, "scale": 1.5} for i, k in enumerate(kinds)]})


def run():
    n = 0
    # summary
    assert h.summarize(h.default_scene()) == "empty scene"; n += 1
    assert h.summary_from_text("") == "empty scene"; n += 1
    assert h.summary_from_text(scene_text("cube")) == "1 object: cube"; n += 1
    assert h.summary_from_text(scene_text("cube", "sphere", "plane")) == "3 objects: cube, sphere, plane"; n += 1
    assert h.summary_from_text(scene_text("cylinder", "cylinder")) == "2 objects: cylinder, cylinder"; n += 1
    # parse
    sc = h.parse_scene(scene_text("cube", "sphere"))
    assert sc["camera"] == {"yaw": 1.0, "pitch": 0.3, "dist": 7.0}; n += 1
    assert sc["objects"][1]["x"] == 1.0 and sc["objects"][1]["z"] == -1.0 and sc["objects"][1]["scale"] == 1.5; n += 1
    assert h.parse_scene("   ") == h.default_scene(); n += 1
    assert h.parse_scene('{"objects": [{"kind": "plane"}]}')["objects"][0]["scale"] == 1.0; n += 1
    assert h.parse_scene('{"objects": [{"kind": "plane"}]}')["camera"] == h.DEFAULT_CAMERA; n += 1
    assert h.parse_scene('{"objects": [{"kind": "cube"}]}')["objects"][0]["id"] == 1; n += 1
    # parse errors are plain words
    assert "JSON" in raises(h.parse_scene, "{not json"); n += 1
    assert "object" in raises(h.parse_scene, "[1, 2]"); n += 1
    assert "list" in raises(h.parse_scene, '{"objects": 5}'); n += 1
    assert "camera" in raises(h.parse_scene, '{"camera": 3}'); n += 1
    assert "kind" in raises(h.parse_scene, '{"objects": [{"kind": "torus"}]}'); n += 1
    assert "object 1" in raises(h.parse_scene, '{"objects": [7]}'); n += 1
    assert "number" in raises(h.parse_scene, '{"objects": [{"kind": "cube", "x": "left"}]}'); n += 1
    assert "number" in raises(h.parse_scene, '{"objects": [{"kind": "cube", "x": true}]}'); n += 1
    assert "between" in raises(h.parse_scene, '{"objects": [{"kind": "cube", "x": 1000}]}'); n += 1
    assert "between" in raises(h.parse_scene, '{"objects": [{"kind": "cube", "scale": 0}]}'); n += 1
    assert "usable" in raises(h.parse_scene, '{"objects": [{"kind": "cube", "x": NaN}]}'); n += 1
    assert "between" in raises(h.parse_scene, '{"camera": {"dist": 0.1}}'); n += 1
    many = json.dumps({"objects": [{"kind": "cube"}] * (h.MAX_OBJECTS + 1)})
    assert "more than" in raises(h.parse_scene, many); n += 1
    # strip / decode
    assert h.strip_data_url("data:image/png;base64, AB CD\n") == "ABCD"; n += 1
    assert h.strip_data_url("") == "" and h.strip_data_url(None) == ""; n += 1
    assert "comma" in raises(h.strip_data_url, "data:image/png;base64"); n += 1
    assert h.decode_png_bytes("") == b"" and h.decode_png_bytes("  ") == b""; n += 1
    b64 = tiny_png_b64()
    assert h.decode_png_bytes(b64).startswith(h.PNG_SIGNATURE); n += 1
    assert h.decode_png_bytes("data:image/png;base64," + b64) == h.decode_png_bytes(b64); n += 1
    assert "base64" in raises(h.decode_png_bytes, "not*base64!!"); n += 1
    assert "PNG" in raises(h.decode_png_bytes, base64.b64encode(b"hello world").decode()); n += 1
    assert "depth" in raises(h.decode_png_bytes, "not*base64!!", "depth picture"); n += 1
    # size
    assert h.check_size(768, 64) == (768, 64); n += 1
    raises(h.check_size, 63, 768); n += 1
    raises(h.check_size, 768, 2049); n += 1
    # node shape
    spec = m.SYScene3D.INPUT_TYPES()["required"]
    assert list(spec) == ["scene_json", "render_data", "depth_data", "width", "height"]; n += 1
    assert spec["scene_json"][1]["multiline"] is False and spec["depth_data"][1]["multiline"] is False; n += 1
    assert spec["width"][1]["default"] == 768 and spec["height"][1]["default"] == 768; n += 1
    assert spec["width"][1]["min"] == 64 and spec["width"][1]["max"] == 2048; n += 1
    assert m.SYScene3D.RETURN_TYPES == ("IMAGE", "IMAGE", "STRING"); n += 1
    assert m.SYScene3D.CATEGORY == "SY/Editors"; n += 1
    assert m.NODE_CLASS_MAPPINGS["SYScene3D"] is m.SYScene3D; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYScene3D"] == "3D Scene SY"; n += 1
    # PIL part (only where PIL exists; the plain selftest python has none)
    try:
        import PIL  # noqa: F401
    except ImportError:
        return n
    im = m.load_picture(b64, 2, 1, "shaded picture")
    assert im.size == (2, 1) and im.getpixel((0, 0)) == (255, 255, 255) and im.getpixel((1, 0)) == (0, 0, 0); n += 1
    big = m.load_picture(b64, 8, 4, "shaded picture")
    assert big.size == (8, 4); n += 1
    assert m.load_picture("", 8, 4, "x") is None; n += 1
    return n
