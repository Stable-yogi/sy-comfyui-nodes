import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_with_caption as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.caption_list("a cat", 3) == ["a cat"] * 3; n += 1
    assert m.caption_list("x", 1) == ["x"]; n += 1
    assert raises(m.caption_list, "   ", 1); n += 1
    assert raises(m.caption_list, "x", 0); n += 1
    assert m.SYSaveWithCaption.OUTPUT_NODE is True; n += 1
    # --- value pass A2: trigger word, tag cleaning, one line per picture
    assert m.clean_caption("a cat ,, a  Cat,  sitting ,") == "a cat, sitting"; n += 1
    assert m.clean_caption("line one\nline two") == "line one line two"; n += 1
    assert m.apply_trigger("a cat, sks, sitting", "SKS") == "SKS, a cat, sitting"; n += 1
    assert m.apply_trigger("a cat", "") == "a cat" and m.apply_trigger("", "sks") == "sks"; n += 2
    assert m.apply_trigger("a cat", " sks, ") == "sks, a cat"; n += 1
    assert m.caption_list("a cat,  a cat", 2, "same for all", "sks", True) == ["sks, a cat"] * 2; n += 1
    assert m.caption_list("one\n\ntwo\n", 2, "one line per picture") == ["one", "two"]; n += 1
    assert m.caption_list("one", 3, "one line per picture") == ["one"] * 3; n += 1
    assert raises(m.caption_list, "a\nb\nc", 2, "one line per picture"); n += 1
    assert raises(m.caption_list, "a", 2, "per magic"); n += 1
    assert raises(m.caption_list, "  ", 2, "one line per picture"); n += 1
    assert raises(m.caption_list, " , ", 1, "same for all", "", True); n += 1
    assert m.caption_list("", 2, "same for all", "sks") == ["sks", "sks"]; n += 1
    ui = [{"filename": "a.png", "subfolder": "SY/dataset"}]
    assert m.save_info(ui, ["sks, a cat sitting"]) == "Saved 1 picture and 1 caption file to SY/dataset (longest caption: 4 words)."; n += 1
    assert "cut short" in m.save_info(ui, ["w " * 200]); n += 1
    assert m.SYSaveWithCaption.RETURN_NAMES == ("saved_paths", "info", "caption_used") and len(m.SYSaveWithCaption.RETURN_TYPES) == 3; n += 1
    assert set(m.SYSaveWithCaption.INPUT_TYPES()["optional"]) == {"caption_mode", "trigger_word", "clean_tags"}; n += 1
    return n
