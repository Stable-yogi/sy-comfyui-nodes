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
    assert m.SYMultiRefLabel.RETURN_TYPES == ("STRING", "INT", "STRING")
    assert m.label_refs(["a man", "", "a hat"], "T", "Picture")[0] == "Picture 1: a man\nPicture 3: a hat\n\nT"
    assert m.label_refs(["a man", "", "a hat"], "T", renumber=True)[0] == "Image 1: a man\nImage 2: a hat\n\nT"
    assert m.label_refs(["a man"], "T", task_first=True)[0] == "T\n\nImage 1: a man"
    assert m.label_refs(["a"], "t", "  ")[0].startswith("Image 1: a")
    assert _raises(["a"], "t") is False
    assert m.refs_info(["a man", "", "a hat"], "Move Image 1") == "2 references labelled: Image 1, Image 3."
    assert m.refs_info(["a man"], "x") == "1 reference labelled: Image 1."
    assert m.refs_info(["a man"], "Put Image 2 on image 1 and Image 3") == "1 reference labelled: Image 1. WARNING: the task names Image 2, Image 3, which has no description."
    assert m.refs_info(["", "b"], "x", renumber=True) == "1 reference labelled: Image 1."
    out = m.SYMultiRefLabel().run("Use Image 2", "a", "", "c", "", "Image", False, True)
    assert out[1] == 2 and out[2].startswith("2 references labelled: Image 1, Image 2.") and "WARNING" not in out[2]
    assert m.SYMultiRefLabel().run("t", "a")[0] == "Image 1: a\n\nt"
    assert m.SYMultiRefLabel.RETURN_NAMES == ("prompt", "ref_count", "info")
    return 22  # checks
