"""Face Detect SY: finds faces in a picture and returns a mask (box or ellipse) plus the box list.
Chain: Face Detect SY -> Inpaint Crop SY -> sampler -> Inpaint Stitch SY. No face found gives an empty mask, no error."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

BUILTIN = "Built-in (no file needed)"
MODEL_FOLDER = "sy_face_detect"
PICK_MODES = ("centre 1", "largest 1", "all")
SHAPES = ("box", "ellipse")
MAX_SIDE = 1280
HAAR_FILES = ("haarcascade_frontalface_default.xml", "haarcascade_frontalface_alt2.xml")
NEED_CV2 = ("this node needs the opencv package; add it with python -m pip install "
            "opencv-python-headless using the python of your ComfyUI")


# ---------------------------------------------------------------- pure functions
# A box is (x0, y0, x1, y1) in pixels. x1 and y1 are exclusive (width = x1 - x0).

def _check_box(box):
    if len(box) != 4:
        raise ValueError("a box needs 4 numbers (x0, y0, x1, y1), got %r" % (box,))
    return box


def _area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def _iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = _area(a) + _area(b) - inter
    return inter / union if union > 0 else 0.0


def nms(boxes, scores, iou):
    """Return the indices of the boxes to keep, highest score first. Overlap above `iou` removes the weaker box."""
    if len(boxes) != len(scores):
        raise ValueError("boxes and scores must have the same length (%d and %d)" % (len(boxes), len(scores)))
    if not 0.0 <= float(iou) <= 1.0:
        raise ValueError("iou must be between 0 and 1, got %r" % (iou,))
    order = sorted(range(len(boxes)), key=lambda i: (-scores[i], boxes[i][0], i))
    kept = []
    for i in order:
        _check_box(boxes[i])
        if all(_iou(boxes[i], boxes[k]) <= iou for k in kept):
            kept.append(i)
    return kept


def small_keep(boxes, min_face):
    """Indices of boxes whose shorter side is at least min_face pixels."""
    if min_face < 1:
        raise ValueError("min_face must be at least 1, got %r" % (min_face,))
    return [i for i, b in enumerate(boxes) if min(b[2] - b[0], b[3] - b[1]) >= min_face]


def drop_small(boxes, min_face):
    """Remove boxes whose shorter side is smaller than min_face pixels."""
    return [boxes[i] for i in small_keep(boxes, min_face)]


def pick_faces(boxes, scores, width, height, mode):
    """Choose boxes: 'centre 1' (nearest the picture centre), 'largest 1', or 'all'. Ties: higher score, then lower x."""
    if mode not in PICK_MODES:
        raise ValueError("unknown pick mode %r; choose one of: %s" % (mode, ", ".join(PICK_MODES)))
    if len(boxes) != len(scores):
        raise ValueError("boxes and scores must have the same length (%d and %d)" % (len(boxes), len(scores)))
    if not boxes:
        return []
    idx = list(range(len(boxes)))
    if mode == "all":
        idx.sort(key=lambda i: (boxes[i][0], boxes[i][1]))
        return [tuple(boxes[i]) for i in idx]
    if mode == "largest 1":
        best = min(idx, key=lambda i: (-_area(boxes[i]), -scores[i], boxes[i][0]))
    else:
        cx, cy = width / 2.0, height / 2.0

        def dist(i):
            b = boxes[i]
            return math.hypot((b[0] + b[2]) / 2.0 - cx, (b[1] + b[3]) / 2.0 - cy)
        best = min(idx, key=lambda i: (round(dist(i), 6), -scores[i], boxes[i][0]))
    return [tuple(boxes[best])]


def grow_box(box, grow, width, height):
    """Add `grow` pixels on every side, then clip to the picture. Returns ints (x0, y0, x1, y1)."""
    _check_box(box)
    if grow < 0:
        raise ValueError("grow must be 0 or more, got %r" % (grow,))
    if width < 1 or height < 1:
        raise ValueError("the picture size must be at least 1 x 1, got %r x %r" % (width, height))
    x0 = max(0, int(math.floor(box[0] - grow)))
    y0 = max(0, int(math.floor(box[1] - grow)))
    x1 = min(int(width), int(math.ceil(box[2] + grow)))
    y1 = min(int(height), int(math.ceil(box[3] + grow)))
    return (x0, y0, x1, y1)


def ellipse_row_span(box, y):
    """Pixels covered on row y by the ellipse inscribed in the box: (x_start, x_end_exclusive) or None.
    A pixel counts when its centre (x+0.5, y+0.5) is inside the ellipse."""
    x0, y0, x1, y1 = _check_box(box)
    a = (x1 - x0) / 2.0
    b = (y1 - y0) / 2.0
    if a <= 0 or b <= 0:
        return None
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    t = (y + 0.5 - cy) / b
    if abs(t) > 1.0:
        return None
    half = a * math.sqrt(max(0.0, 1.0 - t * t))
    start = int(math.ceil(cx - half - 0.5 - 1e-9))
    end = int(math.floor(cx + half - 0.5 + 1e-9)) + 1
    start = max(start, int(math.ceil(x0)))
    end = min(end, int(math.floor(x1)))
    if end <= start:
        return None
    return (start, end)


def format_boxes(boxes_per_image):
    """One line per image: 'x0,y0,x1,y1;x0,y0,x1,y1'. An image with no face gives an empty line."""
    lines = []
    for boxes in boxes_per_image:
        lines.append(";".join("%d,%d,%d,%d" % tuple(int(round(v)) for v in _check_box(b)) for b in boxes))
    return "\n".join(lines)


def haar_min_neighbors(threshold):
    """Map the threshold (0.05 to 0.99) to the Haar minNeighbors setting (2 to 10)."""
    t = float(threshold)
    if not 0.05 <= t <= 0.99:
        raise ValueError("threshold must be between 0.05 and 0.99, got %r" % (threshold,))
    return int(round(2 + t * 8))


def scale_for(width, height, max_side=MAX_SIDE):
    """Factor (<= 1) that brings the long side down to max_side. 1.0 when the picture is already small enough."""
    long_side = max(width, height)
    return 1.0 if long_side <= max_side else max_side / float(long_side)


def rows_to_boxes(rows, scale, width, height):
    """Turn detector rows (x, y, w, h, ..., score) found on a scaled copy into boxes + scores in original pixels."""
    boxes, scores = [], []
    for r in rows:
        x, y, w, h = r[0] / scale, r[1] / scale, r[2] / scale, r[3] / scale
        x0, y0 = max(0.0, x), max(0.0, y)
        x1, y1 = min(float(width), x + w), min(float(height), y + h)
        if x1 > x0 and y1 > y0:
            boxes.append((x0, y0, x1, y1))
            scores.append(float(r[-1]))
    return boxes, scores


def _not_a_detector(path, why):
    return ValueError("%s is not a face detector OpenCV can read (%s). Use a YuNet-style .onnx file or pick the built-in detector."
                      % (path, why))


def _last_line(e):
    text = str(e).strip()
    return text.splitlines()[-1] if text else "load failed"


def _scaled(cv2, bgr):
    h, w = bgr.shape[0], bgr.shape[1]
    scale = scale_for(w, h)
    if scale < 1.0:
        bgr = cv2.resize(bgr, (max(1, int(round(w * scale))), max(1, int(round(h * scale)))), interpolation=cv2.INTER_AREA)
    return bgr, bgr.shape[1] / float(w)


def detect_yunet(cv2, model_path, bgr, threshold):
    """Run a YuNet-style ONNX face detector. `cv2` is passed in so the code path can be tested with a stand-in."""
    h, w = bgr.shape[0], bgr.shape[1]
    try:
        det = cv2.FaceDetectorYN.create(model_path, "", (w, h), float(threshold), 0.3, 5000)
    except Exception as e:  # cv2.error and friends
        raise _not_a_detector(model_path, _last_line(e))
    if det is None:
        raise _not_a_detector(model_path, "load failed")
    img, sx = _scaled(cv2, bgr)
    det.setInputSize((img.shape[1], img.shape[0]))
    try:
        _, faces = det.detect(img)
    except Exception as e:
        raise _not_a_detector(model_path, _last_line(e))
    if faces is None or len(faces) == 0:
        return [], []
    rows = [[float(v) for v in f] for f in faces]
    for r in rows:
        if len(r) < 15:
            raise _not_a_detector(model_path, "unexpected output size")
    return rows_to_boxes(rows, sx, w, h)


def detect_haar(cv2, bgr, threshold, min_face):
    """Built-in detector: the two Haar cascades that ship inside the opencv package, merged with NMS."""
    h, w = bgr.shape[0], bgr.shape[1]
    img, sx = _scaled(cv2, bgr)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    neighbours = haar_min_neighbors(threshold)
    size = max(8, int(round(min_face * sx)))
    rows = []
    for name in HAAR_FILES:
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + name)
        if cascade.empty():
            raise ValueError("the built-in face file %s was not found inside the opencv package; reinstall opencv-python-headless" % name)
        found, _levels, weights = cascade.detectMultiScale3(gray, scaleFactor=1.1, minNeighbors=neighbours,
                                                           minSize=(size, size), outputRejectLevels=True)
        for i in range(len(found)):
            x, y, bw, bh = [float(v) for v in found[i]]
            try:
                score = float(weights[i])
            except (IndexError, TypeError):
                score = 1.0
            rows.append([x, y, bw, bh, score])
    boxes, scores = rows_to_boxes(rows, sx, w, h)
    keep = nms(boxes, scores, 0.3)
    return [boxes[i] for i in keep], [scores[i] for i in keep]


def build_mask_rows(boxes, shape, width, height):
    """List of (y, x_start, x_end_exclusive) fills for the (already grown) boxes."""
    if shape not in SHAPES:
        raise ValueError("unknown shape %r; choose one of: %s" % (shape, ", ".join(SHAPES)))
    fills = []
    for b in boxes:
        x0, y0, x1, y1 = b
        for y in range(max(0, y0), min(height, y1)):
            if shape == "box":
                fills.append((y, max(0, x0), min(width, x1)))
            else:
                span = ellipse_row_span(b, y)
                if span:
                    fills.append((y, span[0], span[1]))
    return fills


# ---------------------------------------------------------------- node

def _model_files():
    """Names of *.onnx files in models/sy_face_detect. Imports folder_paths lazily; creates nothing."""
    try:
        import os
        import folder_paths
        if not folder_paths.folder_names_and_paths.get(MODEL_FOLDER):
            folder_paths.add_model_folder_path(MODEL_FOLDER, os.path.join(folder_paths.models_dir, MODEL_FOLDER))
        return [n for n in folder_paths.get_filename_list(MODEL_FOLDER) if n.lower().endswith(".onnx")]
    except Exception:
        return []  # ComfyUI not present (selftest) or folder missing: only the built-in entry is offered


def _model_path(name):
    import os
    if ".." in name.replace("\\", "/").split("/") or os.path.isabs(name):
        raise ValueError("the detector name must be a file inside models/%s, got %r" % (MODEL_FOLDER, name))
    import folder_paths
    path = folder_paths.get_full_path(MODEL_FOLDER, name)
    if not path:
        raise ValueError("detector file %r was not found in models/%s; pick another detector" % (name, MODEL_FOLDER))
    return path


class SYFaceDetect:
    DESCRIPTION = ("Finds faces and makes a mask for them (box or oval). Feed the mask to Inpaint Crop SY. "
                   "No face found gives an empty mask and no error.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "INT", "STRING")
    RETURN_NAMES = ("mask", "found", "boxes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to search for faces."}),
                "detector": ([BUILTIN] + _model_files(), {"tooltip": "Built-in needs no file. Or pick a YuNet .onnx from models/sy_face_detect (download link in the README)."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.05, "max": 0.99, "step": 0.01, "tooltip": "Higher = stricter, fewer faces."}),
                "min_face": ("INT", {"default": 32, "min": 8, "max": 1024, "tooltip": "Faces whose shorter side is smaller than this many pixels are ignored."}),
                "pick": (list(PICK_MODES), {"tooltip": "Which faces to keep: the one nearest the middle, the biggest one, or all of them."}),
                "grow": ("INT", {"default": 10, "min": 0, "max": 256, "tooltip": "Pixels added on every side of each face box (kept inside the picture)."}),
                "shape": (list(SHAPES), {"tooltip": "Mask shape: a rectangle, or an oval that fits inside the grown box."}),
            }
        }

    def run(self, image, detector, threshold, min_face, pick, grow, shape):
        import torch
        try:
            import cv2
            import numpy as np
        except ImportError:
            raise ValueError(NEED_CV2)
        if pick not in PICK_MODES:
            raise ValueError("unknown pick mode %r; choose one of: %s" % (pick, ", ".join(PICK_MODES)))
        if shape not in SHAPES:
            raise ValueError("unknown shape %r; choose one of: %s" % (shape, ", ".join(SHAPES)))
        haar_min_neighbors(threshold)  # range check for both back ends
        model_path = None if detector == BUILTIN else _model_path(detector)
        batch, height, width = int(image.shape[0]), int(image.shape[1]), int(image.shape[2])
        masks = torch.zeros((batch, height, width), dtype=torch.float32)
        all_boxes = []
        found_first = 0
        for n in range(batch):
            arr = (image[n, :, :, :3].detach().cpu().clamp(0, 1) * 255.0).round().to(torch.uint8).numpy()
            bgr = np.ascontiguousarray(arr[:, :, ::-1])
            if model_path is None:
                boxes, scores = detect_haar(cv2, bgr, threshold, min_face)
            else:
                boxes, scores = detect_yunet(cv2, model_path, bgr, threshold)
            keep = small_keep(boxes, min_face)
            boxes = [boxes[i] for i in keep]
            scores = [scores[i] for i in keep]
            picked = pick_faces(boxes, scores, width, height, pick)
            grown = [grow_box(b, grow, width, height) for b in picked]
            for (y, xs, xe) in build_mask_rows(grown, shape, width, height):
                masks[n, y, xs:xe] = 1.0
            all_boxes.append(grown)
            if n == 0:
                found_first = len(grown)
        return (masks, found_first, format_boxes(all_boxes))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FaceDetect", SYFaceDetect)
NODE_DISPLAY_NAME_MAPPINGS["SYFaceDetect"] = "Face Detect SY"
