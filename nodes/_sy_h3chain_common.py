"""H3 chain helpers: frame maths, seeds, autogrow ordering and the summary text. Pure Python, no torch.

Ported from: ComfyUI-H3-Continuous (https://github.com/loopforge0/ComfyUI-H3-Continuous)
Original author: Loop Forge. Licence: MIT (copy in third_party/ComfyUI-H3-Continuous/LICENSE).
Copyright (c) 2026 Loop Forge.
Changed by Stable Yogi (renamed, SY standard; the ComfyUI and torch parts moved to _sy_h3chain_engine.py;
the seed rule, the segment builder and the summary text moved here from nodes.py as pure functions;
bad input raises ValueError with plain words).
"""
import logging

FPS = 24
AUDIO_LATENT_FPS = 40
HANDOFF_MODES = ("latent", "pixel")
REF_IMAGE_SIZES = ("match", "max")
SEED_PRIME = 9973  # prime, so neighbouring segments never collide on a nearby chain seed
SEED_MOD = 1 << 63


def log(msg, *args):
    logging.info("[SY H3 Chain] " + msg, *args)


def generation_length(frames):
    """Snap a frame count UP onto H3's 17k+5 grid.

    H3 only generates 5, 22, 39, ... 124, 141, ... frames. The trained range is
    124-362 (about 5-15 s at 24 fps); shorter and longer both work but degrade.
    """
    frames = max(5, int(round(frames)))
    while frames % 17 != 5:
        frames += 1
    return frames


def guide_length(frames):
    """Snap a guide-clip frame count DOWN onto the same grid.

    The core guide node truncates guide clips to 17k+5 internally. Doing it here
    too means the handoff length we record in the manifest is the length actually
    anchored, so the join arithmetic and the anchor agree to the frame.
    """
    frames = int(round(frames))
    if frames < 5:
        return 0
    while frames % 17 != 5:
        frames -= 1
    return frames


def seconds_to_frames(seconds):
    return int(round(float(seconds) * FPS))


def audio_latent_frames(frames):
    """Audio latent steps covering ``frames`` pixel frames (H3 audio runs at 40 Hz against 24 fps video)."""
    return int(round(float(frames) / FPS * AUDIO_LATENT_FPS))


def latent_cover_frames(steps):
    """Pixel frames covered by ``steps`` video latent steps: step 0 of every 5 covers 1 frame, the rest 4."""
    return sum(1 if k % 5 == 0 else 4 for k in range(int(steps)))


def ordered_autogrow(values):
    """Autogrow inputs arrive as ``{"image_0": t, "image_3": t}``; return them in
    ordinal order, dropping unconnected slots but keeping the ordinal for pairing."""
    out = []
    for name, value in (values or {}).items():
        if value is None:
            continue
        tail = name.rsplit("_", 1)[-1]
        try:
            ordinal = int(tail)
        except ValueError:
            ordinal = 0
        out.append((ordinal, value))
    out.sort(key=lambda kv: kv[0])
    return out


def build_segment(prompt, seconds, handoff_seconds, seed_override,
                  images=None, videos=None, video_audios=None, audios=None):
    """The shot description the engine renders from. Raises ValueError for a handoff that is not shorter than the shot."""
    if float(seconds) <= 0:
        raise ValueError("seconds must be more than 0, got %s" % (seconds,))
    if float(handoff_seconds) < 0:
        raise ValueError("handoff_seconds cannot be negative, got %s" % (handoff_seconds,))
    length = generation_length(seconds_to_frames(seconds))
    handoff = guide_length(seconds_to_frames(handoff_seconds))
    if handoff >= length:
        raise ValueError(
            "handoff_seconds (%.2fs -> %d frames) must be shorter than the segment "
            "itself (%.2fs -> %d frames), or the next segment would be nothing but "
            "replay." % (handoff_seconds, handoff, seconds, length))
    return {
        "prompt": prompt, "seconds": seconds, "length": length, "handoff": handoff,
        "seed": int(seed_override),
        "images": [t for _, t in ordered_autogrow(images)],
        "videos": ordered_autogrow(videos),
        "video_audios": ordered_autogrow(video_audios),
        "audios": [a for _, a in ordered_autogrow(audios)],
    }


def resolve_seed(settings, segment, index):
    """The seed one segment renders with: its own override, else the chain seed spread by segment number."""
    if segment["seed"]:
        return int(segment["seed"])
    return (int(settings["seed"]) + (index + 1) * SEED_PRIME) % SEED_MOD


def describe(segment, index, anchored):
    """One log line for a segment about to render or be reused."""
    seconds = segment["length"] / float(FPS)
    return "segment %d: %d frames (%.2fs)%s" % (
        index + 1, segment["length"], seconds,
        ", opening on the previous segment's tail" if anchored else "")


def summarize_chain(chain):
    """Plain text summary of a chain: segment count, final length, one line per segment."""
    records = chain["segments"]
    total = sum(r["length"] for r in records) - sum(r["handoff"] for r in records[:-1])
    lines = ["%d segments -> %.2fs (%d frames) once the replayed handoffs come off"
             % (len(records), total / float(FPS), total)]
    for r in records:
        notes = "  (repaired)" if r.get("repaired") else ""
        if r.get("drift_correction"):
            notes += "  drift -%.3f" % r["drift_correction"]
        lines.append("  %2d  %5.2fs  handoff %4.2fs  seed %d%s"
                     % (r["index"] + 1, r["seconds"], r["handoff"] / float(FPS), r["seed"],
                        notes))
    lines.append("  in %s" % chain["dir"])
    return "\n".join(lines)
