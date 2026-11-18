"""H3 Sheet Designer SY: plans a character reference sheet for MiniMax H3 Image. You pick the views (or a preset) and the
size; it gives the prompt, a plain layout guide picture (grey shapes, no text) and the width and height."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MULTIPLE = 32
SIZES = {"4 MP (fast)": 4.0, "8 MP (more detail)": 8.0, "16 MP (best, slow)": 16.0}

# key, kind, words used in the prompt
VIEWS = (
    ("face_front", "face", "the face from the front"),
    ("face_3q_left", "face", "the face in a three-quarter view turned to the left"),
    ("face_left", "face", "the face in profile looking to the left"),
    ("face_3q_right", "face", "the face in a three-quarter view turned to the right"),
    ("face_right", "face", "the face in profile looking to the right"),
    ("face_back", "face", "the back of the head"),
    ("body_front", "body", "the front view"),
    ("body_side", "body", "the side view"),
    ("body_back", "body", "the back view"),
    ("outfit_front", "outfit", "the front"),
    ("outfit_back", "outfit", "the back"),
    ("hands", "hands", "both hands"),
    ("feet", "feet", "both feet"),
)
VIEW_KEYS = tuple(v[0] for v in VIEWS)
_KIND = {v[0]: v[1] for v in VIEWS}
_WORDS = {v[0]: v[2] for v in VIEWS}

PRESETS = {
    "Standard 5 (2 faces + 3 bodies)": ("face_front", "face_left", "body_front", "body_side", "body_back"),
    "Basic 4 (1 face + 3 bodies)": ("face_front", "body_front", "body_side", "body_back"),
    "Turnaround 3 (3 bodies)": ("body_front", "body_side", "body_back"),
    "Head 6 (6 head views)": ("face_front", "face_3q_left", "face_left", "face_3q_right", "face_right", "face_back"),
    "Full 7 (2 faces, 3 bodies, hands, feet)": ("face_front", "face_left", "body_front", "body_side", "body_back", "hands", "feet"),
    "All 13": VIEW_KEYS,
    "Custom (use the views box)": (),
}
STYLES = {
    "as in the picture": "",
    "photo": "a realistic photograph",
    "anime": "clean anime illustration with lines and flat colours",
    "3D render": "a polished 3D character render",
    "painted": "a soft painted illustration",
}

# Sizes in sheet units: a full-body panel is 1.0 high.
GAP = 0.04
MARGIN = 0.04
FACE = (1.0 - GAP) / 2.0
BODY_W = 0.42


def parse_views(text):
    """Pure function. 'face_front, body_back' -> ('face_front', 'body_back'), in sheet order, no repeats."""
    words = [w.strip().lower() for w in str(text or "").replace(";", ",").replace("\n", ",").split(",")]
    words = [w for w in words if w]
    bad = [w for w in words if w not in VIEW_KEYS]
    if bad:
        raise ValueError("unknown view %r; use these words: %s" % (bad[0], ", ".join(VIEW_KEYS)))
    return tuple(k for k in VIEW_KEYS if k in words)


def pick_views(preset, views_text=""):
    """Pure function. The views for a preset; the Custom preset reads views_text."""
    if preset not in PRESETS:
        raise ValueError("unknown preset %r; pick one of: %s" % (preset, ", ".join(PRESETS)))
    views = PRESETS[preset] or parse_views(views_text)
    if not views:
        raise ValueError("no view chosen: type views in the views box, for example face_front, body_front, body_back")
    return tuple(views)


def plan_layout(views):
    """Pure function. Panels as (view, x, y, w, h) in sheet units, plus the sheet (width, height).
    Faces stack two per column on the left (three per row when the sheet holds only faces), then the full bodies,
    then the outfit, then hands above feet on the right."""
    views = [v for v in VIEW_KEYS if v in views]
    if not views:
        raise ValueError("no view to lay out")
    faces = [v for v in views if _KIND[v] == "face"]
    tall = [v for v in views if _KIND[v] in ("body", "outfit")]
    small = [v for v in views if _KIND[v] in ("hands", "feet")]
    panels = []
    x = MARGIN
    if faces and not tall and not small:
        per_row = 1 if len(faces) == 1 else (2 if len(faces) <= 4 else 3)
        rows = int(math.ceil(len(faces) / float(per_row)))
        for i, v in enumerate(faces):
            r, c = divmod(i, per_row)
            panels.append((v, MARGIN + c * (FACE + GAP), MARGIN + r * (FACE + GAP), FACE, FACE))
        width = 2 * MARGIN + per_row * FACE + (per_row - 1) * GAP
        height = 2 * MARGIN + rows * FACE + (rows - 1) * GAP
        return panels, (round(width, 4), round(height, 4))
    columns = []
    for i in range(0, len(faces), 2):
        columns.append([(v, FACE, FACE) for v in faces[i:i + 2]])
    for v in tall:
        columns.append([(v, BODY_W, 1.0)])
    if small:
        columns.append([(v, FACE, FACE) for v in small])
    for col in columns:
        w = max(p[1] for p in col)
        used = sum(p[2] for p in col) + GAP * (len(col) - 1)
        y = MARGIN + (1.0 - used) / 2.0
        for v, pw, ph in col:
            panels.append((v, x, y, pw, ph))
            y += ph + GAP
        x += w + GAP
    width = x - GAP + MARGIN
    return panels, (round(width, 4), round(1.0 + 2 * MARGIN, 4))


def sheet_size(aspect, size, multiple=MULTIPLE):
    """Pure function. (width, height) near the megapixels of `size` for a sheet of shape `aspect` (width / height)."""
    if size not in SIZES:
        raise ValueError("unknown size %r; pick one of: %s" % (size, ", ".join(SIZES)))
    if aspect <= 0:
        raise ValueError("the sheet shape must be above 0, got %r" % (aspect,))
    area = SIZES[size] * 1024 * 1024
    h = math.sqrt(area / aspect)
    w = h * aspect
    return max(multiple, int(round(w / multiple)) * multiple), max(multiple, int(round(h / multiple)) * multiple)


def _join(items):
    items = list(items)
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _count(n):
    return ("one", "two", "three", "four", "five", "six")[n - 1] if 1 <= n <= 6 else str(n)


def build_prompt(views, style="as in the picture", use_guide=True, notes=""):
    """Pure function. The H3 Image prompt. <Picture 1> is the character, <Picture 2> the layout guide.
    Never asks for labels, numbers or frames, so no text ends up in the sheet."""
    if style not in STYLES:
        raise ValueError("unknown style %r; pick one of: %s" % (style, ", ".join(STYLES)))
    views = [v for v in VIEW_KEYS if v in views]
    if not views:
        raise ValueError("no view chosen")
    faces = [v for v in views if _KIND[v] == "face"]
    bodies = [v for v in views if _KIND[v] == "body"]
    outfit = [v for v in views if _KIND[v] == "outfit"]
    small = [v for v in views if _KIND[v] in ("hands", "feet")]
    n = len(views)
    look = STYLES[style]
    head = "A character reference sheet of the character in <Picture 1>"
    head += (", drawn as %s." % look) if look else "."
    if n == 1:
        head = head[:-1] + ", showing one single view in the middle of the sheet."
    parts = []
    if faces:
        if not (bodies or outfit or small) and len(faces) > 2:
            per_row = 2 if len(faces) <= 4 else 3
            parts.append("%s head close-ups in rows of %s: %s" % (_count(len(faces)).capitalize(), _count(per_row),
                                                                  _join(_WORDS[v] for v in faces)))
        else:
            parts.append("%s %s: %s" % (_count(len(faces)).capitalize(),
                                        "head close-up" if len(faces) == 1 else "head close-ups stacked in pairs",
                                        _join(_WORDS[v] for v in faces)))
    if bodies:
        parts.append("%s full-body %s standing upright, whole figure from the top of the head to the soles of the feet: %s"
                     % (_count(len(bodies)).capitalize(), "view" if len(bodies) == 1 else "views", _join(_WORDS[v] for v in bodies)))
    if outfit:
        parts.append("The outfit alone, laid out flat with no person inside it: %s" % _join(_WORDS[v] for v in outfit))
    if small:
        parts.append("Close-ups of %s" % _join(_WORDS[v] for v in small) + (", hands above feet" if len(small) == 2 else ""))
    lines = [head]
    if n > 1:
        lines.append("From left to right: " + ". ".join(parts) + ".")
        lines.append("Each view appears exactly once, with clear white space between the views.")
    else:
        lines.append(parts[0] + ".")
    if use_guide:
        lines.append("Use <Picture 2> only as the layout: each pale grey shape marks where one view goes and how big it is. "
                     "Replace every grey shape with the real character; do not copy the grey shapes.")
    lines.append("Every view shows the very same character with the same face, hair, body shape, clothes, colours and "
                 "accessories as in <Picture 1>. Parts that <Picture 1> does not show are completed so they match it.")
    lines.append("Plain white background, even soft studio light, sharp detail.")
    lines.append("No text, no letters, no numbers, no labels, no captions, no frames, no borders, no grid lines.")
    extra = " ".join(str(notes or "").split())
    if extra:
        lines.append("Character notes: %s" % extra)
    return "\n".join(lines)


def _figure(draw, x0, y0, w, h, kind, view, grey):
    """Draws one plain grey shape that marks a panel (no text)."""
    def ell(cx, cy, rx, ry):
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=grey)

    def rect(ax, ay, bx, by, r=0):
        draw.rounded_rectangle([min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)], radius=r, fill=grey)

    cx = x0 + w / 2.0
    if kind == "face":
        turn = {"face_3q_left": -0.06, "face_left": -0.1, "face_3q_right": 0.06, "face_right": 0.1}.get(view, 0.0) * w
        rect(cx - w * 0.36, y0 + h * 0.80, cx + w * 0.36, y0 + h * 0.98, r=int(w * 0.08))  # shoulders
        rect(cx - w * 0.09, y0 + h * 0.62, cx + w * 0.09, y0 + h * 0.84)  # neck
        ell(cx + turn, y0 + h * 0.42, w * 0.22, h * 0.28)  # head
        if view in ("face_left", "face_right"):
            side = -1 if view == "face_left" else 1
            ell(cx + turn + side * w * 0.2, y0 + h * 0.46, w * 0.05, h * 0.05)  # nose
    elif kind == "body":
        u = h / 8.0
        ell(cx, y0 + u * 0.75, u * 0.45, u * 0.58)
        if view == "body_side":
            rect(cx - u * 0.35, y0 + u * 1.4, cx + u * 0.35, y0 + u * 4.2, r=int(u * 0.2))
            rect(cx - u * 0.2, y0 + u * 1.6, cx + u * 0.2, y0 + u * 4.1, r=int(u * 0.15))
            rect(cx - u * 0.3, y0 + u * 4.0, cx + u * 0.3, y0 + u * 7.7, r=int(u * 0.15))
            rect(cx - u * 0.3, y0 + u * 7.6, cx + u * 0.55, y0 + u * 7.95, r=int(u * 0.1))
        else:
            rect(cx - u * 0.8, y0 + u * 1.4, cx + u * 0.8, y0 + u * 4.2, r=int(u * 0.3))  # body
            for s in (-1, 1):
                rect(cx + s * u * 0.85, y0 + u * 1.5, cx + s * u * 1.2, y0 + u * 4.3, r=int(u * 0.15))  # arms
                rect(cx + s * u * 0.08, y0 + u * 4.0, cx + s * u * 0.6, y0 + u * 7.7, r=int(u * 0.15))  # legs
                rect(cx + s * u * 0.08, y0 + u * 7.6, cx + s * u * 0.65, y0 + u * 7.95, r=int(u * 0.1))  # feet
    elif kind == "outfit":
        u = h / 8.0
        rect(cx - u * 0.9, y0 + u * 1.2, cx + u * 0.9, y0 + u * 4.2, r=int(u * 0.3))
        for s in (-1, 1):
            rect(cx + s * u * 0.95, y0 + u * 1.3, cx + s * u * 1.35, y0 + u * 3.8, r=int(u * 0.15))
            rect(cx + s * u * 0.05, y0 + u * 4.1, cx + s * u * 0.7, y0 + u * 7.3, r=int(u * 0.15))
    elif kind == "hands":
        for s in (-1, 1):
            hx = cx + s * w * 0.22
            ell(hx, y0 + h * 0.6, w * 0.13, h * 0.17)
            for f in range(4):
                fx = hx - w * 0.09 + f * w * 0.06
                rect(fx - w * 0.022, y0 + h * 0.18, fx + w * 0.022, y0 + h * 0.55, r=int(w * 0.02))
    elif kind == "feet":
        for s in (-1, 1):
            ell(cx + s * w * 0.2, y0 + h * 0.55, w * 0.12, h * 0.3)


def draw_guide(views, width, height, grey=225):
    """Draws the layout guide: white sheet, one pale grey shape per view, no text. Returns a numpy array (H, W, 3) 0..1."""
    import numpy as np
    from PIL import Image, ImageDraw
    panels, (sw, sh) = plan_layout(views)
    img = Image.new("RGB", (int(width), int(height)), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    sx, sy = width / sw, height / sh
    for v, x, y, w, h in panels:
        _figure(draw, x * sx, y * sy, w * sx, h * sy, _KIND[v], v, (grey, grey, grey))
    return np.asarray(img, dtype=np.float32) / 255.0


def describe(views, width, height):
    """Pure function. One plain info text."""
    views = [v for v in VIEW_KEYS if v in views]
    return "H3 SHEET DESIGNER\n%d view%s: %s\nSize %d x %d (%.1f MP)." % (
        len(views), "" if len(views) == 1 else "s", ", ".join(views), width, height, width * height / 1048576.0)


class SYH3SheetDesigner:
    DESCRIPTION = ("Plans a character reference sheet for MiniMax H3 Image. Pick a preset or your own views (faces, full "
                   "bodies, outfit, hands, feet) and a size. Gives the prompt, a plain layout guide picture (grey shapes, "
                   "no text) and the width and height. Connect your character picture as image_1 and the layout guide as "
                   "image_2 of the H3 Image conditioning node.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("prompt", "layout_guide", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
                    "preset": (list(PRESETS), {"default": list(PRESETS)[0], "tooltip": "Which views the sheet shows. Custom reads the views box."}),
                    "size": (list(SIZES), {"default": list(SIZES)[0], "tooltip": "How many megapixels the whole sheet has. More = sharper faces, slower."}),
                    "style": (list(STYLES), {"default": "as in the picture", "tooltip": "Keep the look of your picture, or turn the character into another style."}),
                    "use_layout_guide": ("BOOLEAN", {"default": True, "tooltip": "On: the prompt says to follow the layout guide (connect it as image_2). Off: layout in words only."}),
                },
                "optional": {
                    "views": ("STRING", {"default": "", "multiline": False, "tooltip": "Only for the Custom preset. Comma separated, e.g. face_front, body_front, hands. A wrong word shows the full list."}),
                    "notes": ("STRING", {"default": "", "multiline": True, "tooltip": "Optional extra words about the character, added at the end of the prompt."}),
                }}

    def run(self, preset, size, style, use_layout_guide, views="", notes=""):
        import torch
        chosen = pick_views(preset, views)
        _, (sw, sh) = plan_layout(chosen)
        w, h = sheet_size(sw / sh, size)
        prompt = build_prompt(chosen, style, bool(use_layout_guide), notes)
        guide = torch.from_numpy(draw_guide(chosen, w, h)).unsqueeze(0)
        return (prompt, guide, w, h, describe(chosen, w, h))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3SheetDesigner", SYH3SheetDesigner)
NODE_DISPLAY_NAME_MAPPINGS["SYH3SheetDesigner"] = "H3 Sheet Designer SY"
