"""Voice Split SY: cuts a long voice file at its pauses into pieces a video model can take one at a time."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_PIECES = 6
WINDOW_SECONDS = 0.05


def plan_cuts(levels, window_seconds, pieces, search_seconds=2.0, max_piece_seconds=15.0):
    """Pure function. levels: loudness of each short window. Cuts the sound into `pieces` parts of about the same
    length, moving each cut to the quietest window within search_seconds of the even point.
    Returns (cut times in seconds, notes)."""
    pieces = int(pieces)
    n = len(levels)
    if n < 1:
        raise ValueError("the voice is empty")
    if not 1 <= pieces <= MAX_PIECES:
        raise ValueError("pieces must be between 1 and %d" % MAX_PIECES)
    if search_seconds < 0:
        raise ValueError("search_seconds cannot be negative")
    total = n * window_seconds
    if total / pieces < 1.0:
        raise ValueError("%.1f s of voice is too short for %d pieces: each piece needs 1 s or more" % (total, pieces))
    reach = int(round(search_seconds / window_seconds))
    cuts, last = [], 0
    for k in range(1, pieces):
        even = int(round(n * k / float(pieces)))
        lo = max(last + int(1.0 / window_seconds), even - reach)
        hi = min(n - int(1.0 / window_seconds) * (pieces - k), even + reach)
        if hi < lo:
            lo = hi = even
        best = min(range(lo, hi + 1), key=lambda i: (levels[min(i, n - 1)], abs(i - even)))
        cuts.append(round(best * window_seconds, 3))
        last = best
    notes = []
    edges = [0.0] + cuts + [round(total, 3)]
    for i in range(pieces):
        length = edges[i + 1] - edges[i]
        if length > max_piece_seconds:
            notes.append("piece %d is %.1f s: more than %.0f s, use more pieces" % (i + 1, length, max_piece_seconds))
    return cuts, notes


def piece_ranges(cuts, total_seconds, overlap_seconds=0.0):
    """Pure function. Returns (start, end) seconds per piece. Every piece after the first starts overlap_seconds
    early, so it carries the voice of the replayed opening of a chained segment."""
    if overlap_seconds < 0:
        raise ValueError("overlap_seconds cannot be negative")
    edges = [0.0] + list(cuts) + [float(total_seconds)]
    out = []
    for i in range(len(edges) - 1):
        start = edges[i] if i == 0 else max(0.0, edges[i] - overlap_seconds)
        out.append((round(start, 3), round(edges[i + 1], 3)))
    return out


def window_levels(wave, rate, window_seconds=WINDOW_SECONDS):
    """wave: tensor [channels, samples]. Returns the RMS level of each window as a list of floats."""
    mono = wave.float().mean(dim=0)
    step = max(1, int(rate * window_seconds))
    usable = (mono.shape[0] // step) * step
    if usable == 0:
        return [float(mono.pow(2).mean().sqrt())]
    chunks = mono[:usable].reshape(-1, step)
    levels = chunks.pow(2).mean(dim=1).sqrt().tolist()
    if mono.shape[0] > usable:
        levels.append(float(mono[usable:].pow(2).mean().sqrt()))
    return levels


class SYVoiceSplit:
    DESCRIPTION = ("Cuts a long voice or song into up to 6 pieces of about the same length, each cut placed in the "
                   "quietest moment near its even point, so no word is cut in half. Feed piece 1 to the first video "
                   "segment, piece 2 to the second and so on. seconds gives each piece's length for the segment.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO",) * MAX_PIECES + ("STRING", "INT", "STRING")
    RETURN_NAMES = tuple("piece_%d" % (i + 1) for i in range(MAX_PIECES)) + ("seconds", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The whole voice or song."}),
                "pieces": ("INT", {"default": 4, "min": 1, "max": MAX_PIECES, "tooltip": "How many pieces. Keep each piece under 15 s: a 50 s voice needs 4 or more."}),
            },
            "optional": {
                "search_seconds": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 6.0, "step": 0.25, "tooltip": "How far a cut may move from the even point to find a pause."}),
                "overlap_seconds": ("FLOAT", {"default": 1.625, "min": 0.0, "max": 4.0, "step": 0.125, "tooltip": "Pieces 2 and later start this much early. Set it to the chain handoff_seconds (1.625)."}),
            },
        }

    def run(self, audio, pieces, search_seconds=2.0, overlap_seconds=1.625):
        wave = audio["waveform"]
        rate = int(audio["sample_rate"])
        if wave.dim() != 3 or wave.shape[-1] < 1 or rate <= 0:
            raise ValueError("audio input is not a sound: connect an AUDIO output (for example Load Audio)")
        total = wave.shape[-1] / float(rate)
        cuts, notes = plan_cuts(window_levels(wave[0], rate), WINDOW_SECONDS, pieces, search_seconds)
        ranges = piece_ranges(cuts, total, overlap_seconds)
        outs, secs = [], []
        for start, end in ranges:
            a, b = int(round(start * rate)), int(round(end * rate))
            outs.append({"waveform": wave[..., a:b].contiguous(), "sample_rate": rate})
            secs.append(end - start)
        while len(outs) < MAX_PIECES:
            outs.append({"waveform": wave[..., :max(1, rate // 10)] * 0.0, "sample_rate": rate})
        info = "%.2f s voice, %d pieces, cuts at %s s" % (total, len(ranges), ", ".join("%.2f" % c for c in cuts) or "none")
        if notes:
            info += "\n" + "\n".join(notes)
        seconds = ", ".join("%.3f" % s for s in secs)
        return tuple(outs) + (seconds, len(ranges), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VoiceSplit", SYVoiceSplit)
NODE_DISPLAY_NAME_MAPPINGS["SYVoiceSplit"] = "Voice Split SY"
