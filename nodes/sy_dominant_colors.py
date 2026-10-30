"""Dominant Colors SY: finds the main colours of a picture and shows them as swatches."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_hexcolour import to_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_hexcolour import to_hex

SWATCH_HEIGHT = 64


def luma709(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def check_settings(count, sample_size):
    if not 1 <= count <= 12:
        raise ValueError("count must be between 1 and 12, got %s" % count)
    if not 16 <= sample_size <= 512:
        raise ValueError("sample_size must be between 16 and 512, got %s" % sample_size)


def sample_dims(width, height, sample_size):
    """Pure function. New (width, height) so the longest side is at most sample_size (never enlarges)."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1")
    longest = max(width, height)
    if longest <= sample_size:
        return width, height
    scale = sample_size / float(longest)
    return max(1, int(width * scale)), max(1, int(height * scale))


def sample_index(dst_i, dst_n, src_n):
    """Pure function. Nearest-neighbour source index for output index dst_i."""
    return min(src_n - 1, int((dst_i + 0.5) * src_n / dst_n))


def _assign(pixels, centres):
    labels = []
    for p in pixels:
        best, best_d = 0, None
        for k, c in enumerate(centres):
            d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
            if best_d is None or d < best_d:  # strict: a tie keeps the lower index
                best, best_d = k, d
        labels.append(best)
    return labels


def kmeans_clusters(pixels, count, rounds=12):
    """Pure function. Deterministic k-means on (r, g, b) tuples.
    Returns [(centre, size)] with exactly `count` entries, biggest first (ties: darker first)."""
    if count < 1:
        raise ValueError("count must be at least 1, got %s" % count)
    if not pixels:
        raise ValueError("the picture has no pixels")
    ordered = sorted(pixels, key=lambda p: (luma709(p), p))
    n = len(ordered)
    centres = [tuple(ordered[min(n - 1, int((i + 0.5) * n / count))]) for i in range(count)]
    for _ in range(rounds):
        labels = _assign(pixels, centres)
        sums = [[0.0, 0.0, 0.0, 0] for _ in range(count)]
        for p, k in zip(pixels, labels):
            s = sums[k]
            s[0] += p[0]
            s[1] += p[1]
            s[2] += p[2]
            s[3] += 1
        centres = [
            (s[0] / s[3], s[1] / s[3], s[2] / s[3]) if s[3] else centres[k]
            for k, s in enumerate(sums)
        ]
    labels = _assign(pixels, centres)
    sizes = [0] * count
    for k in labels:
        sizes[k] += 1
    pairs = list(zip(centres, sizes))
    pairs.sort(key=lambda cs: (-cs[1], luma709(cs[0])))
    return pairs


def kmeans_colours(pixels, count, rounds=12):
    """Pure function. Just the centre colours of kmeans_clusters, biggest share first."""
    return [c for c, _ in kmeans_clusters(pixels, count, rounds)]


class SYDominantColors:
    DESCRIPTION = "Finds the main colours of a picture. Gives a text list of hex colours and a strip of colour swatches."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("hex_list", "swatches")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to read. Only the first picture of a batch is used."}),
                "count": ("INT", {"default": 5, "min": 1, "max": 12, "tooltip": "How many main colours to find."}),
                "sample_size": ("INT", {"default": 128, "min": 16, "max": 512, "tooltip": "The picture is shrunk to this longest side first. Bigger is slower."}),
            }
        }

    def run(self, image, count, sample_size):
        import torch

        need_image(image)
        check_settings(count, sample_size)
        _, h, w, _c = image.shape
        nw, nh = sample_dims(w, h, sample_size)
        ys = torch.tensor([sample_index(i, nh, h) for i in range(nh)], dtype=torch.long)
        xs = torch.tensor([sample_index(i, nw, w) for i in range(nw)], dtype=torch.long)
        small = image[0, :, :, :3].detach().cpu().to(torch.float32)
        small = small.index_select(0, ys).index_select(1, xs)
        pixels = [tuple(row) for row in small.reshape(-1, 3).tolist()]
        colours = kmeans_colours(pixels, int(count))
        hex_list = ", ".join(to_hex(c) for c in colours)
        blocks = [torch.tensor(c, dtype=torch.float32).view(1, 1, 3).expand(SWATCH_HEIGHT, SWATCH_HEIGHT, 3) for c in colours]
        sw = torch.cat(blocks, dim=1).unsqueeze(0).to(image.dtype).contiguous()
        return (hex_list, sw)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DominantColors", SYDominantColors)
NODE_DISPLAY_NAME_MAPPINGS["SYDominantColors"] = "Dominant Colors SY"
