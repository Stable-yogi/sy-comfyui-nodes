"""Orientation SY: tells if an image is landscape, portrait or square, and its size."""

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def classify(width, height, tolerance_percent=0.0):
    """Pure function. Returns 'landscape', 'portrait' or 'square'.
    Square when the two sides differ by no more than tolerance_percent of the longer side."""
    width = int(width)
    height = int(height)
    tol = float(tolerance_percent)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1 (got %dx%d)" % (width, height))
    if tol < 0 or tol > 100:
        raise ValueError("tolerance_percent must be between 0 and 100")
    if abs(width - height) * 100.0 <= tol * max(width, height):
        return "square"
    return "landscape" if width > height else "portrait"


def image_size(image):
    """Reads (width, height) from an IMAGE tensor shaped [batch, height, width, channels]."""
    shape = tuple(image.shape)
    if len(shape) != 4:
        raise ValueError("expected an IMAGE shaped [batch, height, width, channels], got %r" % (shape,))
    return int(shape[2]), int(shape[1])


class SYOrientation:
    DESCRIPTION = "Tells if an image is landscape, portrait or square, and gives its width and height."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "INT", "INT")
    RETURN_NAMES = ("orientation", "is_landscape", "width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to measure. For a batch the first size is used."}),
                "tolerance_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.5, "tooltip": "Sides this close (in percent of the longer side) count as square."}),
            },
        }

    def run(self, image, tolerance_percent=0.0):
        width, height = image_size(image)
        kind = classify(width, height, tolerance_percent)
        return (kind, kind == "landscape", width, height)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Orientation", SYOrientation)
NODE_DISPLAY_NAME_MAPPINGS["SYOrientation"] = "Orientation SY"
