"""LUT helpers for Apply LUT SY: .cube reader, identity table, built-in looks, plain-Python sampler. Pure Python, no node inside."""
import math

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_SIZE_3D = 65
MAX_SIZE_1D = 16384
BUILTIN_NAMES = ("none", "warm", "cool", "teal and orange", "faded film", "black and white", "high contrast",
                 "sunset glow", "cold moon", "night city", "pastel", "bleach bypass", "vivid", "film stock", "noir")


def _clamp(v):
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def _floats(tokens, line_no, what):
    out = []
    for t in tokens:
        try:
            v = float(t)
        except ValueError:
            raise ValueError("The LUT text, line %d: %s must be numbers, but %r is not a number." % (line_no, what, t))
        if not math.isfinite(v):
            raise ValueError("The LUT text, line %d: %s must be ordinary numbers, but %r is not." % (line_no, what, t))
        out.append(v)
    return out


def parse_cube(text):
    """Read the text of a .cube file. Returns dict(size, domain_min, domain_max, table, kind).
    table is a flat list of floats (three per row), red changes fastest."""
    if not isinstance(text, str):
        raise ValueError("The LUT must be text in the .cube format.")
    if len(text) > MAX_FILE_BYTES:
        raise ValueError("The LUT text is bigger than 20 MB. Use a smaller .cube file.")
    size3 = size1 = None
    dmin = [0.0, 0.0, 0.0]
    dmax = [1.0, 1.0, 1.0]
    table = []
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        tok = line.split()
        key = tok[0].upper()
        if key == "TITLE":
            continue
        if key in ("LUT_3D_SIZE", "LUT_1D_SIZE"):
            if len(tok) != 2:
                raise ValueError("The LUT text, line %d: %s needs one whole number, for example %s 17." % (no, key, key))
            try:
                n = int(tok[1])
            except ValueError:
                raise ValueError("The LUT text, line %d: the size must be a whole number, but %r is not." % (no, tok[1]))
            if key == "LUT_3D_SIZE":
                size3 = n
            else:
                size1 = n
            continue
        if key in ("DOMAIN_MIN", "DOMAIN_MAX"):
            if len(tok) != 4:
                raise ValueError("The LUT text, line %d: %s needs three numbers (red green blue)." % (no, key))
            vals = _floats(tok[1:], no, key)
            if key == "DOMAIN_MIN":
                dmin = vals
            else:
                dmax = vals
            continue
        if key in ("LUT_1D_INPUT_RANGE", "LUT_3D_INPUT_RANGE"):
            if len(tok) != 3:
                raise ValueError("The LUT text, line %d: %s needs two numbers (low high)." % (no, key))
            lo, hi = _floats(tok[1:], no, key)
            dmin = [lo] * 3
            dmax = [hi] * 3
            continue
        if len(tok) != 3:
            raise ValueError("The LUT text, line %d: a table row needs exactly three numbers (red green blue)." % no)
        table.extend(_floats(tok, no, "a table row"))
    if size3 is None and size1 is None:
        raise ValueError("The LUT has no size line. Add LUT_3D_SIZE 17 (or LUT_1D_SIZE) before the numbers.")
    if size3 is not None and size1 is not None:
        raise ValueError("The LUT has both LUT_3D_SIZE and LUT_1D_SIZE. Keep only one of them.")
    if size3 is not None:
        kind, size, limit = "3D", size3, MAX_SIZE_3D
    else:
        kind, size, limit = "1D", size1, MAX_SIZE_1D
    if not 2 <= size <= limit:
        raise ValueError("The LUT size is %d, but it must be between 2 and %d." % (size, limit))
    rows = size ** 3 if kind == "3D" else size
    if len(table) != rows * 3:
        raise ValueError("The LUT says size %d (%s), so it needs %d rows of three numbers, but it has %d rows."
                         % (size, kind, rows, len(table) // 3))
    for i in range(3):
        if dmax[i] <= dmin[i]:
            raise ValueError("DOMAIN_MAX must be larger than DOMAIN_MIN for every colour channel.")
    return {"size": size, "domain_min": tuple(dmin), "domain_max": tuple(dmax), "table": table, "kind": kind}


def _cube_from_func(size, fn):
    if not 2 <= size <= MAX_SIZE_3D:
        raise ValueError("The LUT size must be between 2 and %d." % MAX_SIZE_3D)
    step = float(size - 1)
    table = []
    for b in range(size):
        for g in range(size):
            for r in range(size):
                rr, gg, bb = fn(r / step, g / step, b / step)
                table.extend((_clamp(rr), _clamp(gg), _clamp(bb)))
    return {"size": size, "domain_min": (0.0, 0.0, 0.0), "domain_max": (1.0, 1.0, 1.0), "table": table, "kind": "3D"}


def identity_cube(size):
    """A table that leaves every colour unchanged."""
    return _cube_from_func(size, lambda r, g, b: (r, g, b))


def _luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _look_warm(r, g, b):
    return r * 1.06 + 0.03, g * 1.01 + 0.005, b * 0.90


def _look_cool(r, g, b):
    return r * 0.90, g * 1.0 + 0.005, b * 1.06 + 0.03


def _look_teal_orange(r, g, b):
    t = _luma(r, g, b) - 0.5          # dark parts lean teal, bright parts lean orange
    r2 = r + 0.16 * t
    g2 = g + (0.03 * -t if t < 0 else 0.0)
    b2 = b - 0.16 * t
    return (0.5 + (r2 - 0.5) * 1.08, 0.5 + (g2 - 0.5) * 1.08, 0.5 + (b2 - 0.5) * 1.08)


def _look_faded(r, g, b):
    y = _luma(r, g, b)
    out = []
    for c in (r, g, b):
        c = y + (c - y) * 0.75          # less colour
        out.append(c * 0.84 + 0.09)     # lifted blacks, softer whites
    return out[0] + 0.01, out[1], out[2] - 0.01


def _look_bw(r, g, b):
    y = _luma(r, g, b)
    return y, y, y


def _look_contrast(r, g, b):
    out = []
    for c in (r, g, b):
        c = _clamp(c)
        s = c * c * (3.0 - 2.0 * c)     # S curve
        out.append(c + 0.9 * (s - c))
    return out[0], out[1], out[2]


def _sat(r, g, b, k):
    """Colour strength: k 1 keeps it, 0 is grey, above 1 is stronger."""
    y = _luma(r, g, b)
    return y + (r - y) * k, y + (g - y) * k, y + (b - y) * k


def _curve(c, amount=1.0):
    c = _clamp(c)
    return c + amount * (c * c * (3.0 - 2.0 * c) - c)


def _look_sunset(r, g, b):
    y = _luma(r, g, b)
    r2, g2, b2 = r * 1.06 + 0.05 * y, g * 1.0 + 0.012 * y, b * 0.84 + 0.02 * (1.0 - y)   # gold in the light, a little rose in the dark
    return _curve(r2, 0.25), _curve(g2, 0.25), _curve(b2, 0.25)


def _look_cold_moon(r, g, b):
    r2, g2, b2 = _sat(r, g, b, 0.82)
    y = _luma(r, g, b)
    return r2 * 0.88, g2 * 0.97 + 0.01, b2 * 1.08 + 0.04 * (1.0 - y)


def _look_night_city(r, g, b):
    t = _luma(r, g, b) - 0.5          # cyan in the dark, magenta in the light
    r2, g2, b2 = r + 0.14 * t, g - 0.10 * abs(t) * (1.0 if t > 0 else -0.6), b + 0.06 + 0.10 * t
    r2, g2, b2 = _sat(r2, g2, b2, 1.15)
    return _curve(r2, 0.35), _curve(g2, 0.35), _curve(b2, 0.35)


def _look_pastel(r, g, b):
    r2, g2, b2 = _sat(r, g, b, 0.7)
    return r2 * 0.72 + 0.26, g2 * 0.72 + 0.24, b2 * 0.72 + 0.27


def _look_bleach(r, g, b):
    y = _curve(_luma(r, g, b), 0.8)
    return 0.45 * r + 0.55 * y, 0.45 * g + 0.55 * y, 0.45 * b + 0.55 * y


def _look_vivid(r, g, b):
    r2, g2, b2 = _sat(r, g, b, 1.35)
    return _curve(r2, 0.3), _curve(g2, 0.3), _curve(b2, 0.3)


def _look_film_stock(r, g, b):
    out = []
    for c in (r, g, b):
        out.append(0.035 + _curve(c, 0.3) * 0.925)      # lifted blacks, softer whites
    return out[0] + 0.012, out[1] + 0.004, out[2] - 0.012


def _look_noir(r, g, b):
    y = _curve(_luma(r, g, b), 1.0)
    return y, y, y


_LOOKS = {"warm": _look_warm, "cool": _look_cool, "teal and orange": _look_teal_orange,
          "faded film": _look_faded, "black and white": _look_bw, "high contrast": _look_contrast,
          "sunset glow": _look_sunset, "cold moon": _look_cold_moon, "night city": _look_night_city, "pastel": _look_pastel,
          "bleach bypass": _look_bleach, "vivid": _look_vivid, "film stock": _look_film_stock, "noir": _look_noir}


def builtin_cube(name, size=17):
    """Build one of the built-in looks as a 3D table, from simple per-pixel maths."""
    if name == "none":
        return identity_cube(size)
    fn = _LOOKS.get(name)
    if fn is None:
        raise ValueError("Unknown built-in look %r. Choose one of: %s." % (name, ", ".join(BUILTIN_NAMES)))
    return _cube_from_func(size, fn)


def sample_cube(cube, rgb):
    """Plain-Python sampler (trilinear for 3D, linear per channel for 1D). rgb is three floats; returns three floats."""
    n = cube["size"]
    t = cube["table"]
    pos = []
    for i in range(3):
        lo, hi = cube["domain_min"][i], cube["domain_max"][i]
        pos.append(_clamp((rgb[i] - lo) / (hi - lo)) * (n - 1))
    if cube["kind"] == "1D":
        out = []
        for c in range(3):
            i0 = min(int(math.floor(pos[c])), n - 2)
            f = pos[c] - i0
            out.append(t[i0 * 3 + c] * (1 - f) + t[(i0 + 1) * 3 + c] * f)
        return tuple(out)
    i0 = [min(int(math.floor(p)), n - 2) for p in pos]
    f = [pos[k] - i0[k] for k in range(3)]
    res = [0.0, 0.0, 0.0]
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (f[0] if dr else 1 - f[0]) * (f[1] if dg else 1 - f[1]) * (f[2] if db else 1 - f[2])
                if w == 0.0:
                    continue
                base = ((i0[2] + db) * n * n + (i0[1] + dg) * n + (i0[0] + dr)) * 3
                for c in range(3):
                    res[c] += w * t[base + c]
    return tuple(res)
