import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_multi_ref_label as m


def _raises(refs, task):
    try:
        m.label_refs(refs, task)
    except ValueError:
        return True
    return False


def run():
    assert m.label_refs(["a man", "", "a hat", ""], "Put the hat from Image 3 on Image 1.") == (
        "Image 1: a man\nImage 3: a hat\n\nPut the hat from Image 3 on Image 1.", 2)
    assert m.label_refs(["a dog"], "Do it")[1] == 1
    assert m.label_refs(["a", "b", "c", "d"], "t")[1] == 4
    assert m.label_refs(["  big   dog "], "t")[0].startswith("Image 1: big dog")
    assert m.label_refs([None, "x"], "t")[0].startswith("Image 2: x")
    assert _raises(["", " ", "", ""], "task")
    assert _raises([], "task")
    assert _raises(["a"], "")
    assert m.SYMultiRefLabel().run("t", "", "b")[1] == 1
    assert m.SYMultiRefLabel.RETURN_TYPES == ("STRING", "INT")
    return 10  # checks
