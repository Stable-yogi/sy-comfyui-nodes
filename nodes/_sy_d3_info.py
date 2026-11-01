"""Plain-word text helpers for the Image nodes' info outputs (batch D3). Pure Python, no torch, no node class."""
from math import gcd

COMMON_RATIOS = ((1, 1), (5, 4), (4, 3), (3, 2), (16, 10), (16, 9), (21, 9), (2, 1), (3, 1),
                 (4, 5), (3, 4), (2, 3), (10, 16), (9, 16), (9, 21), (1, 2), (1, 3))


def size_text(width, height):
    """'1024x768'."""
    return "%dx%d" % (int(width), int(height))


def percent(part, total):
    """Share of `part` in `total` as a percent 0..100. An empty total gives 0."""
    if total <= 0:
        return 0.0
    return 100.0 * float(part) / float(total)


def pct_text(part, total):
    """'12.5%'."""
    return "%.1f%%" % percent(part, total)


def plural(n, word):
    """'1 frame', '3 frames'."""
    n = int(n)
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def ratio_text(width, height):
    """Plain shape of a picture: a well known ratio like 16:9 when it is within 1.5 percent, otherwise 'about 1.37:1'."""
    width = int(width)
    height = int(height)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1 (got %dx%d)" % (width, height))
    r = width / float(height)
    best = None
    for a, b in COMMON_RATIOS:
        err = abs(r - a / float(b)) / (a / float(b))
        if err <= 0.015 and (best is None or err < best[0]):
            best = (err, a, b)
    if best is not None:
        return "%d:%d" % (best[1], best[2])
    g = gcd(width, height)
    if width // g <= 32 and height // g <= 32:
        return "%d:%d" % (width // g, height // g)
    return "about %.2f:1" % r


def need_nonempty(shape, what="picture"):
    """Pure function. Plain refusal when a batch has no pictures. shape is the tensor shape."""
    dims = tuple(int(v) for v in shape)
    if len(dims) == 4 and dims[0] < 1:
        raise ValueError("the %s batch is empty: connect at least 1 picture" % what)
    if len(dims) == 4 and min(dims) < 1:
        raise ValueError("the %s batch has a zero size %s: check the node before this one" % (what, dims))
