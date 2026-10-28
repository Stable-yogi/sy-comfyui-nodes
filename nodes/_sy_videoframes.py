"""Pure helpers for the SY video frame nodes. Work on counts and index lists, no torch."""

MAX_FRAMES = 1_000_000
COUNT_MODES = ["frames_to_seconds", "seconds_to_frames", "fps_from_frames_and_seconds"]
LOOP_MODES = ["repeat", "ping_pong"]


def _pos(value, what, upper):
    v = float(value)
    if not (0 < v <= upper):  # also rejects nan
        raise ValueError("%s must be above 0 and at most %s, got %s" % (what, upper, value))
    return v


def count_video(mode, frames, seconds, fps):
    """Returns (frames, seconds, fps, info). The mode says which two values are used to work out the third."""
    if mode not in COUNT_MODES:
        raise ValueError("mode must be one of: %s" % ", ".join(COUNT_MODES))
    if mode == "frames_to_seconds":
        f = int(_pos(frames, "frames", MAX_FRAMES))
        r = _pos(fps, "fps", 1000)
        s = f / r
    elif mode == "seconds_to_frames":
        s = _pos(seconds, "seconds", 100000)
        r = _pos(fps, "fps", 1000)
        f = max(1, int(s * r + 0.5))
    else:
        f = int(_pos(frames, "frames", MAX_FRAMES))
        s = _pos(seconds, "seconds", 100000)
        r = f / s
    if f > MAX_FRAMES:
        raise ValueError("that is %d frames, more than the limit of %d" % (f, MAX_FRAMES))
    info = "%d frames, %.3f seconds, %.3f fps" % (f, s, r)
    return (f, s, r, info)


def loop_indices(total, target, mode):
    """Index list of length `target` that fills the target by repeating the batch or by bouncing back and forth."""
    total, target = int(total), int(target)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 frame, got %d" % total)
    if not (1 <= target <= MAX_FRAMES):
        raise ValueError("target_frames must be between 1 and %d, got %d" % (MAX_FRAMES, target))
    if mode not in LOOP_MODES:
        raise ValueError("mode must be one of: %s" % ", ".join(LOOP_MODES))
    if mode == "repeat" or total == 1:
        return [i % total for i in range(target)]
    period = 2 * (total - 1)
    out = []
    for i in range(target):
        p = i % period
        out.append(p if p < total else period - p)
    return out


def rate_convert_indices(total, source_fps, target_fps):
    """Index list that turns `total` frames at source_fps into the same length of time at target_fps (nearest frame)."""
    total = int(total)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 frame, got %d" % total)
    src = _pos(source_fps, "source_fps", 1000)
    tgt = _pos(target_fps, "target_fps", 1000)
    new_count = max(1, int(total * tgt / src + 0.5))
    if new_count > MAX_FRAMES:
        raise ValueError("that makes %d frames, more than the limit of %d" % (new_count, MAX_FRAMES))
    return [min(total - 1, int(i * src / tgt + 0.5)) for i in range(new_count)]


def split_range(total, part_size, part):
    """Returns (start, end, parts_total) for slice number `part` (from 0) of size `part_size`. Last slice may be shorter."""
    total, part_size, part = int(total), int(part_size), int(part)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 frame, got %d" % total)
    if part_size < 1:
        raise ValueError("part_size must be at least 1, got %d" % part_size)
    parts_total = (total + part_size - 1) // part_size
    if not (0 <= part < parts_total):
        raise ValueError("part %d does not exist: %d frames in slices of %d make %d parts (0 to %d)"
                         % (part, total, part_size, parts_total, parts_total - 1))
    start = part * part_size
    return (start, min(total, start + part_size), parts_total)


def frame_range(start, end, step):
    """List of frame numbers from start toward end (end included when a step lands on it). Counts down if end < start."""
    start, end, step = int(start), int(end), int(step)
    if step < 1:
        raise ValueError("step must be at least 1, got %d" % step)
    count = abs(end - start) // step + 1
    if count > 100000:
        raise ValueError("that range has %d frames, more than the limit of 100000. Raise step" % count)
    sign = 1 if end >= start else -1
    return [start + sign * step * i for i in range(count)]
