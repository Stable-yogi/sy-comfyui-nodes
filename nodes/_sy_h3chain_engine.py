"""Rendering one segment: the seamless-join trick, the latent handoff and drift arrest.

Ported from: ComfyUI-H3-Continuous (https://github.com/loopforge0/ComfyUI-H3-Continuous)
Original author: Loop Forge. Licence: MIT (copy in third_party/ComfyUI-H3-Continuous/LICENSE).
Copyright (c) 2026 Loop Forge.
Changed by Stable Yogi (renamed, SY standard; every torch, comfy and comfy_extras import moved inside the
functions so this file loads without ComfyUI; frame maths moved to _sy_h3chain_common.py; slice_audio moved
here from common.py; the maths is unchanged).

Nothing here reimplements H3 conditioning. The chain calls the core nodes (the reference-to-video node and
MiniMaxH3AddGuide) and the core sampler, so a ComfyUI update carries straight through.

The whole seamless-join trick lives in ``render_segment``: the previous segment's tail is anchored at frame 0
as a ``minimax_keyframes`` entry, so the new video *opens on those exact frames* rather than being asked to
imagine a plausible continuation. A keyframe pins the clip (about 30 dB against the source); ``ref_videos``
only conditions on it (about 17 dB).

Two ways to build that keyframe (``handoff_mode``):
``latent``  slice the tail straight out of the previous segment's *sampled* latent and pin it. No VAE anywhere.
``pixel``   decode, write an mp4, read it back and let ``MiniMaxH3AddGuide`` VAE-encode it again. The only path
            that survives a resolution change mid-session, and the only one a session from before latent
            tails existed can resume from.
"""
import math
import types

try:
    from ._sy_h3chain_common import (
        FPS,
        audio_latent_frames,
        latent_cover_frames,
    )
except ImportError:  # run as a plain file by the selftest
    from _sy_h3chain_common import (
        FPS,
        audio_latent_frames,
        latent_cover_frames,
    )

_CORE = None
_CLIP_GUIDES = None


def core():
    """The H3 pieces of the ComfyUI core, imported on first use.

    Needs ComfyUI 0.34.0 or newer (comfy_extras/nodes_minimax_h3.py). Raises ValueError with plain words if
    this install is older, so the other SY nodes are not affected.
    """
    global _CORE
    if _CORE is None:
        try:
            from comfy_extras import nodes_minimax_h3 as h3
            from comfy.ldm.minimax.model import FRAME_RESCALE
        except ImportError as exc:
            raise ValueError(
                "The H3 chain nodes need a ComfyUI with MiniMax H3 support (comfy_extras/nodes_minimax_h3.py, "
                "ComfyUI 0.34.0 or newer). Update ComfyUI and restart it.") from exc
        _CORE = types.SimpleNamespace(
            AddGuide=h3.MiniMaxH3AddGuide,
            RefToVideo=h3.MiniMaxH3ReferenceToVideo,
            video_latent_t=h3.video_latent_t,
            FRAME_RESCALE=FRAME_RESCALE,
        )
    return _CORE


def _probe_clip_guides():
    """Does this core reserve a guide latent's real length in the packed sequence?

    ``PackedLayout`` is asked for a two-frame guide and its answer is counted. A core with multi-frame guide
    support reserves ``vt * frame_rows`` condition rows; the one that shipped before ``MiniMaxH3AddGuide``
    reserves ``frame_rows`` -- one frame -- whatever length of guide it is handed.

    A probe rather than a version string because that is the thing that actually has to be true, and because
    the failure this catches is a *partially* updated install, where the version number is already the new one.
    """
    import torch
    from comfy.ldm.minimax.model import PackedLayout

    latent_h = latent_w = 4
    frame_rows = (latent_h // 2) * (latent_w // 2)
    guide = {"resolved_frame_index": 0, "latent": torch.zeros(1, 24, 2, latent_h, latent_w)}
    layout = PackedLayout(1, 2, latent_h, latent_w, 1, keyframes=[guide])
    return int((~layout.img_update).sum()) == 2 * frame_rows


def assert_clip_guides_supported():
    """Refuse to pin a clip a core of this vintage will mis-size.

    Without this the render gets several minutes into the segment and then dies inside the DiT on a bare
    tensor shape, naming neither the guide nor ComfyUI.
    """
    global _CLIP_GUIDES
    if _CLIP_GUIDES is None:
        try:
            _CLIP_GUIDES = _probe_clip_guides()
        except Exception:
            _CLIP_GUIDES = True  # an unreadable core is not grounds for refusing to render
    if _CLIP_GUIDES:
        return
    raise RuntimeError(
        "This ComfyUI reserves one latent frame for a guide clip however long the "
        "clip is, so the handoff this segment opens on would write about twelve "
        "times the rows the sequence has room for -- the 'shape mismatch: value "
        "tensor of shape [A, 96] cannot be broadcast to indexing result of shape "
        "[B, 96]' that would come out of the sampler in a minute or two.\n\n"
        "Multi-frame guides arrived in ComfyUI together with MiniMaxH3AddGuide, in "
        "0.34.0. This install has that node, but comfy/ldm/minimax/model.py is from "
        "before it, which is a half-applied update rather than an old one. Update "
        "ComfyUI, restart it fully, and check that comfy/ldm/minimax/model.py "
        "contains 'vt = video_latent.shape[2]'. If it does and this still fires, "
        "delete comfy/ldm/minimax/__pycache__.")


def slice_audio(audio, start_seconds, duration_seconds):
    """Cut an AUDIO dict to a window, padding with silence if it falls short.

    An anchor clip whose audio outran its video by six seconds is the bug this function exists to make
    impossible: the guide crops audio against the *target's* remaining duration, never against the image
    clip beside it, so an over-long soundtrack is anchored in full and a segment with no dialogue of its own
    replays the previous segment's lines.
    """
    if audio is None:
        return None
    import torch
    waveform = audio["waveform"]
    rate = int(audio["sample_rate"])
    start = max(0, int(round(start_seconds * rate)))
    want = max(1, int(round(duration_seconds * rate)))
    cut = waveform[..., start:start + want].clone()
    if cut.shape[-1] < want:
        pad = torch.zeros(cut.shape[:-1] + (want - cut.shape[-1],), dtype=cut.dtype)
        cut = torch.cat([cut, pad], dim=-1)
    return {"waveform": cut, "sample_rate": rate}


def _reference_conditioning(settings, segment):
    """Hand the segment's references to the core ref2va node in tag order.

    Only ``ref_images`` / ``ref_videos`` / ``ref_audios`` reach the tokenizer, and
    the tags are numbered 1-based per type in wiring order: the first image is
    ``<Picture 1>``, the second ``<Picture 2>``, and so on. That is why the segment
    node keeps its inputs in ordinal order -- the prompt's tag numbers are the
    socket numbers.
    """
    ref_images = {"ref_image_%d" % i: t for i, t in enumerate(segment["images"])}
    ref_videos = {"ref_video_%d" % i: t for i, (_, t) in enumerate(segment["videos"])}
    ref_video_audios = {"ref_video_audio_%d" % i: a
                        for i, (_, a) in enumerate(segment["video_audios"])}
    ref_audios = {"ref_audio_%d" % i: a for i, a in enumerate(segment["audios"])}

    return core().RefToVideo.execute(
        clip=settings["clip"],
        vae=settings["vae"],
        audio_vae=settings["audio_vae"],
        prompt=segment["prompt"],
        width=settings["width"],
        height=settings["height"],
        length=segment["length"],
        ref_image_size=settings["ref_image_size"],
        ref_images=ref_images or None,
        ref_videos=ref_videos or None,
        ref_video_audios=ref_video_audios or None,
        ref_audios=ref_audios or None,
    )


def _av_streams(samples):
    """The (video, audio) pair inside an H3 AV latent, each with a batch axis."""
    parts = samples.unbind() if samples.is_nested else (samples,)
    if len(parts) < 2:
        raise ValueError("not a MiniMax H3 joint AV latent: no audio stream")
    video, audio = parts[0], parts[1]
    if video.ndim == 4:
        video = video.unsqueeze(0)
    if audio.ndim == 3:
        audio = audio.unsqueeze(0)
    return video, audio


def latent_tail(samples, handoff):
    """The last ``handoff`` frames of a sampled AV latent, as an anchor.

    The slice is always token-aligned. H3's frame grid is 17k+5 frames -> 5k+2
    latent steps, and a valid handoff is 17m+5 -> 5m+2, so the tail starts at
    5(k-m): a multiple of 5, which is cycle position 0 of the 1/4/4/4/4
    frames-per-token pattern. That matters -- start anywhere else and the tail's
    first token claims to cover 4 frames where a fresh encode would cover 1, and
    the anchor lands 3 frames out.
    """
    if handoff <= 0:
        return None
    video, audio = _av_streams(samples)
    tokens = core().video_latent_t(handoff)
    total = int(video.shape[2])
    if tokens > total:
        raise ValueError("handoff of %d frames needs %d latent steps, segment has %d"
                         % (handoff, tokens, total))
    start = total - tokens
    if start % 5 != 0:
        raise RuntimeError("tail starts at cycle position %d, not 0 -- the frame grid "
                           "and the handoff have gone out of phase" % (start % 5))
    rt = audio_latent_frames(handoff)
    return {
        "video_latent": video[:1, :, start:].clone(),
        "audio_latent": audio[:1, ..., max(0, int(audio.shape[-1]) - rt):].clone(),
    }


def latent_signature(samples):
    """Per-channel mean and std of a segment's whole video latent.

    24 numbers each. This is what "the look of this shot" reduces to: exposure and
    colour balance live in the channel means, contrast in the spreads. Taken over
    the *whole* segment rather than its tail, so that a specific pose, gesture or
    expression at the moment of the handoff averages out and only the shot's
    standing appearance is left.
    """
    video, _ = _av_streams(samples)
    video = video.detach().float()
    return {"mean": video.mean(dim=(0, 2, 3, 4)).cpu(),
            "std": video.std(dim=(0, 2, 3, 4)).cpu()}


def arrest_drift(anchor, reference, current, strength, clamp_sigma=0.35):
    """Pull a handoff's channel means back toward the opening shot's.

    Chained generation drifts because nothing in it is absolute. Each segment is
    told only "continue from this", so wherever segment N ended up *is* the truth
    for segment N+1, and a small bias repeats until the take has walked somewhere
    else entirely -- measurably, on a six-shot chain, about 8 L* of face brightness
    and 0.24 of ArcFace cosine.

    Closing that loop needs an absolute reference, and segment 1 is the only one
    available: it is the shot that was rendered from the prompt and the reference
    image alone, with no inherited anchor to be wrong about. So each handoff is
    shifted back toward segment 1's channel means before it is pinned.

    Two deliberate limits:

    ``strength`` is a fraction, not a reset. Correcting the whole error would put a
    step at every join -- the previous segment really did end where it ended, and
    the cut keeps those frames. A fraction leaves a residual small enough to hide
    under the join while still bounding the walk, which is the difference between
    drift that accumulates and drift that settles.

    ``clamp_sigma`` caps any single channel's correction at a fraction of that
    channel's own spread. It is there for the case this function cannot tell apart
    from drift: a shot that is *legitimately* darker because she walked away from
    the window. A real lighting change is large, and the clamp stops it being
    fought; accumulated drift is small, and passes through untouched.

    Only the video stream is touched. Audio does not drift this way, and shifting
    its latent would detune the voice.
    """
    if anchor is None or reference is None or current is None or strength <= 0:
        return anchor
    video_latent = anchor.get("video_latent")
    if video_latent is None:
        return anchor

    error = (reference["mean"] - current["mean"]) * float(strength)
    limit = reference["std"] * float(clamp_sigma)
    import torch

    error = torch.clamp(error, -limit, limit)

    shift = error.to(device=video_latent.device, dtype=video_latent.dtype)
    corrected = dict(anchor)
    corrected["video_latent"] = video_latent + shift.view(1, -1, 1, 1, 1)
    corrected["drift_correction"] = float(error.abs().mean())
    return corrected


def anchor_frames(anchor):
    """How many pixel frames an anchor covers, whichever form it is in."""
    if anchor is None:
        return 0
    video_latent = anchor.get("video_latent")
    if video_latent is not None:
        return latent_cover_frames(video_latent.shape[2])
    return int(anchor["images"].shape[0])


def picture_only(anchor):
    """The same anchor with its soundtrack dropped.

    The repair node pins a segment's ending to the clip the *next* segment already
    opens on. That clip's audio belongs to the render being thrown away, so
    re-anchoring it would drag back the very take the repair exists to replace --
    which is how a shot with no dialogue of its own ends up speaking the previous
    shot's lines.
    """
    if anchor is None:
        return None
    if anchor.get("video_latent") is not None:
        return {"video_latent": anchor["video_latent"], "audio_latent": None}
    return {"images": anchor["images"], "audio": None}


def _pin_latent(positive, latent, anchor, frame_idx=0):
    """Pin a pre-encoded tail as a keyframe, the way AddGuide would if it took one.

    This is the one place the pack builds an H3 conditioning entry itself instead
    of calling the core node, because ``MiniMaxH3AddGuide`` only accepts pixels and
    always VAE-encodes them. The dict is exactly the shape ``PackedLayout`` reads:
    a resolved frame index, a video latent, and an audio latent placed on the same
    t-axis.
    """
    target_video, target_audio = _av_streams(latent["samples"])
    frame_count = latent_cover_frames(target_video.shape[2])

    video_latent = anchor["video_latent"]
    if tuple(video_latent.shape[3:]) != tuple(target_video.shape[3:]):
        raise ValueError(
            "latent handoff cannot resize: the anchor is %dx%d but this segment is "
            "%dx%d. Re-render the session at one resolution, or set handoff_mode to "
            "'pixel', which re-encodes through the VAE and can rescale."
            % (int(video_latent.shape[4]) * 16, int(video_latent.shape[3]) * 16,
               int(target_video.shape[4]) * 16, int(target_video.shape[3]) * 16))

    guide_frames = latent_cover_frames(video_latent.shape[2])
    resolved = frame_idx if frame_idx >= 0 else frame_count + frame_idx
    if resolved < 0 or resolved + guide_frames > frame_count:
        raise ValueError("a %d frame anchor at frame_idx %d does not fit in %d frames"
                         % (guide_frames, frame_idx, frame_count))

    keyframe = {
        "resolved_frame_index": resolved,
        "latent": video_latent.to(device=target_video.device, dtype=target_video.dtype),
    }
    audio_latent = anchor.get("audio_latent")
    if audio_latent is not None and audio_latent.shape[-1] > 0:
        # Same clamp AddGuide applies: the guide's audio cannot outrun the target's
        # own remaining track. Letting it would anchor a whole soundtrack into a
        # segment that has room for part of one, which is how a segment ends up
        # replaying the previous segment's dialogue.
        max_rt = math.floor(int(target_audio.shape[-1]) - core().FRAME_RESCALE * resolved)
        if max_rt >= 1:
            if audio_latent.shape[-1] > max_rt:
                audio_latent = audio_latent[..., :max_rt]
            keyframe["audio_latent"] = audio_latent.to(
                device=target_audio.device, dtype=target_audio.dtype)

    import node_helpers

    keyframes = list(positive[0][1].get("minimax_keyframes", []))
    keyframes.append(keyframe)
    return node_helpers.conditioning_set_values(positive, {"minimax_keyframes": keyframes})


def _pin_pixels(settings, positive, latent, images, audio, frame_idx):
    return core().AddGuide.execute(
        positive=positive,
        latent=latent,
        frame_idx=frame_idx,
        vae=settings["vae"],
        audio_vae=settings["audio_vae"] if audio is not None else None,
        image=images,
        audio=audio,
    )[0]


def _pin(settings, positive, latent, anchor, frame_idx):
    """Anchor whichever form this anchor arrived in."""
    # Both forms pin a clip, and a clip is what a pre-0.34.0 core mis-sizes; the
    # check is here rather than in either branch so neither path can skip it.
    if anchor_frames(anchor) > 1:
        assert_clip_guides_supported()
    if anchor.get("video_latent") is not None:
        return _pin_latent(positive, latent, anchor, frame_idx)
    return _pin_pixels(settings, positive, latent, anchor["images"],
                       anchor.get("audio"), frame_idx)


def render_segment(settings, segment, start_anchor=None, end_anchor=None):
    """Render one segment. Returns ``(images, audio, samples)``.

    ``start_anchor`` is the previous segment's tail, pinned at frame 0, in either
    anchor form. ``end_anchor`` is picture only, pinned at the end -- see the repair
    node for why its audio is deliberately dropped.

    ``samples`` is the sampled AV latent, handed back so the caller can cut the next
    handoff out of it without a VAE round trip.
    """
    from comfy_extras.nodes_audio import vae_decode_audio
    from comfy_extras.nodes_custom_sampler import (
        Guider_Basic,
        Noise_RandomNoise,
        SamplerCustomAdvanced,
    )

    positive, latent = _reference_conditioning(settings, segment)

    if start_anchor is not None:
        positive = _pin(settings, positive, latent, start_anchor, 0)

    if end_anchor is not None:
        positive = _pin(settings, positive, latent, end_anchor,
                        -anchor_frames(end_anchor))

    guider = Guider_Basic(settings["model"])
    guider.set_conds(positive)

    sampled = SamplerCustomAdvanced.execute(
        noise=Noise_RandomNoise(segment["resolved_seed"]),
        guider=guider,
        sampler=settings["sampler"],
        sigmas=settings["sigmas"],
        latent_image=latent,
    )[0]

    samples = sampled["samples"]
    video_latent = samples.unbind()[0] if samples.is_nested else samples
    images = settings["vae"].decode(video_latent)
    if images.ndim == 5:
        images = images.reshape(-1, *images.shape[-3:])
    audio = vae_decode_audio(settings["audio_vae"], sampled)

    del sampled, video_latent, positive, latent, guider
    return images, audio, samples


def take_tail(images, audio, handoff, fps=FPS):
    """The last ``handoff`` frames and exactly their own audio.

    ``.clone()`` is not optional: a view keeps the whole decoded segment alive, and
    the point of writing each segment to disk is to stop holding it in memory.
    """
    if handoff <= 0:
        return None
    total = int(images.shape[0])
    start = max(0, total - handoff)
    tail_images = images[start:].clone()
    tail_audio = slice_audio(audio, start / float(fps), (total - start) / float(fps))
    return tail_images, tail_audio


def free_between_segments(unload_models=False):
    import comfy.model_management

    if unload_models:
        comfy.model_management.unload_all_models()
    comfy.model_management.soft_empty_cache()


def push_preview(pbar, frame, done, total):
    """Show a finished segment on the node while the chain is still running.

    A chain is one node execution that can run for hours, so without this the canvas
    sits apparently idle from the first segment to the last. ProgressBar's preview
    channel is the same one latent previews use, and the executor resolves the node
    id from the running context, so the image lands on the chain node itself.

    The frame shown is the segment's LAST one, deliberately: that is the frame the
    next segment opens on, so what you are watching is the state being handed
    forward.
    """
    if pbar is None:
        return
    preview = None
    if frame is not None:
        try:
            from PIL import Image
            import latent_preview
            array = (frame.clamp(0, 1) * 255).byte().cpu().numpy()
            preview = ("JPEG", Image.fromarray(array), latent_preview.MAX_PREVIEW_RESOLUTION)
        except Exception:
            preview = None  # a preview is never worth failing a render over
    pbar.update_absolute(done, total, preview)
