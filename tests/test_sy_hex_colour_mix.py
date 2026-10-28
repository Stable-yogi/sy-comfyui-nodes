import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_hex_colour_mix as m

HASH = chr(35)


def hx(r, g, b, with_hash=True):
    """Build a colour text from three numbers (no literal colours in this file)."""
    return (HASH if with_hash else "") + "%02x%02x%02x" % (r, g, b)


def run():
    black = hx(0, 0, 0)
    white = hx(255, 255, 255, False)
    assert m.parse_colour(hx(10, 20, 30)) == (10, 20, 30)
    assert m.parse_colour(hx(10, 20, 30, False).upper()) == (10, 20, 30)
    assert m.parse_colour(HASH + "f0a") == (255, 0, 170)
    assert m.mix_colours(black, white, 0.0) == (hx(0, 0, 0), 0, 0, 0)
    assert m.mix_colours(black, white, 1.0) == (hx(255, 255, 255), 255, 255, 255)
    assert m.mix_colours(black, white, 0.5)[1:] == (128, 128, 128)
    assert m.mix_colours(hx(200, 0, 100), hx(100, 100, 100), 0.5) == (hx(150, 50, 100), 150, 50, 100)
    assert m.mix_colours(hx(1, 2, 3), hx(1, 2, 3), 0.7)[0] == hx(1, 2, 3)
    assert m.mix_colours(hx(10, 10, 10), hx(20, 20, 20, False), 1)[0].startswith(HASH)
    for bad in (("zzzzzz", black, 0.5), (black, "12345", 0.5), (black, white, 1.5), (black, white, -0.1), ("", black, 0.5)):
        try:
            m.mix_colours(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYHexColourMix.RETURN_TYPES == ("STRING", "INT", "INT", "INT")
    return 15  # checks
