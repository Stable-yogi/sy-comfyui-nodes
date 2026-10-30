import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_preview as m


class TextNode:
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",), "text": ("STRING", {})}, "optional": {"ref": ("IMAGE",)}}

    def run(self, text, image=None, ref=None):
        return (text.upper(), len(text))


class OwnUiNode:
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)

    def run(self):
        return {"ui": {"text": ["x"]}, "result": ("x",)}


class ModelOnly:
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL",)

    def run(self):
        return (object(),)


class ListNode:
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    OUTPUT_IS_LIST = (True,)

    def run(self):
        return (["a"],)


class Broken:
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    def run(self):
        return ("ok",)


def run():
    n = 0
    assert m.clip_text("abc", 10) == "abc"; n += 1
    cut = m.clip_text("x" * 50, 10)
    assert cut.startswith("x" * 10) and "40 more" in cut; n += 1
    assert m.format_value(True) == "True" and m.format_value(False) == "False"; n += 1
    assert m.format_value(1.5) == "1.5" and m.format_value(1 / 3) == "0.333333"; n += 1
    assert m.format_value(7) == "7"; n += 1
    p = m.plan_outputs(("IMAGE", "MASK", "STRING", "INT", "MODEL", "IMAGE"))
    assert p == {"image": 0, "mask": 1, "text": [2, 3]}; n += 1
    assert m.plan_outputs(("MODEL", "CLIP")) == {"image": None, "mask": None, "text": []}; n += 1
    assert m.plan_outputs(None)["text"] == []; n += 1
    assert len(m.plan_outputs(("STRING",) * 9)["text"]) == m.MAX_TEXT_ITEMS; n += 1
    items = m.text_items(m.plan_outputs(("STRING", "INT")), ("text", "count"), ("hi", 3))
    assert items == [{"name": "text", "text": "hi"}, {"name": "count", "text": "3"}]; n += 1
    assert m.text_items({"text": [0]}, None, (None,)) == []; n += 1
    assert m.text_items({"text": [0]}, None, (["a"],)) == []; n += 1
    assert m.text_items({"text": [0, 5]}, ("a",), ("v",)) == [{"name": "a", "text": "v"}]; n += 1
    assert m.can_wrap(TextNode); n += 1
    assert not m.can_wrap(ModelOnly); n += 1
    assert not m.can_wrap(ListNode); n += 1
    assert m.image_input_names(TextNode) == ["image", "ref"]; n += 1
    assert m.image_input_names(ModelOnly) == []; n += 1
    # wrapping keeps the result and adds the ui part
    assert m.wrap_class(TextNode); n += 1
    assert not m.wrap_class(TextNode); n += 1  # second time does nothing
    out = TextNode().run(text="ab")
    assert out["result"] == ("AB", 2); n += 1
    assert out["ui"]["sy_text"][0] == {"name": "text", "text": "AB"}; n += 1
    assert "sy_preview" not in out["ui"]; n += 1
    # a node that returns its own ui is passed through
    assert m.wrap_class(OwnUiNode); n += 1
    assert OwnUiNode().run() == {"ui": {"text": ["x"]}, "result": ("x",)}; n += 1
    # the switch-off variable gives the plain tuple back
    os.environ["SY_NO_PREVIEW"] = "1"
    try:
        assert TextNode().run(text="ab") == ("AB", 2); n += 1
    finally:
        del os.environ["SY_NO_PREVIEW"]
    # a broken preview never breaks the node
    orig = m.add_preview
    m.add_preview = lambda *a, **k: 1 / 0
    try:
        m.wrap_class(Broken)
        assert Broken().run() == ("ok",); n += 1
    finally:
        m.add_preview = orig
    assert m.wrap_all({"A": ModelOnly, "B": ListNode}) == 0; n += 1
    return n
