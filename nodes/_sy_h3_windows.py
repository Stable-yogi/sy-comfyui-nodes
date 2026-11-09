"""Time windows for MiniMax H3 sampling: which stretch of the video each piece covers, and how guides move to that stretch.
plan_windows, window_keyframes and window_refs are ported from ComfyUI-MiniMaxH3-TemporalWindow-SpatialTiles by mo-akkakk
(MIT, commit 6be3267d6fe52ce8b8121a74d425cd6f389b6ef9). Licence text: third_party/ComfyUI-MiniMaxH3-TemporalWindow-SpatialTiles/LICENSE."""
import math

FRAME_PER_TOKEN = (1, 4, 4, 4, 4)  # video frames behind each latent frame, repeating
FRAME_RESCALE = 5.0 / 3.0  # sound latent ticks per video frame
CLIP_TOKENS = 5  # 5 latent frames = one 17 frame block


def frames_for_tokens(t):
    """Pure function. Video frames covered by the first t latent frames."""
    return sum(FRAME_PER_TOKEN[k % 5] for k in range(t))


def tokens_for_frames(frames):
    """Pure function. Latent length of the longest valid H3 clip (17k + 5 frames) that fits in frames."""
    return 2 + 5 * max(0, (frames - 5) // 17)


def audio_ticks(frames):
    """Pure function. Sound latent ticks that match this many video frames."""
    return round(frames * FRAME_RESCALE)


def plan_windows(latent_t, window_frames, overlap_frames):
    """Pure function. [(start, length)] in latent frames. Starts sit on block edges, the last window ends on the last frame. 0 = one window."""
    win = tokens_for_frames(window_frames)
    if window_frames <= 0 or win >= latent_t:
        return [(0, latent_t)]
    ov = min(tokens_for_frames(overlap_frames), win - CLIP_TOKENS)
    windows = [(0, win)]
    while windows[-1][0] + win < latent_t:
        start = windows[-1][0] + win - ov
        if start + win > latent_t:
            start = latent_t - win
        windows.append((start, latent_t - start if start + win >= latent_t else win))
    return windows


def audio_span(windows, index, audio_t):
    """Pure function. The (first, last) sound latent ticks that belong to one window."""
    t0, tn = windows[index]
    a0 = 0 if t0 == 0 else min(audio_ticks(frames_for_tokens(t0)), audio_t)
    return a0, audio_t if index == len(windows) - 1 else min(audio_t, a0 + audio_ticks(frames_for_tokens(tn)))


def ease_in_out(n):
    """Pure function. n soft steps from near 0 to near 1, for crossfading two windows."""
    steps = [(i + 1.0) / (n + 1.0) for i in range(n)]
    return [t * t * (3.0 - 2.0 * t) for t in steps]


def ref_window_span(ref_t, k0, k1):
    """Latent range of a reference video that covers window [k0, k1). A shorter reference gives its tail."""
    if k1 <= ref_t:
        return k0, k1
    return min(k0, (ref_t - 2) // CLIP_TOKENS * CLIP_TOKENS), ref_t


def window_refs(refs, k0, k1):
    """Reference videos cut to the window. Pictures stay whole."""
    out = []
    for blk in refs:
        if blk["kind"] not in ("video", "video_audio"):
            out.append(blk)
            continue
        s, e = ref_window_span(blk["latent_t"], k0, k1)
        new = dict(blk)
        new["latent"] = blk["latent"][:, :, s:e]
        new["latent_t"] = e - s
        audio = blk.get("audio_latent")
        if audio is not None and blk["ref_audio_t"] > 0:
            a0 = min(audio_ticks(frames_for_tokens(s)), audio.shape[-1])
            a1 = min(a0 + audio_ticks(frames_for_tokens(e) - frames_for_tokens(s)), audio.shape[-1])
            if a1 > a0:
                new["audio_latent"] = audio[..., a0:a1]
                new["ref_audio_t"] = a1 - a0
            else:
                new.update({"audio_latent": None, "ref_audio_t": 0, "kind": "video"})
        out.append(new)
    return out


def window_keyframes(keyframes, k0, k1):
    """Frame guides moved to window time. A guide clip that crosses the window edge keeps its 5 latent blocks inside the window, its sound stays as a separate guide."""
    f0, frames = frames_for_tokens(k0), frames_for_tokens(k1) - frames_for_tokens(k0)
    a0 = audio_ticks(f0) if k0 > 0 else 0
    a1 = audio_ticks(f0 + frames)
    out = []
    for kf in keyframes:
        idx = kf["resolved_frame_index"] - f0
        latent = kf.get("latent")
        span = 1 if latent is None or latent.shape[2] <= 1 else frames_for_tokens(latent.shape[2])
        if 0 <= idx and idx + span <= frames:
            new = dict(kf)
            new["resolved_frame_index"] = idx
            audio = kf.get("audio_latent")
            if audio is not None:
                max_rt = math.floor(audio_ticks(frames) - FRAME_RESCALE * idx)
                new["audio_latent"] = audio[..., :max_rt] if max_rt >= 1 else None
            out.append(new)
            continue
        if idx >= frames or idx + span <= 0:
            continue
        if latent is not None and latent.shape[2] > 1:
            vt = latent.shape[2]
            gs = [frames_for_tokens(g) for g in range(vt + 1)]
            chunks = [g for g in range(0, vt, CLIP_TOKENS) if idx + gs[g] >= 0 and idx + gs[min(g + CLIP_TOKENS, vt)] <= frames]
            if chunks:
                new = {k: v for k, v in kf.items() if k != "audio_latent"}
                new["resolved_frame_index"] = idx + gs[chunks[0]]
                new["latent"] = latent[:, :, chunks[0]:chunks[-1] + CLIP_TOKENS]
                out.append(new)
        audio = kf.get("audio_latent")
        if audio is not None:
            t = FRAME_RESCALE * kf["resolved_frame_index"]
            j0, j1 = max(0, math.ceil(a0 - t)), min(audio.shape[-1], math.ceil(a1 - t))
            if j1 > j0:
                new = {k: v for k, v in kf.items() if k != "latent"}
                new["resolved_frame_index"] = (t + j0 - a0) / FRAME_RESCALE
                new["audio_latent"] = audio[..., j0:j1]
                out.append(new)
    return out


def window_conditioning(positive, k0, k1):
    """Conditioning moved to the window [k0, k1). The words stay whole."""
    out = []
    for emb, extra in positive:
        extra = extra.copy()
        if extra.get("minimax_refs"):
            extra["minimax_refs"] = window_refs(extra["minimax_refs"], k0, k1)
        if "minimax_keyframes" in extra:
            extra["minimax_keyframes"] = window_keyframes(extra["minimax_keyframes"] or [], k0, k1)
        out.append([emb, extra])
    return out


def add_carry(positive, latent):
    """The finished frames of the window before, as a guide at the start of this one."""
    out = []
    for emb, extra in positive:
        extra = extra.copy()
        extra["minimax_keyframes"] = list(extra.get("minimax_keyframes") or []) + [{"resolved_frame_index": 0, "latent": latent}]
        out.append([emb, extra])
    return out
