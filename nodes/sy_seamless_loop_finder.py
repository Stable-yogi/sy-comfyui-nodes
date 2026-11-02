"""Seamless Loop Finder SY: finds the pair of frames in a clip where a loop between them is least visible."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MIN_FRAMES = 8
SCORE_SCALE = 100.0


def distance_matrix(features):
    """Pure function. features = one list of numbers (0..1) per frame -> square matrix of mean absolute differences, scaled 0..100."""
    n = len(features)
    if n == 0:
        raise ValueError("no frames to compare")
    size = len(features[0])
    if size == 0 or any(len(f) != size for f in features):
        raise ValueError("every frame must give the same, non-empty list of numbers")
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        fi = features[i]
        for j in range(i + 1, n):
            fj = features[j]
            d = sum(abs(x - y) for x, y in zip(fi, fj)) / size * SCORE_SCALE
            mat[i][j] = mat[j][i] = d
    return mat


def rank_loops(matrix, min_length, max_length, top):
    """Pure function. matrix[i][j] = difference between frame i and j (lower is better).
    Returns up to `top` candidates (score, start, end, length), best first. A loop plays frames start..end-1 and then jumps
    back to start, so frame `end` should look like frame `start`. Near copies of a better candidate are skipped."""
    n = len(matrix)
    min_length = int(min_length)
    max_length = int(max_length)
    top = int(top)
    if n < MIN_FRAMES:
        raise ValueError("need at least %d frames to look for a loop, got %d" % (MIN_FRAMES, n))
    if any(len(row) != n for row in matrix):
        raise ValueError("the difference table must be square")
    if min_length < 2:
        raise ValueError("min_length must be at least 2, got %d" % min_length)
    if top < 1:
        raise ValueError("top must be at least 1, got %d" % top)
    longest = n - 1
    if max_length < 0:
        raise ValueError("max_length must be 0 (whole clip) or more, got %d" % max_length)
    if max_length == 0 or max_length > longest:
        max_length = longest
    if min_length > max_length:
        raise ValueError("no loop fits: min_length %d is longer than the longest loop possible (%d frames). "
                         "Lower min_length or raise max_length" % (min_length, max_length))
    cands = []
    for s in range(n):
        for e in range(s + min_length, min(s + max_length, longest) + 1):
            cands.append((float(matrix[s][e]), s, e, e - s))
    cands.sort(key=lambda c: (c[0], -c[3], c[1]))
    chosen = []
    for c in cands:
        if any(abs(c[1] - k[1]) <= 1 and abs(c[2] - k[2]) <= 1 for k in chosen):
            continue
        chosen.append(c)
        if len(chosen) >= top:
            break
    return chosen


def build_report(cands, total):
    """Pure function. Ranked candidates -> plain text report."""
    lines = ["Best loops in a clip of %d frames (score = mean pixel difference between the first frame and the frame it "
             "jumps back from, scaled 0..100, lower is better):" % total]
    for rank, (score, s, e, length) in enumerate(cands, 1):
        lines.append("%d. frames %d to %d, length %d, score %.3f" % (rank, s, e, length, score))
    return "\n".join(lines)


class SYSeamlessLoopFinder:
    DESCRIPTION = ("Looks through a clip for the start and end frame that look most alike, so a loop between them is "
                   "hardly visible. Gives the frames of the best loop and a ranked list of the best candidates.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("images", "start", "end", "length", "report")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The clip as a batch of frames. At least 8 frames."}),
                "min_length": ("INT", {"default": 24, "min": 2, "max": 100000, "tooltip": "Shortest loop to accept, in frames."}),
                "max_length": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Longest loop to accept, in frames. 0 means up to the whole clip."}),
                "compare_size": ("INT", {"default": 64, "min": 8, "max": 512, "tooltip": "Frames are shrunk to this many pixels on the long side before comparing."}),
                "top": ("INT", {"default": 3, "min": 1, "max": 20, "tooltip": "How many of the best loop candidates to list in the report."}),
            },
        }

    def run(self, images, min_length=24, max_length=0, compare_size=64, top=3):
        import torch
        import torch.nn.functional as F

        if images.dim() != 4:
            raise ValueError("images must be a batch of frames, got %d dimensions" % images.dim())
        n, h, w, _c = images.shape
        if n < MIN_FRAMES:
            raise ValueError("need at least %d frames to look for a loop, got %d" % (MIN_FRAMES, n))
        compare_size = max(1, int(compare_size))
        scale = compare_size / float(max(h, w))
        th, tw = max(1, round(h * scale)), max(1, round(w * scale))
        feats = []
        with torch.no_grad():
            for i in range(0, n, 32):
                chunk = images[i:i + 32, :, :, :3].permute(0, 3, 1, 2).float().cpu()
                if (th, tw) != (h, w):
                    chunk = F.interpolate(chunk, size=(th, tw), mode="area")
                feats.append(chunk.reshape(chunk.shape[0], -1))
            flat = torch.cat(feats, 0)
            dist = torch.cdist(flat, flat, p=1) / flat.shape[1] * SCORE_SCALE
        cands = rank_loops(dist.tolist(), min_length, max_length, top)
        _score, s, e, length = cands[0]
        return (images[s:e], s, e, length, build_report(cands, n))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SeamlessLoopFinder", SYSeamlessLoopFinder)
NODE_DISPLAY_NAME_MAPPINGS["SYSeamlessLoopFinder"] = "Seamless Loop Finder SY"
