"""Face Parts Mask SY: tick face parts (skin, eyes, brows, lips, hair, neck ...) and get one mask of them, from a
face-parsing model file. One node does what used to take a model loader, a processor loader, a parser and a picker.
Two engines:
- "free to sell (MediaPipe)" (default): Google MediaPipe models, Apache 2.0, in models/mediapipe
  (selfie_multiclass_256x256.tflite for hair, face skin, neck, clothes; face_landmarker.task for eyes, brows, lips, nose).
- "research only (face-parsing)": a Segformer face-parsing model in models/face_parsing (config.json,
  preprocessor_config.json, model.safetensors). The common one is licensed for non-commercial research only."""
import json
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FOLDER = "face_parsing"
NEEDED = ("config.json", "preprocessor_config.json", "model.safetensors")
# (input name shown on the node, label in the model file, default)
PARTS = (
    ("background", "background", False),
    ("skin", "skin", True),
    ("nose", "nose", True),
    ("glasses", "eye_g", False),
    ("left_eye", "l_eye", True),
    ("right_eye", "r_eye", True),
    ("left_brow", "l_brow", True),
    ("right_brow", "r_brow", True),
    ("left_ear", "l_ear", False),
    ("right_ear", "r_ear", False),
    ("mouth_inside", "mouth", True),
    ("upper_lip", "u_lip", True),
    ("lower_lip", "l_lip", True),
    ("hair", "hair", False),
    ("hat", "hat", False),
    ("earring", "ear_r", False),
    ("necklace", "neck_l", False),
    ("neck", "neck", False),
    ("clothes", "cloth", False),
)
PART_NAMES = tuple(p[0] for p in PARTS)
DEFAULT_MEAN = (0.485, 0.456, 0.406)
DEFAULT_STD = (0.229, 0.224, 0.225)
DEFAULT_SIZE = 512
_CACHE = {}
ENGINES = ("free to sell (MediaPipe)", "research only (face-parsing)")
MP_FOLDER = "mediapipe"
MP_SEG = "selfie_multiclass_256x256.tflite"
MP_LMK = "face_landmarker.task"
MP_CLASS = {"background": 0, "hair": 1, "body_skin": 2, "face_skin": 3, "clothes": 4, "other": 5}
# face mesh landmark rings; left/right = the person's own side, like the face-parsing labels
RING = {
    "l_eye": (263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466),
    "r_eye": (33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246),
    "l_brow": (300, 293, 334, 296, 336, 285, 295, 282, 283, 276),
    "r_brow": (70, 63, 105, 66, 107, 55, 65, 52, 53, 46),
    "u_lip": (61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191, 78),
    "l_lip": (61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78),
    "mouth": (78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95),
}
FACE_OVAL = (10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
             176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109)
NOSE_POINTS = (168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 327, 64, 294, 48, 278, 49, 279, 102, 331, 129, 358,
               219, 439, 115, 344, 220, 440, 45, 275, 51, 281, 3, 248, 236, 456)
# where each part comes from in the free-to-sell engine: (kind, source)
MP_SOURCE = {"background": ("class", "background"), "skin": ("skin", None), "nose": ("hull", None),
             "eye_g": ("zone", "glasses"), "l_eye": ("ring", "l_eye"), "r_eye": ("ring", "r_eye"),
             "l_brow": ("ring", "l_brow"), "r_brow": ("ring", "r_brow"), "l_ear": ("zone", "l_ear"),
             "r_ear": ("zone", "r_ear"), "mouth": ("ring", "mouth"), "u_lip": ("ring", "u_lip"),
             "l_lip": ("ring", "l_lip"), "hair": ("class", "hair"), "hat": ("none", None),
             "ear_r": ("zone", "earring"), "neck_l": ("zone", "necklace"), "neck": ("zone", "neck"),
             "cloth": ("class", "clothes")}
# zone parts: (model class, which side of the face outline, rows as face heights from the face top)
# side: "in" = inside the face outline, "out" = outside it, "any"; left/right = the person's own side;
# face_width = only columns under the face (keeps the neck off the shoulders)
ZONES = {"glasses": ("other", "in", -0.05, 0.62, None), "l_ear": ("face_skin", "out", 0.2, 0.85, "left"),
         "r_ear": ("face_skin", "out", 0.2, 0.85, "right"), "earring": ("other", "out", 0.35, 1.15, None),
         "necklace": ("other", "out", 1.0, 2.2, None), "neck": ("body_skin", "any", 0.85, 1.35, "face_width")}


def zone_rows(top, bottom, start, end, height):
    """Pure function. (first_row, last_row_exclusive) for a zone given as face heights below the face top."""
    fh = max(1.0, bottom - top)
    a = int(max(0, min(height, round(top + start * fh))))
    b = int(max(0, min(height, round(top + end * fh))))
    return a, max(a, b)


def convex_hull(points):
    """Pure function. Convex hull of (x, y) points, counter-clockwise, no repeats."""
    pts = sorted(set((float(x), float(y)) for x, y in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return lower[:-1] + upper[:-1]


def unsupported(labels):
    """Pure function. Labels the free-to-sell engine cannot find (they stay empty)."""
    return [l for l in labels if MP_SOURCE[l][0] == "none"]


def ring_points(landmarks, ring, w, h):
    """Pure function. Pixel (x, y) points for one landmark ring; landmarks have .x and .y from 0 to 1."""
    return [(landmarks[i].x * w, landmarks[i].y * h) for i in ring]


def mp_model_files():
    """Paths of the two MediaPipe files, or a clear error naming what is missing."""
    import folder_paths
    folder = os.path.join(folder_paths.models_dir, MP_FOLDER)
    missing = [f for f in (MP_SEG, MP_LMK) if not os.path.isfile(os.path.join(folder, f))]
    if missing:
        raise ValueError("No MediaPipe model files were found. Face Parts Mask SY (free to sell) needs %s in %s. "
                         "Get them from Google's MediaPipe model pages (Apache 2.0), or pick the research-only engine."
                         % (" and ".join(missing), folder))
    return os.path.join(folder, MP_SEG), os.path.join(folder, MP_LMK)


def _mp_tools():
    key = ("mediapipe",)
    if key not in _CACHE:
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import BaseOptions, vision
        except ImportError:
            raise ValueError("The free-to-sell engine needs the Python package mediapipe in the ComfyUI Python "
                             "(pip install mediapipe), or pick the research-only engine.")
        seg_path, lmk_path = mp_model_files()
        cpu = BaseOptions.Delegate.CPU
        seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path=seg_path, delegate=cpu), output_category_mask=True))
        lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=lmk_path, delegate=cpu), num_faces=4))
        _CACHE.clear()
        _CACHE[key] = (mp, seg, lmk)
    return _CACHE[key]


def mp_label_masks(rgb):
    """{label: HxW bool array} for every part of one picture (uint8 HxWx3), free-to-sell engine; plus faces found."""
    import numpy as np
    from PIL import Image, ImageDraw
    mp, seg, lmk = _mp_tools()
    h, w = rgb.shape[:2]
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
    cls = np.asarray(seg.segment(img).category_mask.numpy_view()).reshape(h, w)
    faces = lmk.detect(img).face_landmarks or []

    def fill(polys):
        im = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(im)
        for poly in polys:
            if len(poly) >= 3:
                d.polygon(poly, fill=255)
        return np.asarray(im) > 0
    shapes = {name: fill([ring_points(f, ring, w, h) for f in faces]) for name, ring in RING.items()}
    shapes["nose"] = fill([convex_hull(ring_points(f, NOSE_POINTS, w, h)) for f in faces])
    zones = {name: np.zeros((h, w), bool) for name in ZONES}
    xs = np.arange(w)[None, :]
    for f in faces:
        oval = fill([ring_points(f, FACE_OVAL, w, h)])
        pts = ring_points(f, FACE_OVAL, w, h)
        top, bottom = min(y for _, y in pts), max(y for _, y in pts)
        mid = sum(x for x, _ in pts) / len(pts)
        left_x, right_x = min(x for x, _ in pts), max(x for x, _ in pts)
        for name, (cname, side, start, end, lr) in ZONES.items():
            a, b = zone_rows(top, bottom, start, end, h)
            if a == b:
                continue
            area = cls[a:b] == MP_CLASS[cname]
            if side == "in":
                area &= oval[a:b]
            elif side == "out":
                area &= ~oval[a:b]
            if lr == "left":      # the person's left = the right side of the picture
                area &= xs >= mid
            elif lr == "right":
                area &= xs < mid
            elif lr == "face_width":
                area &= (xs >= left_x) & (xs <= right_x)
            zones[name][a:b] |= area
    shapes["u_lip"] &= ~shapes["mouth"]
    shapes["l_lip"] &= ~shapes["mouth"]
    cut = np.zeros((h, w), bool)
    for name in ("l_eye", "r_eye", "l_brow", "r_brow", "u_lip", "l_lip", "mouth", "nose"):
        cut |= shapes[name]
    out = {}
    for _, label, _ in PARTS:
        kind, src = MP_SOURCE[label]
        if kind == "class":
            out[label] = cls == MP_CLASS[src]
        elif kind == "skin":
            out[label] = (cls == MP_CLASS["face_skin"]) & ~cut
        elif kind == "ring":
            out[label] = shapes[src]
        elif kind == "hull":
            out[label] = shapes["nose"]
        elif kind == "zone":
            out[label] = zones[src]
        else:
            out[label] = np.zeros((h, w), bool)
    return out, len(faces)


def picked_labels(flags):
    """Pure function. Model label names for the ticked parts. `flags` maps node input name -> bool."""
    unknown = [k for k in flags if k not in PART_NAMES]
    if unknown:
        raise ValueError("unknown face part(s): %s; allowed: %s" % (", ".join(sorted(unknown)), ", ".join(PART_NAMES)))
    return [label for name, label, _ in PARTS if flags.get(name)]


def label_ids(id2label, labels):
    """Pure function. Class numbers for the label names, read from the model's id2label table."""
    lookup = {str(v): int(k) for k, v in id2label.items()}
    missing = [l for l in labels if l not in lookup]
    if missing:
        raise ValueError("this face-parsing model has no part(s) %s; it knows: %s"
                         % (", ".join(missing), ", ".join(sorted(lookup))))
    return sorted(lookup[l] for l in labels)


def preprocess_settings(cfg):
    """Pure function. (height, width, mean, std, rescale) from a preprocessor_config.json dict."""
    size = cfg.get("size", DEFAULT_SIZE)
    if isinstance(size, dict):
        h, w = int(size.get("height", DEFAULT_SIZE)), int(size.get("width", DEFAULT_SIZE))
    else:
        h = w = int(size)
    if not (32 <= h <= 4096 and 32 <= w <= 4096):
        raise ValueError("preprocessor size %dx%d is outside 32-4096" % (w, h))
    mean = tuple(float(x) for x in cfg.get("image_mean", DEFAULT_MEAN))
    std = tuple(float(x) for x in cfg.get("image_std", DEFAULT_STD))
    if len(mean) != 3 or len(std) != 3 or min(std) <= 0:
        raise ValueError("preprocessor mean/std must be 3 numbers each, std above 0")
    return h, w, mean, std, bool(cfg.get("do_normalize", True))


def palette(n):
    """Pure function. n distinct preview colours as (r, g, b) 0-1, class 0 (background) black."""
    out = [(0.0, 0.0, 0.0)]
    for i in range(1, n):
        h = (i * 0.618033988749895) % 1.0
        k = int(h * 6)
        f = h * 6 - k
        v, s = 1.0, 0.75
        p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
        out.append(((v, q, p, p, t, v)[k % 6], (t, v, v, q, p, p)[k % 6], (p, p, t, v, v, q)[k % 6]))
    return out


def missing_files(folder):
    if not folder or not os.path.isdir(folder):
        return list(NEEDED)
    return [f for f in NEEDED if not os.path.isfile(os.path.join(folder, f))]


def model_folder():
    """The first face_parsing folder ComfyUI knows that holds all 3 files (models/face_parsing by default)."""
    import folder_paths
    tries = []
    try:
        tries += list(folder_paths.get_folder_paths(FOLDER))
    except Exception:
        pass
    tries.append(os.path.join(folder_paths.models_dir, FOLDER))
    for t in tries:
        if not missing_files(t):
            return t
    raise ValueError("No face-parsing model files were found. Face Parts Mask SY needs a Segformer face-parsing model in models/%s (files: %s). "
                     "Missing in %s: %s" % (FOLDER, ", ".join(NEEDED), tries[-1], ", ".join(missing_files(tries[-1]))))


def _load(folder, device):
    key = (folder, str(device))
    if key not in _CACHE:
        from transformers import SegformerForSemanticSegmentation
        model = SegformerForSemanticSegmentation.from_pretrained(folder, local_files_only=True).to(device).eval()
        with open(os.path.join(folder, "preprocessor_config.json"), encoding="utf-8") as f:
            pre = preprocess_settings(json.load(f))
        _CACHE.clear()
        _CACHE[key] = (model, pre)
    return _CACHE[key]


def parse_faces(image, folder, device):
    """Class number per pixel for every picture in the batch: a [B, H, W] long tensor on the CPU."""
    import torch
    import torch.nn.functional as F
    model, (h, w, mean, std, norm) = _load(folder, device)
    m = torch.tensor(mean, device=device).view(1, 3, 1, 1)
    s = torch.tensor(std, device=device).view(1, 3, 1, 1)
    out = []
    with torch.no_grad():
        for i in range(image.shape[0]):
            x = image[i:i + 1, :, :, :3].permute(0, 3, 1, 2).to(device, torch.float32)
            H, W = x.shape[-2:]
            x = F.interpolate(x, size=(h, w), mode="bilinear", align_corners=False)
            if norm:
                x = (x - m) / s
            logits = model(pixel_values=x.to(model.dtype)).logits.float()
            logits = F.interpolate(logits, size=(H, W), mode="bilinear", align_corners=False)
            out.append(logits.argmax(dim=1).cpu())
    return torch.cat(out, 0)


class SYFacePartsMask:
    DESCRIPTION = ("Tick the face parts you want (skin, eyes, brows, lips, hair, neck and more) and get one white mask "
                   "of them, ready for skin fixes, face detail or inpainting. Also gives a coloured map of all parts "
                   "so you can see what the model found. Default engine: Google MediaPipe models in models/mediapipe "
                   "(free to sell). Research-only engine: face-parsing model files in models/face_parsing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "IMAGE", "STRING")
    RETURN_NAMES = ("mask", "parts_map", "info")

    @classmethod
    def INPUT_TYPES(cls):
        req = {"image": ("IMAGE", {"tooltip": "The picture(s) with a face."})}
        for name, label, default in PARTS:
            req[name] = ("BOOLEAN", {"default": default, "tooltip": "On: %s goes into the mask." % name.replace("_", " ")})
        return {"required": req, "optional": {"engine": (list(ENGINES), {"default": ENGINES[0], "tooltip":
                "MediaPipe: fine for paid work, finds every part but hats. face-parsing: all parts, research use only."})}}

    def run(self, image, engine=ENGINES[0], **flags):
        if engine not in ENGINES:
            raise ValueError("unknown engine %r; pick one of: %s" % (engine, ", ".join(ENGINES)))
        labels = picked_labels(flags)
        if engine == ENGINES[0]:
            return self._run_mp(image, labels, flags)
        return self._run_parsing(image, labels, flags)

    def _run_mp(self, image, labels, flags):
        import numpy as np
        import torch
        pal = np.array(palette(len(PARTS)), dtype=np.float32)
        masks, maps, found = [], [], 0
        for i in range(image.shape[0]):
            rgb = (image[i, :, :, :3].clamp(0, 1).cpu().numpy() * 255).round().astype(np.uint8)
            parts, nf = mp_label_masks(rgb)
            found += nf
            m = np.zeros(rgb.shape[:2], bool)
            for l in labels:
                m |= parts[l]
            idx = np.zeros(rgb.shape[:2], np.int64)
            for k, (_, l, _) in enumerate(PARTS):
                if k:
                    idx[parts[l]] = k
            masks.append(torch.from_numpy(m.astype(np.float32)))
            maps.append(torch.from_numpy(pal[idx]))
        mask, parts_map = torch.stack(masks), torch.stack(maps)
        cover = float(mask.mean()) * 100.0
        info = "FACE PARTS MASK (free to sell: MediaPipe)\n%d picture(s), %d face(s) found, parts: %s\nMask covers %.1f%% of the picture." % (
            image.shape[0], found, ", ".join(n for n, _, _ in PARTS if flags.get(n)) or "(none ticked: empty mask)", cover)
        miss = unsupported(labels)
        if miss:
            info += "\nNot found by this engine (left empty): %s." % ", ".join(n for n, l, _ in PARTS if l in miss)
        return (mask, parts_map, info)

    def _run_parsing(self, image, labels, flags):
        import torch
        import comfy.model_management as mm
        folder = model_folder()
        device = mm.get_torch_device()
        model, _ = _load(folder, device)
        ids = label_ids(model.config.id2label, labels)
        cls_map = parse_faces(image, folder, device)
        mask = torch.zeros(cls_map.shape, dtype=torch.float32)
        for i in ids:
            mask[cls_map == i] = 1.0
        pal = torch.tensor(palette(len(model.config.id2label)), dtype=torch.float32)
        parts_map = pal[cls_map.clamp(0, len(pal) - 1)]
        cover = float(mask.mean()) * 100.0
        info = "FACE PARTS MASK (research only: face-parsing)\n%d picture(s), parts: %s\nMask covers %.1f%% of the picture." % (
            image.shape[0], ", ".join(n for n, _, _ in PARTS if flags.get(n)) or "(none ticked: empty mask)", cover)
        return (mask, parts_map, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FacePartsMask", SYFacePartsMask)
