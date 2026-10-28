import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_square_crop_train as m


def run():
    assert m.centre_square(100, 100) == (0, 0, 100)
    assert m.centre_square(200, 100) == (50, 0, 100)
    assert m.centre_square(100, 200) == (0, 50, 100)
    assert m.centre_square(101, 100) == (0, 0, 100)             # odd leftover: extra pixel is cut from the right
    assert m.centre_square(105, 100) == (2, 0, 100)
    assert m.centre_square(1, 1) == (0, 0, 1)
    assert m.centre_square(1, 7) == (0, 3, 1)
    for bad in ((0, 5), (5, 0), (-1, 5)):
        try:
            m.centre_square(*bad)
            raise SystemExit("bad size must raise")
        except ValueError:
            pass
    assert m.METHODS[0] == "area"
    assert m.SYSquareCropTrain.RETURN_TYPES == ("IMAGE",)
    return 12
