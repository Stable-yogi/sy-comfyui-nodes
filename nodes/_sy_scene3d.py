"""Pure helpers for 3D Scene SY. Plain Python values only; PIL and torch are imported by the node, never here."""
import json
import math

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
KINDS = ("cube", "sphere", "cylinder", "plane")
MAX_OBJECTS = 64
MAX_DATA_CHARS = 24 * 1024 * 1024
MAX_PICTURE_SIDE = 8192
POS_LIMIT = 100.0
SCALE_MIN = 0.05
SCALE_MAX = 50.0
DEFAULT_CAMERA = {"yaw": 0.7, "pitch": 0.45, "dist": 9.0}
DIST_MIN = 1.5
DIST_MAX = 60.0
PITCH_LIMIT = 1.5
SHADED_EMPTY = 0.5   # an empty shaded picture is plain mid grey
DEPTH_EMPTY = 0.0    # an empty depth picture is plain black


def default_scene():
    return {"version": 1, "camera": dict(DEFAULT_CAMERA), "objects": []}


def _number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("scene value '%s' must be a number; delete the object and add it again" % name)
    v = float(value)
    if math.isnan(v) or math.isinf(v):
        raise ValueError("scene value '%s' is not a usable number; delete the object and add it again" % name)
    if v < low or v > high:
        raise ValueError("scene value '%s' must be between %g and %g" % (name, low, high))
    return v


def parse_scene(text):
    """Scene text (JSON) -> a clean scene dict. Empty text gives an empty scene. Bad text raises ValueError."""
    s = (text or "").strip()
    if not s:
        return default_scene()
    try:
        data = json.loads(s)
    except ValueError:
        raise ValueError("the scene text is not valid JSON; clear the scene_json box or rebuild the scene in the editor")
    if not isinstance(data, dict):
        raise ValueError("the scene text must be a JSON object with 'objects' and 'camera'")
    objs = data.get("objects", [])
    if not isinstance(objs, list):
        raise ValueError("scene 'objects' must be a list")
    if len(objs) > MAX_OBJECTS:
        raise ValueError("the scene has more than %d objects; delete some in the editor" % MAX_OBJECTS)
    cam_in = data.get("camera", {})
    if not isinstance(cam_in, dict):
        raise ValueError("scene 'camera' must be an object with yaw, pitch and dist")
    cam = dict(DEFAULT_CAMERA)
    if "yaw" in cam_in:
        cam["yaw"] = _number(cam_in["yaw"], "camera yaw", -1000.0, 1000.0)
    if "pitch" in cam_in:
        cam["pitch"] = _number(cam_in["pitch"], "camera pitch", -PITCH_LIMIT, PITCH_LIMIT)
    if "dist" in cam_in:
        cam["dist"] = _number(cam_in["dist"], "camera dist", DIST_MIN, DIST_MAX)
    out = []
    for i, o in enumerate(objs):
        if not isinstance(o, dict):
            raise ValueError("scene object %d must be an object with a kind and a position" % (i + 1))
        kind = o.get("kind")
        if kind not in KINDS:
            raise ValueError("scene object %d has kind %r; use one of: %s" % (i + 1, kind, ", ".join(KINDS)))
        oid = o.get("id")
        out.append({
            "id": oid if isinstance(oid, int) and not isinstance(oid, bool) else i + 1,
            "kind": kind,
            "x": _number(o.get("x", 0), "x", -POS_LIMIT, POS_LIMIT),
            "y": _number(o.get("y", 0), "y", -POS_LIMIT, POS_LIMIT),
            "z": _number(o.get("z", 0), "z", -POS_LIMIT, POS_LIMIT),
            "scale": _number(o.get("scale", 1), "scale", SCALE_MIN, SCALE_MAX),
        })
    return {"version": 1, "camera": cam, "objects": out}


def summarize(scene):
    """'3 objects: cube, sphere, plane' (or 'empty scene') from a clean scene dict."""
    objs = scene.get("objects", [])
    if not objs:
        return "empty scene"
    n = len(objs)
    return "%d object%s: %s" % (n, "" if n == 1 else "s", ", ".join(o["kind"] for o in objs))


def summary_from_text(text):
    return summarize(parse_scene(text))


def strip_data_url(text):
    """Removes a 'data:image/png;base64,' start and spaces. Returns the bare base64 text."""
    s = (text or "").strip()
    if s.startswith("data:"):
        cut = s.find(",")
        if cut < 0:
            raise ValueError("the stored picture text is damaged: a data header has no comma. Clear it and use the editor again")
        s = s[cut + 1:]
    return "".join(s.split())


def decode_png_bytes(text, what="picture"):
    """Base64 text (with or without a data header) -> PNG bytes. Empty text -> b''."""
    import base64
    import binascii
    s = strip_data_url(text)
    if not s:
        return b""
    if len(s) > MAX_DATA_CHARS:
        raise ValueError("the stored %s is too large; clear it and use the editor again" % what)
    try:
        raw = base64.b64decode(s, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("the stored %s text is not valid base64; clear it and use the editor again" % what)
    if not raw.startswith(PNG_SIGNATURE):
        raise ValueError("the stored %s is not a PNG picture; clear it and use the editor again" % what)
    return raw


def check_size(width, height):
    for name, v in (("width", width), ("height", height)):
        if int(v) < 64 or int(v) > 2048:
            raise ValueError("%s must be between 64 and 2048" % name)
    return int(width), int(height)
