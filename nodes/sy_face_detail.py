"""Face Detail SY: finds each face, redraws it at a better size with a short second sampling pass, pastes it back softly.
Chain: picture + model + vae + prompts -> Face Detail SY -> picture. No face found leaves the picture as it is (no error)."""
import math

try:
    from ._sy_common import category, register
    from .sy_face_detect import (BUILTIN, PICK_MODES, NEED_CV2, small_keep, pick_faces, detect_haar, detect_yunet,
                                 _model_files, _model_path)
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from sy_face_detect import (BUILTIN, PICK_MODES, NEED_CV2, small_keep, pick_faces, detect_haar, detect_yunet,
                                _model_files, _model_path)

DETECT_THRESHOLD = 0.5
FALLBACK_SAMPLERS = ("euler", "euler_ancestral", "dpmpp_2m", "dpmpp_sde", "uni_pc")
FALLBACK_SCHEDULERS = ("normal", "karras", "simple", "sgm_uniform", "beta")
MAX_SEED = 0xFFFFFFFFFFFFFFFF
NO_FACE_TEXT = "No face found. The picture was left as it is."


# ---------------------------------------------------------------- pure functions
# A box is (x0, y0, x1, y1) in pixels, x1 and y1 exclusive.

def expand_box(box, padding, width, height):
    """Square crop around a face box. The side is the longer box side times (1 + padding), centred on the box.
    Returns (inside, pads): `inside` = (x0, y0, x1, y1) of the part that lies inside the picture;
    `pads` = (left, top, right, bottom) pixels where the square leaves the picture (fill them with edge pixels).
    The full square is inside + pads: side = (x1 - x0) + left + right = (y1 - y0) + top + bottom."""
    if len(box) != 4:
        raise ValueError("a box needs 4 numbers (x0, y0, x1, y1), got %r" % (box,))
    if padding < 0:
        raise ValueError("padding must be 0 or more, got %r" % (padding,))
    if width < 1 or height < 1:
        raise ValueError("the picture size must be at least 1 x 1, got %r x %r" % (width, height))
    bw, bh = box[2] - box[0], box[3] - box[1]
    if bw <= 0 or bh <= 0:
        raise ValueError("the face box has no size: %r" % (tuple(box),))
    side = max(2, int(round(max(bw, bh) * (1.0 + float(padding)))))
    cx, cy = (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0
    x0 = int(round(cx - side / 2.0))
    y0 = int(round(cy - side / 2.0))
    x1, y1 = x0 + side, y0 + side
    ix0, iy0 = max(0, x0), max(0, y0)
    ix1, iy1 = min(int(width), x1), min(int(height), y1)
    if ix1 <= ix0 or iy1 <= iy0:
        raise ValueError("the face box %r lies outside the %dx%d picture" % (tuple(box), width, height))
    pads = (ix0 - x0, iy0 - y0, x1 - ix1, y1 - iy1)
    return (ix0, iy0, ix1, iy1), pads


def _smooth(t):
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return t * t * (3.0 - 2.0 * t)


def feather_weight(i, j, size, feather):
    """Weight of pixel row i, column j in a size x size square: an ellipse (circle) inside the square.
    0 outside the ellipse, 1 in the middle, a smooth fall over `feather` pixels inward. feather 0 = hard ellipse."""
    r = size / 2.0
    d = r - math.hypot(i + 0.5 - r, j + 0.5 - r)
    if d <= 0.0:
        return 0.0
    if feather <= 0:
        return 1.0
    return _smooth(d / min(float(feather), r))


def feather_profile(size, feather):
    """2D list (size rows of size values) of 0..1: the soft ellipse used to paste a redrawn face back."""
    if size < 1:
        raise ValueError("size must be at least 1, got %r" % (size,))
    if feather < 0:
        raise ValueError("feather must be 0 or more, got %r" % (feather,))
    return [[feather_weight(i, j, size, feather) for j in range(size)] for i in range(size)]


def face_seed(seed, index):
    """Seed for the face number `index` (0, 1, ...): the seed plus the index, kept inside the allowed range."""
    if index < 0:
        raise ValueError("the face number must be 0 or more, got %r" % (index,))
    return (int(seed) + int(index)) & MAX_SEED


def plan_faces(boxes, scores, pick, min_face, picture_size):
    """Which faces to redraw: drop faces whose short side is under min_face, then apply the pick mode.
    picture_size = (width, height). Returns a list of boxes."""
    if pick not in PICK_MODES:
        raise ValueError("unknown pick mode %r; choose one of: %s" % (pick, ", ".join(PICK_MODES)))
    if min_face < 1:
        raise ValueError("min_face must be at least 1, got %r" % (min_face,))
    if len(boxes) != len(scores):
        raise ValueError("boxes and scores must have the same length (%d and %d)" % (len(boxes), len(scores)))
    keep = small_keep(boxes, min_face)
    kept_boxes = [boxes[i] for i in keep]
    kept_scores = [scores[i] for i in keep]
    return pick_faces(kept_boxes, kept_scores, picture_size[0], picture_size[1], pick)


def check_settings(crop_size, padding, denoise, steps, cfg, feather, min_face):
    if not 256 <= int(crop_size) <= 2048:
        raise ValueError("crop_size must be between 256 and 2048, got %r" % (crop_size,))
    if not 0.0 <= float(padding) <= 2.0:
        raise ValueError("padding must be between 0 and 2, got %r" % (padding,))
    if not 0.0 <= float(denoise) <= 1.0:
        raise ValueError("denoise must be between 0 and 1, got %r" % (denoise,))
    if int(steps) < 1:
        raise ValueError("steps must be at least 1, got %r" % (steps,))
    if float(cfg) < 0.0:
        raise ValueError("cfg must be 0 or more, got %r" % (cfg,))
    if not 0 <= int(feather) <= 128:
        raise ValueError("feather must be between 0 and 128, got %r" % (feather,))
    if not 16 <= int(min_face) <= 512:
        raise ValueError("min_face must be between 16 and 512, got %r" % (min_face,))


def info_text(counts, crop_size, denoise, steps):
    """One sentence for the info output. counts = faces redrawn per picture in the batch."""
    total = sum(counts)
    if total == 0:
        return NO_FACE_TEXT
    if len(counts) == 1:
        where = ""
    else:
        where = " (" + ", ".join("picture %d: %d" % (i + 1, c) for i, c in enumerate(counts)) + ")"
    return "Face Detail: redrew %d face%s%s at %d px, %d steps, denoise %.2f." % (
        total, "" if total == 1 else "s", where, crop_size, steps, denoise)


# ---------------------------------------------------------------- torch helpers (imported lazily)

def _feather_tensor(size, feather):
    """Same numbers as feather_profile, built with torch in one go (a 1500 px square in python lists is slow)."""
    import torch
    r = size / 2.0
    c = torch.arange(size, dtype=torch.float64) + 0.5 - r
    dist = torch.sqrt(c[:, None] ** 2 + c[None, :] ** 2)
    d = r - dist
    if feather <= 0:
        w = (d > 0).to(torch.float64)
    else:
        t = (d / min(float(feather), r)).clamp(0.0, 1.0)
        w = t * t * (3.0 - 2.0 * t)
        w = torch.where(d > 0, w, torch.zeros_like(w))
    return w.to(torch.float32)


def _resize(x, size):
    """x: [1, C, H, W] -> [1, C, size, size]. Area when shrinking, bicubic when growing."""
    import torch.nn.functional as F
    if x.shape[-1] == size and x.shape[-2] == size:
        return x
    if x.shape[-1] >= size and x.shape[-2] >= size:
        return F.interpolate(x, size=(size, size), mode="area")
    return F.interpolate(x, size=(size, size), mode="bicubic", align_corners=False).clamp(0.0, 1.0)


def _detect(rgb, detector, min_face):
    """rgb: uint8 numpy array [H, W, 3]. Returns (boxes, scores) from the same detectors Face Detect SY uses."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ValueError(NEED_CV2)
    bgr = np.ascontiguousarray(rgb[:, :, ::-1])
    if detector == BUILTIN:
        return detect_haar(cv2, bgr, DETECT_THRESHOLD, min_face)
    return detect_yunet(cv2, _model_path(detector), bgr, DETECT_THRESHOLD)


def _sampler_lists():
    try:
        import comfy.samplers
        return list(comfy.samplers.KSampler.SAMPLERS), list(comfy.samplers.KSampler.SCHEDULERS)
    except Exception:
        return list(FALLBACK_SAMPLERS), list(FALLBACK_SCHEDULERS)


def _prepare_mask(mask, batch, height, width):
    """Bring an optional mask to [batch, height, width] floats, or None."""
    import torch
    import torch.nn.functional as F
    if mask is None:
        return None
    if mask.ndim == 2:
        mask = mask.unsqueeze(0)
    if mask.ndim != 3:
        raise ValueError("mask must be a MASK shaped [batch, height, width]")
    if mask.shape[0] not in (1, batch):
        raise ValueError("mask batch has %d, but the picture batch has %d; use 1 or the same number" % (mask.shape[0], batch))
    if mask.shape[1] != height or mask.shape[2] != width:
        mask = F.interpolate(mask.unsqueeze(1).float(), size=(height, width), mode="bilinear", align_corners=False).squeeze(1)
    mask = mask.float().clamp(0.0, 1.0)
    if mask.shape[0] == 1 and batch > 1:
        mask = mask.expand(batch, -1, -1)
    return mask


# ---------------------------------------------------------------- node

class SYFaceDetail:
    DESCRIPTION = ("Finds each face, redraws it bigger with a short second pass of the sampler, and blends it back softly. "
                   "No face found leaves the picture as it is.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "IMAGE", "MASK", "INT", "STRING")
    RETURN_NAMES = ("image", "face_crops", "mask", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        samplers, schedulers = _sampler_lists()
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures whose faces should get more detail."}),
                "model": ("MODEL", {"tooltip": "The model used to redraw each face."}),
                "vae": ("VAE", {"tooltip": "Turns the face crop into latent data and back into a picture."}),
                "positive": ("CONDITIONING", {"tooltip": "What the redrawn face should look like."}),
                "negative": ("CONDITIONING", {"tooltip": "What the redrawn face should avoid."}),
                "detector": ([BUILTIN] + _model_files(), {"tooltip": "Built-in needs no file. Or pick a YuNet .onnx from models/sy_face_detect."}),
                "pick": (list(PICK_MODES), {"default": "largest 1", "tooltip": "Which faces to redraw: the biggest one, the one nearest the middle, or all."}),
                "crop_size": ("INT", {"default": 768, "min": 256, "max": 2048, "step": 64, "tooltip": "The size in pixels each face is redrawn at."}),
                "padding": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "Extra picture around the face, as a fraction of the face box."}),
                "denoise": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much the face is changed. Low keeps the face, high redraws it."}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 200, "tooltip": "Number of sampling steps for each face."}),
                "cfg": ("FLOAT", {"default": 6.0, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "How strongly the sampler follows the prompt."}),
                "sampler_name": (samplers, {"tooltip": "The sampling method."}),
                "scheduler": (schedulers, {"tooltip": "How the noise steps are spread."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "control_after_generate": True, "tooltip": "Random seed. Each face after the first uses the seed plus its number."}),
                "feather": ("INT", {"default": 24, "min": 0, "max": 128, "tooltip": "Soft edge in pixels where the new face blends into the old picture."}),
                "min_face": ("INT", {"default": 48, "min": 16, "max": 512, "tooltip": "Faces whose shorter side is smaller than this many pixels are ignored."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "Optional. Only change the white area of this mask."}),
            },
        }

    def run(self, image, model, vae, positive, negative, detector, pick, crop_size, padding, denoise, steps, cfg,
            sampler_name, scheduler, seed, feather, min_face, mask=None):
        import torch
        import torch.nn.functional as F
        import nodes as comfy_nodes

        if getattr(image, "ndim", 0) != 4 or image.shape[0] < 1:
            raise ValueError("expected a picture batch shaped [batch, height, width, channels] with at least one picture")
        if image.shape[-1] < 3:
            raise ValueError("the picture needs at least 3 colour channels (red, green, blue)")
        check_settings(crop_size, padding, denoise, steps, cfg, feather, min_face)
        if pick not in PICK_MODES:
            raise ValueError("unknown pick mode %r; choose one of: %s" % (pick, ", ".join(PICK_MODES)))
        samplers, schedulers = _sampler_lists()
        if sampler_name not in samplers:
            raise ValueError("unknown sampler %r; pick one from the list" % (sampler_name,))
        if scheduler not in schedulers:
            raise ValueError("unknown scheduler %r; pick one from the list" % (scheduler,))

        batch, height, width = int(image.shape[0]), int(image.shape[1]), int(image.shape[2])
        masks_in = _prepare_mask(mask, batch, height, width)
        result = image.clone()
        changed = torch.zeros((batch, height, width), dtype=torch.float32)
        crops = []
        counts = []
        face_no = 0
        for n in range(batch):
            rgb = (image[n, :, :, :3].detach().cpu().clamp(0, 1) * 255.0).round().to(torch.uint8).numpy()
            boxes, scores = _detect(rgb, detector, min_face)
            picked = plan_faces(boxes, scores, pick, min_face, (width, height))
            done = 0
            for box in picked:
                inside, pads = expand_box(box, padding, width, height)
                x0, y0, x1, y1 = inside
                if masks_in is not None and float(masks_in[n, y0:y1, x0:x1].max()) <= 0.0:
                    continue  # the face lies outside the allowed area
                pl, pt, pr, pb = pads
                side = (x1 - x0) + pl + pr
                piece = result[n:n + 1, y0:y1, x0:x1, :3].permute(0, 3, 1, 2).float()
                if pl or pt or pr or pb:
                    piece = F.pad(piece, (pl, pr, pt, pb), mode="replicate")
                resized = _resize(piece, int(crop_size)).permute(0, 2, 3, 1).contiguous()
                latent = {"samples": vae.encode(resized)}
                out = comfy_nodes.common_ksampler(model, face_seed(seed, face_no), int(steps), float(cfg), sampler_name,
                                                  scheduler, positive, negative, latent, denoise=float(denoise))
                decoded = vae.decode(out[0]["samples"])
                if decoded.ndim == 5:
                    decoded = decoded.reshape(-1, *decoded.shape[-3:])
                decoded = decoded[:1, :, :, :3].detach().to(image.device).float().clamp(0.0, 1.0)
                crops.append(decoded.cpu())
                back = _resize(decoded.permute(0, 3, 1, 2), side)
                back = back[:, :, pt:pt + (y1 - y0), pl:pl + (x1 - x0)]
                w = _feather_tensor(side, int(feather)).to(image.device)[pt:pt + (y1 - y0), pl:pl + (x1 - x0)]
                if masks_in is not None:
                    w = w * masks_in[n, y0:y1, x0:x1].to(image.device)
                old = result[n, y0:y1, x0:x1, :3].permute(2, 0, 1)
                new = old + (back[0] - old) * w.unsqueeze(0)
                result[n, y0:y1, x0:x1, :3] = new.permute(1, 2, 0).to(result.dtype)
                changed[n, y0:y1, x0:x1] = torch.maximum(changed[n, y0:y1, x0:x1], w.detach().cpu())
                face_no += 1
                done += 1
            counts.append(done)
        if crops:
            face_crops = torch.cat(crops, dim=0)
        else:
            face_crops = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
        return (result, face_crops, changed, sum(counts), info_text(counts, int(crop_size), float(denoise), int(steps)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FaceDetail", SYFaceDetail)
