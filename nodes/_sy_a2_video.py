"""Pure helpers for the batch A2 video nodes: frame counts of the form k*n+1 (4n+1 for Wan, 8n+1 for LTX). No node inside."""

ROUNDINGS = ["nearest", "up", "down"]


def snap_frames(frames, step=4, rounding="nearest"):
    """Pure function. Moves a frame count to a value of the form step*n+1 (1, 5, 9, 13 ... for step 4).

    nearest: the closest one (a tie goes up). up: never fewer frames than asked. down: never more.
    """
    frames, step = int(frames), int(step)
    if step < 1:
        raise ValueError("the frame step must be at least 1, got %d" % step)
    if rounding not in ROUNDINGS:
        raise ValueError("rounding must be one of: %s" % ", ".join(ROUNDINGS))
    frames = max(1, frames)
    q, r = divmod(frames - 1, step)
    if r == 0:
        return frames
    if rounding == "up":
        n = q + 1
    elif rounding == "down":
        n = q
    else:
        n = q + (1 if 2 * r >= step else 0)
    return step * n + 1


def is_valid_count(frames, step=4):
    return int(frames) >= 1 and (int(frames) - 1) % int(step) == 0


def rule_note(frames, step=4):
    """Pure function. A plain sentence telling if the frame count fits the step*n+1 rule and what to use if it does not."""
    frames, step = int(frames), int(step)
    if step < 1:
        raise ValueError("the frame step must be at least 1, got %d" % step)
    rule = "%dn+1" % step
    if is_valid_count(frames, step):
        return "%d frames fits the %s rule." % (frames, rule)
    lo, hi = snap_frames(frames, step, "down"), snap_frames(frames, step, "up")
    return "%d frames does not fit the %s rule. Use %d (shorter) or %d (longer)." % (frames, rule, lo, hi)
