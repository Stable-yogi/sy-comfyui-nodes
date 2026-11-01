import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_note as m


def run():
    assert m.clean_note(None) == ("", "info")
    assert m.clean_note("hi", "tip") == ("hi", "tip")
    assert m.clean_note("hi", "bogus") == ("hi", "info")
    assert m.clean_note(5, "warning") == ("5", "warning")
    assert m.SYNote().run("abc", "step")[0] == "abc"
    # new: style label, trim, info
    assert m.note_output("  hi \n", "tip") == "  hi \n"                         # plain by default
    assert m.note_output("  hi \n", "tip", trim=True) == "hi"
    assert m.note_output("check seed", "warning", add_style_label=True) == "WARNING: check seed"
    assert m.note_output("x", "bogus", True) == "INFO: x"                        # unknown style becomes info
    assert m.note_output("", "tip", True) == ""                                  # empty note stays empty
    assert m.note_output("  \n ", "tip", True, True) == ""
    assert m.note_output(None, "tip", True) == ""
    assert m.note_output(5, "step", True, True) == "STEP: 5"
    assert m.note_info("one two\n\nthree", "tip") == "Tip note: 2 lines, 3 words, 14 characters."
    assert m.note_info("hi", "model") == "Model note: 1 line, 1 word, 2 characters."
    assert m.note_info("", "warning") == "Empty warning note: nothing to send as a prompt."
    assert m.note_info("   ", "bogus") == "Empty info note: nothing to send as a prompt."
    assert m.SYNote().run("a b", "tip", True, True) == ("TIP: a b", "Tip note: 1 line, 2 words, 3 characters.")
    assert m.SYNote.RETURN_TYPES == ("STRING", "STRING") and m.SYNote.RETURN_NAMES[0] == "text"
    assert list(m.SYNote.INPUT_TYPES()["required"]) == ["text", "style"]
    return 19
