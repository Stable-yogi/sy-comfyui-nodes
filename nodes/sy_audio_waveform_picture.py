"""Audio Waveform Picture SY: draws a sound as a picture."""

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_audio(audio):
    """Pure function. Returns (batch, channels, samples, sample_rate) or raises ValueError."""
    if not isinstance(audio, dict) or "waveform" not in audio or "sample_rate" not in audio:
        raise ValueError("audio input is not a sound: connect an AUDIO output (for example from a Load Audio node)")
    shape = tuple(audio["waveform"].shape)
    rate = int(audio["sample_rate"])
    if len(shape) != 3:
        raise ValueError("audio has an odd shape %s: expected batch, channels, samples" % (shape,))
    if rate <= 0:
        raise ValueError("sample rate is %d: it must be above zero" % rate)
    if shape[0] < 1 or shape[1] < 1 or shape[2] < 1:
        raise ValueError("audio is empty: it needs at least one sample. Check the node that makes the sound")
    return shape[0], shape[1], shape[2], rate

STYLES = ("bars", "line", "filled")
CHANNEL_MODES = ("mixed", "each channel")
BAR_WIDTH = 3   # bars style: each bar is this many pixels wide, followed by a 1 pixel gap


def column_extremes(samples, width):
    """Pure function. (min, max) of each of `width` near-equal chunks of the list, left to right.
    If there are fewer samples than columns, neighbouring columns share a sample."""
    n = len(samples)
    if n < 1:
        raise ValueError("no samples to draw")
    if width < 1:
        raise ValueError("width is %s: it must be 1 or more" % width)
    out = []
    for c in range(width):
        s = (c * n) // width
        e = ((c + 1) * n) // width
        if e <= s:
            e = s + 1
        chunk = samples[s:e]
        out.append((min(chunk), max(chunk)))
    return out


def value_to_row(v, height):
    """Pure function. Sample value -1..1 to a pixel row (0 = top). 0 lands on the centre row."""
    v = min(1.0, max(-1.0, v))
    return int(round((1.0 - v) / 2.0 * (height - 1)))


def column_rows(extremes, height):
    """Pure function. (top_row, bottom_row) to colour for each column. Always at least one row (silence = centre line)."""
    if height < 1:
        raise ValueError("height is %s: it must be 1 or more" % height)
    return [(value_to_row(mx, height), value_to_row(mn, height)) for (mn, mx) in extremes]


def bar_extremes(samples, width):
    """Pure function. Extremes per pixel column for the bars style: one symmetric bar every BAR_WIDTH+1 pixels."""
    if width <= BAR_WIDTH + 1:
        return [(-max(abs(a), abs(b)), max(abs(a), abs(b))) for a, b in column_extremes(samples, width)]
    nb = max(1, width // (BAR_WIDTH + 1))
    bars = column_extremes(samples, nb)
    out = []
    for a, b in bars:
        m = max(abs(a), abs(b))
        out.extend([(-m, m)] * BAR_WIDTH + [(0.0, 0.0)])
    out.extend([(0.0, 0.0)] * (width - len(out)))
    return out[:width]


def bar_gaps(width):
    """Pure function. Columns that stay empty in the bars style."""
    if width <= BAR_WIDTH + 1:
        return set()
    nb = width // (BAR_WIDTH + 1)
    return set([i * (BAR_WIDTH + 1) + BAR_WIDTH for i in range(nb)] + list(range(nb * (BAR_WIDTH + 1), width)))


def band_layout(height, bands):
    """Pure function. (start_row, band_height) for each band when the picture is split top to bottom."""
    if bands < 1:
        raise ValueError("need at least one band")
    if height // bands < 2:
        raise ValueError("height %d is too small for %d channels: make it bigger or use 'mixed'" % (height, bands))
    base = height // bands
    out = []
    pos = 0
    for i in range(bands):
        h = base if i < bands - 1 else height - pos
        out.append((pos, h))
        pos += h
    return out


class SYAudioWaveformPicture:
    DESCRIPTION = ("Draws a sound as a picture: bars, a line or a filled shape in the colour you pick. "
                   "A silent sound gives a flat line in the middle. Useful for videos and checks.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to draw."}),
                "width": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 1, "tooltip": "Picture width in pixels. The whole sound is squeezed into it."}),
                "height": ("INT", {"default": 256, "min": 32, "max": 2048, "step": 1, "tooltip": "Picture height in pixels."}),
                "style": (list(STYLES), {"default": "filled", "tooltip": "Bars: separate bars. Line: only the outline. Filled: a solid shape."}),
                "wave_colour_r": ("FLOAT", {"default": 0.83, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Red part of the wave colour. 0 = none, 1 = full."}),
                "wave_colour_g": ("FLOAT", {"default": 0.65, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Green part of the wave colour. 0 = none, 1 = full."}),
                "wave_colour_b": ("FLOAT", {"default": 0.22, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Blue part of the wave colour. 0 = none, 1 = full."}),
                "background_grey": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Grey level of the background. 0 = black, 1 = white."}),
                "channels": (list(CHANNEL_MODES), {"default": "mixed", "tooltip": "Mixed: one wave for all channels. Each channel: one wave per channel, stacked top to bottom."}),
            }
        }

    def run(self, audio, width, height, style, wave_colour_r, wave_colour_g, wave_colour_b, background_grey, channels):
        import torch
        _b, c, n, _rate = check_audio(audio)
        if style not in STYLES:
            raise ValueError("unknown style %r: pick one of %s" % (style, ", ".join(STYLES)))
        if channels not in CHANNEL_MODES:
            raise ValueError("unknown channels option %r: pick one of %s" % (channels, ", ".join(CHANNEL_MODES)))
        wave = audio["waveform"][0].float()
        if channels == "mixed" or c == 1:
            tracks = [wave.mean(dim=0)]
        else:
            tracks = [wave[i] for i in range(c)]
        layout = band_layout(height, len(tracks))
        img = torch.full((height, width, 3), float(background_grey), dtype=torch.float32)
        colour = torch.tensor([wave_colour_r, wave_colour_g, wave_colour_b], dtype=torch.float32)
        gaps = bar_gaps(width) if style == "bars" else set()
        for track, (y0, bh) in zip(tracks, layout):
            # column extremes by chunk; use vector min/max per chunk to stay fast on long sounds
            if style == "bars":
                ext = bar_extremes_tensor(track, width, torch)
            else:
                ext = extremes_tensor(track, width, torch)
            rows = column_rows(ext, bh)
            for x in range(width):
                if x in gaps:
                    continue
                top, bottom = rows[x]
                if style == "line":
                    for r in (top, bottom):
                        img[y0 + r, x] = colour
                else:
                    img[y0 + top:y0 + bottom + 1, x] = colour
        return (img.unsqueeze(0).contiguous(),)


def extremes_tensor(track, width, torch):
    """Same as column_extremes but for a 1-D tensor. Returns a list of (min, max)."""
    n = int(track.shape[0])
    if n >= width:
        edges = [(c * n) // width for c in range(width + 1)]
        return [(float(track[edges[i]:edges[i + 1]].min()), float(track[edges[i]:edges[i + 1]].max())) for i in range(width)]
    return column_extremes(track.tolist(), width)


def bar_extremes_tensor(track, width, torch):
    """Same as bar_extremes but for a 1-D tensor."""
    if width <= BAR_WIDTH + 1:
        return [(-max(abs(a), abs(b)), max(abs(a), abs(b))) for a, b in extremes_tensor(track, width, torch)]
    nb = max(1, width // (BAR_WIDTH + 1))
    out = []
    for a, b in extremes_tensor(track, nb, torch):
        m = max(abs(a), abs(b))
        out.extend([(-m, m)] * BAR_WIDTH + [(0.0, 0.0)])
    out.extend([(0.0, 0.0)] * (width - len(out)))
    return out[:width]


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioWaveformPicture", SYAudioWaveformPicture)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioWaveformPicture"] = "Audio Waveform Picture SY"
