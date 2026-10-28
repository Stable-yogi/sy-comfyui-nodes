"""Image Hash Duplicate SY: compares two pictures with a small average hash and says if they are near duplicates."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def average_hash(gray, size=8):
    """Pure function. gray is a list of rows of brightness numbers. Returns size*size bits (0 or 1):
    the grid is shrunk to size x size by block averages, then each cell is 1 when brighter than the overall average."""
    if size < 2:
        raise ValueError("hash size must be at least 2 (got %s)" % size)
    h = len(gray)
    if h == 0 or len(gray[0]) == 0:
        raise ValueError("the picture has no pixels")
    w = len(gray[0])
    cells = []
    for i in range(size):
        y0 = min(h - 1, i * h // size)
        y1 = max(y0 + 1, min(h, (i + 1) * h // size))
        for j in range(size):
            x0 = min(w - 1, j * w // size)
            x1 = max(x0 + 1, min(w, (j + 1) * w // size))
            total = 0.0
            for y in range(y0, y1):
                row = gray[y]
                for x in range(x0, x1):
                    total += row[x]
            cells.append(total / ((y1 - y0) * (x1 - x0)))
    mean = sum(cells) / len(cells)
    return [1 if c > mean else 0 for c in cells]


def hamming(a, b):
    """Pure function. Number of positions where two equal-length bit lists differ."""
    if len(a) != len(b):
        raise ValueError("hashes have different lengths (%d and %d); use the same hash size" % (len(a), len(b)))
    return sum(1 for x, y in zip(a, b) if x != y)


def compare_grids(gray_a, gray_b, size=8, threshold=5):
    """Pure function. Returns (distance, is_duplicate, report). Duplicate means distance <= threshold."""
    if threshold < 0:
        raise ValueError("threshold must be 0 or more (got %s)" % threshold)
    d = hamming(average_hash(gray_a, size), average_hash(gray_b, size))
    total = size * size
    dup = d <= threshold
    report = "%s: %d of %d hash bits differ (limit %d)." % ("near duplicate" if dup else "different pictures", d, total, threshold)
    return d, dup, report


def tensor_to_gray(image, size):
    """First picture of a [B,H,W,C] tensor -> brightness rows, shrunk to (size*4) x (size*4). torch is imported here."""
    import torch

    img = image[0, ..., :3].float()
    if img.shape[-1] == 3:
        gray = img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114
    else:
        gray = img.mean(dim=-1)
    pooled = torch.nn.functional.adaptive_avg_pool2d(gray[None, None], (size * 4, size * 4))[0, 0]
    return pooled.tolist()


class SYImageHashDuplicate:
    DESCRIPTION = "Compares two pictures with a small fingerprint. Tells you how different they are and if they are near duplicates."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("distance", "near_duplicate", "report")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE", {"tooltip": "First picture. If it is a batch, the first picture of the batch is used."}),
                "image_b": ("IMAGE", {"tooltip": "Second picture. If it is a batch, the first picture of the batch is used."}),
                "hash_size": ("INT", {"default": 8, "min": 4, "max": 32, "tooltip": "Fingerprint grid size. 8 gives 64 bits. Bigger notices smaller differences."}),
                "threshold": ("INT", {"default": 5, "min": 0, "max": 1024, "tooltip": "Largest number of differing bits that still counts as a near duplicate."}),
            }
        }

    def run(self, image_a, image_b, hash_size, threshold):
        return compare_grids(tensor_to_gray(image_a, hash_size), tensor_to_gray(image_b, hash_size), hash_size, threshold)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageHashDuplicate", SYImageHashDuplicate)
NODE_DISPLAY_NAME_MAPPINGS["SYImageHashDuplicate"] = "Image Hash Duplicate Check SY"
