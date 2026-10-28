import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_swatch as m


def run():
    assert m.parse_colour("#d4a537") == (212, 165, 55)
    assert m.parse_colour("d4a537") == (212, 165, 55)
    assert m.parse_colour("  #D4A537 ") == (212, 165, 55)
    assert m.parse_colour("#fa0") == (255, 170, 0)
    assert m.parse_colour("000") == (0, 0, 0)
    assert m.normalise_colour((212, 165, 55)) == "#d4a537"
    assert m.normalise_colour(m.parse_colour("FFF")) == "#ffffff"
    for bad in ("", "#", "12345", "#gggggg", "d4a53", "#d4a5377"):
        try:
            m.parse_colour(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    assert m.SWATCH_SIZE == 64
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYColourSwatch"] == "Colour Swatch SY"
    return 14
