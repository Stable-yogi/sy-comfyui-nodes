"""Upscale SY: loads an upscale model and enlarges pictures or video frames to a size you choose, in safe chunks."""
try:
    from ._sy_common import category, register
    from ._sy_core_call import core, is_out_of_memory
    from ._sy_model_files import list_names, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core, is_out_of_memory
    from _sy_model_files import list_names, NONE_NAME

TARGETS = ["Keep the model's size", "Longest side", "Width", "Height", "Megapixels"]
METHODS = ["lanczos", "bicubic", "bilinear", "area", "nearest-exact"]


def target_size(width, height, target, amount):
    """Pure function. The final (width, height), both even, keeping the shape. `amount` is pixels (or megapixels)."""
    width, height = int(width), int(height)
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1, got %dx%d" % (width, height))
    if target not in TARGETS:
        raise ValueError("target must be one of %s, got %r" % (TARGETS, target))
    if target == TARGETS[0]:
        return width, height
    if amount <= 0:
        raise ValueError("the target amount must be above 0")
    if target == TARGETS[1]:
        scale = amount / float(max(width, height))
    elif target == TARGETS[2]:
        scale = amount / float(width)
    elif target == TARGETS[3]:
        scale = amount / float(height)
    else:
        scale = (amount * 1000000.0 / (width * height)) ** 0.5
    return max(2, int(round(width * scale / 2.0)) * 2), max(2, int(round(height * scale / 2.0)) * 2)


def chunk_ranges(count, chunk):
    """Pure function. Splits `count` frames into (start, end) pieces of at most `chunk` frames."""
    count, chunk = int(count), int(chunk)
    if count < 1 or chunk < 1:
        raise ValueError("frame count and chunk size must be at least 1")
    return [(s, min(count, s + chunk)) for s in range(0, count, chunk)]


def info_text(model_name, src, model_out, final, chunk, tries):
    """Pure function. One line telling what happened."""
    how = "plain resize (no model)" if model_name == NONE_NAME else "model %s" % model_name
    parts = ["%dx%d -> %dx%d" % (src[0], src[1], final[0], final[1]), how]
    if model_out != final and model_name != NONE_NAME:
        parts.append("model made %dx%d, then resized" % (model_out[0], model_out[1]))
    parts.append("chunks of %d frame(s)" % chunk)
    if tries > 1:
        parts.append("memory ran short, %d tries" % tries)
    return ", ".join(parts)


def _model_pass(model, images, chunk):
    """Runs the upscale model over the frames in chunks. Halves the chunk on a memory error. Returns (frames, chunk, tries)."""
    import torch
    tries = 0
    while True:
        tries += 1
        try:
            pieces = []
            for a, b in chunk_ranges(images.shape[0], chunk):
                pieces.append(core("ImageUpscaleWithModel", "Upscale SY", upscale_model=model, image=images[a:b])[0].cpu())
            return torch.cat(pieces, dim=0), chunk, tries
        except Exception as e:
            if not is_out_of_memory(e) or chunk <= 1:
                raise
            chunk = max(1, chunk // 2)
            try:
                import comfy.model_management as mm
                mm.soft_empty_cache()
            except Exception:
                pass


def _resize(images, width, height, method):
    import comfy.utils
    if (images.shape[2], images.shape[1]) == (width, height):
        return images
    return comfy.utils.common_upscale(images.movedim(-1, 1), width, height, method, "disabled").movedim(1, -1)


class SYUpscale:
    DESCRIPTION = ("Picks an upscale model, enlarges a picture or video frames, and lands on the exact size you want "
                   "(longest side, width, height or megapixels). Video frames go through in chunks, and a chunk is halved "
                   "by itself if the card runs out of memory. Model on None = plain resize.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or the video frames to enlarge."}),
                "upscale_model": ([NONE_NAME] + list_names("upscale_models"), {"tooltip": "The upscale model file. None = plain resize only."}),
                "target": (TARGETS, {"default": TARGETS[1], "tooltip": "What the amount below means. 'Keep the model's size' uses the size the model gives."}),
                "amount": ("FLOAT", {"default": 2048.0, "min": 0.0, "max": 32768.0, "step": 1.0, "tooltip": "Pixels for side, width and height. Megapixels for the last choice."}),
                "method": (METHODS, {"default": "lanczos", "tooltip": "How the last resize to the exact size is done."}),
                "chunk_frames": ("INT", {"default": 8, "min": 1, "max": 512, "tooltip": "Frames sent through the model at once. Lower = less memory."}),
            }
        }

    def run(self, image, upscale_model, target, amount, method, chunk_frames):
        src = (int(image.shape[2]), int(image.shape[1]))
        final = target_size(src[0], src[1], target, amount) if not (upscale_model == NONE_NAME and target == TARGETS[0]) else src
        if upscale_model == NONE_NAME:
            out = _resize(image, final[0], final[1], method)
            return (out, info_text(upscale_model, src, final, final, int(image.shape[0]), 1))
        model = core("UpscaleModelLoader", "Upscale SY", model_name=upscale_model)[0]
        out, used_chunk, tries = _model_pass(model, image, chunk_frames)
        model_out = (int(out.shape[2]), int(out.shape[1]))
        if target == TARGETS[0]:
            final = model_out
        out = _resize(out, final[0], final[1], method)
        return (out, info_text(upscale_model, src, model_out, final, used_chunk, tries))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Upscale", SYUpscale)
NODE_DISPLAY_NAME_MAPPINGS["SYUpscale"] = "Upscale SY"
