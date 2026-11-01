import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_caption_prefix_suffix as m


def run():
    f = m.add_prefix_suffix
    assert f("a dog on grass", "sks", "", ", ") == "sks, a dog on grass"
    assert f("a dog on grass", "", "high quality", ", ") == "a dog on grass, high quality"
    assert f("a dog", "sks", "hq", ", ") == "sks, a dog, hq"
    assert f("sks, a dog", "sks", "hq", ", ") == "sks, a dog, hq"                 # prefix already there
    assert f("SKS, a dog", "sks", "", ", ") == "SKS, a dog"                       # ignores upper/lower case
    assert f("a dog, hq", "", "hq", ", ") == "a dog, hq"                          # suffix already there
    assert f("a dog, hq.", "", "hq", ", ") == "a dog, hq."                        # trailing dot ignored
    assert f("a dog,", "", "hq", ", ") == "a dog, hq"                             # no double comma
    assert f("sks", "sks", "sks", ", ") == "sks"                                  # same word both places
    assert f("sksfoo bar", "sks", "", ", ") == "sks, sksfoo bar"                  # only whole words count
    assert f("a dog", "sks", "", " ") == "sks a dog"                              # other separator
    assert f("", "sks", "hq", ", ") == "sks, hq"                                  # empty caption
    assert f("", "", "", ", ") == ""
    assert f("  a dog  ", " sks, ", " ,hq ", ", ") == "sks, a dog, hq"            # tags are cleaned
    assert f("a dog", "", "", ", ") == "a dog"
    assert f("photo of sks man", "photo of sks", "", ", ") == "photo of sks man"  # phrase prefix, then a space
    assert f("a dog with hq", "", "hq", ", ") == "a dog with hq"                  # ends with whole word
    assert f("a dog with xhq", "", "hq", ", ") == "a dog with xhq, hq"            # but not part of a word
    text = "a dog\n\nsks, a cat\n"
    assert m.apply_to_text(text, "sks", "hq", ", ", True) == "sks, a dog, hq\n\nsks, a cat, hq\n"
    assert m.apply_to_text("a dog\nb", "sks", "", ", ", False) == "sks, a dog\nb"
    assert m.SYCaptionPrefixSuffix().run("x", "p", "s", ", ", False)[0] == "p, x, s"
    # value pass C1: tidy option and info line
    assert m.tidy_caption("a  dog ,, on   grass ,") == "a dog, on grass,"
    assert m.tidy_caption("  a \n\n b  ") == "a\n\nb"
    assert m.tidy_caption(None) == ""
    t, i = m.apply_with_info("a  dog ,, x", "sks", "", ", ", False, True)
    assert t == "sks, a dog, x" and "prefix added to 1, already there in 0" in i
    t, i = m.apply_with_info("sks, a dog", "sks", "hq", ", ")
    assert t == "sks, a dog, hq" and "prefix added to 0, already there in 1" in i and "suffix added to 1" in i
    t, i = m.apply_with_info("a\n\nsks, b", "sks", "", ", ", True)
    assert t == "sks, a\n\nsks, b" and i.startswith("2 captions:") and "prefix added to 1, already there in 1" in i
    assert m.apply_with_info("x", "", "", ", ")[1] == "Nothing to add: prefix and suffix are both empty."
    assert m.apply_with_info("a hq", "", "hq", ", ")[1].endswith("suffix added to 0, already there in 1.")
    assert m.SYCaptionPrefixSuffix().run("x", "p", "s", ", ", False) == ("p, x, s", "1 caption: prefix added to 1, already there in 0; suffix added to 1, already there in 0.")
    assert m.SYCaptionPrefixSuffix.RETURN_NAMES == ("caption", "info")
    return 30
