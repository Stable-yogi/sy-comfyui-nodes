import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_moss_layout_prompt as m


def refuses(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    assert m.read_label("text: OPEN LATE | blue shop sign") == ("text", "blue shop sign", "OPEN LATE"); n += 1
    assert m.read_label("Text: SALE") == ("text", "", "SALE"); n += 1
    assert m.read_label("person: a woman in a grey coat") == ("character", "a woman in a grey coat", ""); n += 1
    assert m.read_label("a red bicycle") == ("object", "a red bicycle", ""); n += 1
    assert m.read_label("sign: 10:30 train") == ("object", "sign: 10:30 train", ""); n += 1   # unknown head = object
    assert "needs the words" in refuses(m.read_label, "text:  | look"); n += 1
    # same numbers as the moss-image-prompt skill script (896x1152, 0..1000 box [80,300,200,700])
    assert m.centred_box({"x": 268.8, "y": 92.16, "w": 358.4, "h": 138.24}, 896, 1152) == [-484, -180, -345, 180]; n += 1
    assert m.centred_box({"x": -50, "y": 0, "w": 100, "h": 100}, 1024, 1024) == [-512, -512, -412, -462]; n += 1
    assert m.centred_box({"x": 2000, "y": 0, "w": 10, "h": 10}, 1024, 1024) is None; n += 1
    boxes = json.dumps([{"x": 100, "y": 50, "w": 300, "h": 100, "label": "text: OPEN | neon sign", "colour": "red"},
                        {"x": 500, "y": 300, "w": 400, "h": 700, "label": "person: an old man", "colour": "blue"}])
    p, notes = m.build_layout(boxes, 1024, 1024, "A street at night.")
    d = json.loads(p)
    assert d["bbox_format"] == "yxyx" and d["bbox_coord_space"] == "abs_centralized" and d["summary"]["caption"] == "A street at night."; n += 1
    assert d["items"][0] == {"label": "text", "caption": "neon sign", "text": "OPEN", "bbox": [-462, -412, -362, -112]}; n += 1
    assert d["items"][1]["label"] == "character" and d["items"][1]["bbox"] == [-212, -12, 488, 388] and notes == []; n += 1
    assert m.build_layout("", 512, 512, " just a cat ")[0] == "just a cat"; n += 1
    p, notes = m.build_layout(json.dumps([{"x": 900, "y": 0, "w": 10, "h": 10}]), 512, 512, "x")
    assert p == "x" and "outside" in notes[0]; n += 1
    assert "no number for w" in refuses(m.build_layout, json.dumps([{"x": 0, "y": 0, "h": 5}]), 64, 64, ""); n += 1
    prompt, info = m.SYMossLayoutPrompt().run("A street.", 1024, 1024, boxes)
    assert prompt.startswith('{"summary"') and "2 box(es)" in info; n += 1
    it = m.SYMossLayoutPrompt.INPUT_TYPES()
    assert list(it["required"]) == ["caption", "width", "height"] and "layout_boxes" in it["optional"]; n += 1
    assert "SYMossLayoutPrompt" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYMossLayoutPrompt"].endswith(" SY"); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
