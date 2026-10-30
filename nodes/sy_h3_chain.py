"""H3 Chain SY: five nodes that chain MiniMax H3 renders into one unbroken take.

Ported from: ComfyUI-H3-Continuous (https://github.com/loopforge0/ComfyUI-H3-Continuous)
Original author: Loop Forge. Licence: MIT (copy in third_party/ComfyUI-H3-Continuous/LICENSE).
Copyright (c) 2026 Loop Forge.
Changed by Stable Yogi (renamed to SY ids and display names, sockets renamed SY_H3_SETTINGS and SY_H3_CHAIN,
SY category and tooltips of at most 120 characters with the long text moved into the descriptions and
docs/h3-chain.md, all logic moved into the helper files _sy_h3chain_*.py, bad input raises ValueError with plain
words, session paths go through safe_join). The maths and the on-disk session format are unchanged, so a session
started with the original pack can be resumed.

The five nodes use ComfyUI's V3 schema (the sockets image_0, image_1 ... grow as you connect them). Their classes
are built from the plain data table SPECS below. If this ComfyUI has no V3 Autogrow or no MiniMax H3 core nodes,
the five nodes are simply not registered (SY_REGISTER is False, the reason is in SY_NOT_LOADED_REASON) and the
rest of the SY pack loads as usual. The classes in NODE_CLASS_MAPPINGS are then stand-ins that only describe
the inputs, so the selftest can check names, tooltips and descriptions without ComfyUI.
"""
import os
import shutil

try:
    from ._sy_common import category, safe_join
    from . import _sy_h3chain_common as common
    from . import _sy_h3chain_engine as engine
    from . import _sy_h3chain_session as session_mod
    from . import _sy_h3chain_video as video_io
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, safe_join
    import _sy_h3chain_common as common
    import _sy_h3chain_engine as engine
    import _sy_h3chain_session as session_mod
    import _sy_h3chain_video as video_io

CATEGORY = category("Utility")
SETTINGS_TYPE = "SY_H3_SETTINGS"
CHAIN_TYPE = "SY_H3_CHAIN"
MAX_TOOLTIP = 120

# ---------------------------------------------------------------------------
# the data table: one entry per node, one dict per input
# kinds: model clip vae sampler sigmas int float string combo bool image audio video custom autogrow
# ---------------------------------------------------------------------------


def _inp(kind, id, tooltip, **kw):
    d = {"kind": kind, "id": id, "tooltip": tooltip}
    d.update(kw)
    return d


def _segment_inputs():
    """The shot fields shared by H3 Render Segment and H3 Repair Segment."""
    return [
        _inp("string", "prompt",
             "The H3 prompt. Tags count per type: image_0 is <Picture 1>, video_0 is <Video 1>, audio_0 is <Audio 1>.",
             multiline=True, dynamic_prompts=False),
        _inp("float", "seconds",
             "Length of this segment in seconds. It snaps up to H3's frame grid (24 fps). About 5 to 15 s works best.",
             default=8.0, min=0.25, max=15.0, step=0.25, round=False),
        _inp("float", "handoff_seconds",
             "Seconds of this ending replayed at the start of the next segment. Use 0 on the last segment.",
             default=1.625, min=0.0, max=4.0, step=0.125, round=False, advanced=True),
        _inp("int", "seed_override",
             "0 uses the chain seed. Any other number re-rolls just this segment.",
             default=0, min=0, max=0xffffffffffffffff, advanced=True),
        _inp("model", "model",
             "Optional model for this shot only (for example with a LoRA). It replaces the model from the settings.",
             optional=True),
        _inp("autogrow", "images", "Reference images. They become <Picture 1> to <Picture 9> in the prompt.",
             optional=True, prefix="image_", min=1, max=9,
             inner=_inp("image", "image", "Reference image for this segment.", optional=True)),
        _inp("autogrow", "videos", "Reference videos (frames at 24 fps, 2 to 15 s). They become <Video 1> to <Video 3>.",
             optional=True, prefix="video_", min=0, max=3,
             inner=_inp("image", "video", "Frames of one reference video.", optional=True)),
        _inp("autogrow", "video_audios", "Soundtrack of the reference video with the same number.",
             optional=True, prefix="video_audio_", min=0, max=3,
             inner=_inp("audio", "video_audio", "Soundtrack of the video with the same number.", optional=True)),
        _inp("autogrow", "audios", "Separate reference audio. It becomes <Audio 1> to <Audio 3>.",
             optional=True, prefix="audio_", min=0, max=3,
             inner=_inp("audio", "audio", "One separate reference audio.", optional=True)),
    ]


DESC_SETTINGS = (
    "Everything the chain and the repair node both need: models, sampler, canvas and seed. Wire one of these into "
    "either.\n\n"
    "session_name is read by H3 Render Segment (the first segment of a chain reads it, later ones inherit it from "
    "chain_state) but NOT by H3 Repair Segment, which has its own session_name.\n\n"
    "chain_seed is deliberately not called 'seed': the ComfyUI page would add a randomise control to it and "
    "re-render the whole chain on every run.\n\n"
    "ref_image_size: 'match' scales reference images to the video size. 'max' uses a 2048 pixel short edge for the "
    "best likeness and is several times slower.\n\n"
    "handoff_mode: 'latent' (default) cuts the previous ending out of the previous segment's own latent and pins it. "
    "No VAE is used, so the anchor is exact and a VAE encode per segment is saved. 'pixel' decodes the ending, "
    "writes it as an mp4, reads it back and re-encodes it. It is slower and lossy, but it is the only way to change "
    "the picture size part way through a session. Both endings are always written to disk, so a session can be "
    "resumed in either mode. A session from before latent endings existed falls back to 'pixel' on its own.\n\n"
    "drift_arrest: a long chain slowly drifts in colour and brightness because each segment only continues the "
    "last one. This pulls each handoff back toward segment 1 by the given fraction of the measured error (0 is "
    "off, 0.4 to 0.6 is the useful range). It is a fraction and not a reset, so no step shows at the joins, and "
    "large corrections are capped so a real lighting change is not fought. It needs handoff_mode 'latent'. "
    "Changing it re-renders the segments after the first. See docs/h3-chain.md.")

DESC_RENDER = (
    "One shot in a continuous take: a prompt, its references and how long it runs. It renders right here. Chain "
    "shots by wiring this node's chain_state output into the next H3 Render Segment's chain_state input. Each shot "
    "after the first opens on an exact replay of the end of the one before it, so the cut is invisible.\n\n"
    "The video output is ready as soon as THIS segment finishes. The segment is also written to "
    "output/h3_continuous/<session>/ and reused on the next run, so a crash, an interrupt or an edited prompt only "
    "costs the segments that changed.\n\n"
    "resume: reuse this segment if it is already in the session with the same settings. Editing an earlier "
    "segment still re-renders this one, because each fingerprint includes the segment before it.\n\n"
    "prompt: the clip carried in from the previous segment gets NO tag (it never reaches the text encoder). "
    "Describe it in plain words, for example 'the shot opens on an exact replay of the preceding shot and carries "
    "straight on'. Nothing new can be scheduled inside the replayed opening.\n\n"
    "handoff_seconds: snapped down to 5, 22, 39 or 56 frames (0.21, 0.92, 1.63 or 2.33 s). 39 frames is the sweet "
    "spot. Keep it near a fifth of the segment: 1.63 s in an 8 s segment joins cleanly, in a 5 s segment the seams "
    "get worse. A longer handoff also costs that much new footage per segment. On the last segment set it to 0.\n\n"
    "model: replaces the settings model for this shot only. Put a per-shot LoRA here, and keep the speed LoRA the "
    "chain relies on in the stack you wire in. Changing the LoRA or its strength re-renders this segment and every "
    "one after it.\n\n"
    "chain_state: leave unconnected on the first segment. It also accepts the chain output of H3 Load Session, to "
    "add new segments onto a finished session. unload_models_after is only for the one segment where you run out "
    "of memory: it forces a full model reload.")

DESC_JOIN = (
    "Joins a session's segments into one cut and drops each segment's replayed opening, so the motion does not "
    "stutter once per join.\n\n"
    "crf is the quality of the joined file (lower is better and bigger, 0 is lossless).\n\n"
    "stabilize flattens the slow drift of the finished cut away from its own opening (0 is off, 0.7 to 1.0 is the "
    "useful range). Each colour channel's per-frame mean is smoothed over two seconds, and a gain aimed at "
    "segment 1's level is applied. Gains keep black black, and the curve is smooth, so no step shows at a join. "
    "Gains are limited to plus or minus 25 percent so a real lighting change survives. It costs one extra decoding "
    "pass and no GPU. It fixes colour only: for likeness drift use drift_arrest on H3 Chain Settings.")

DESC_REPAIR = (
    "Re-render one segment of a finished session, in place.\n\n"
    "Normally re-rendering segment N changes its ending, so every segment after it has to be re-rendered too. This "
    "node pins BOTH ends: the opening to the previous segment's handoff clip, and the ending to the very clip the "
    "next segment already opens on. Nothing downstream moves.\n\n"
    "segment_number is 1-based and matches seg_NN.mp4 in the session folder. The old file is kept as "
    "seg_NN.replaced.mp4. pin_ending: turn it off only for the last segment, or when you mean to re-render "
    "everything after this one.")

DESC_LOAD = (
    "Pick up a session that is already on disk, to re-join it, feed the repair node or extend it, without "
    "re-rendering anything.\n\n"
    "Its chain output wires into H3 Chain To Video and H3 Repair Segment, and also into another H3 Render Segment's "
    "chain_state, to render more shots onto the end of a finished session.\n\n"
    "handoff_mode is which form of the last segment's ending to load. Match the chain that will use it. It falls "
    "back to 'pixel' if the session has no latent ending.")

SPECS = [
    {
        "id": "SYH3ChainSettings", "name": "H3 Chain Settings", "description": DESC_SETTINGS,
        "inputs": [
            _inp("model", "model", "The H3 video model used for every segment."),
            _inp("clip", "clip", "The text encoder that goes with the H3 model."),
            _inp("vae", "vae", "The H3 video VAE."),
            _inp("vae", "audio_vae", "The H3 audio VAE."),
            _inp("sampler", "sampler", "The sampler used for every segment."),
            _inp("sigmas", "sigmas", "The noise steps (sigmas) used for every segment."),
            _inp("int", "width", "Picture width in pixels, in steps of 32.", default=864, min=32, max=16384, step=32),
            _inp("int", "height", "Picture height in pixels, in steps of 32.", default=480, min=32, max=16384, step=32),
            _inp("int", "chain_seed", "Each segment gets its own seed from this one. Changing it re-renders the whole chain.",
                 default=0, min=0, max=0xffffffffffffffff),
            _inp("string", "session_name",
                 "Folder name under output/h3_continuous/. The first segment of a chain reads it from here.",
                 default="my_chain", multiline=False),
            _inp("combo", "ref_image_size",
                 "'match' scales reference images to the video size. 'max' is sharper but several times slower.",
                 options=list(common.REF_IMAGE_SIZES), default="match"),
            _inp("combo", "handoff_mode",
                 "'latent' carries the ending over without a VAE (best). 'pixel' re-encodes it and can change size.",
                 options=list(common.HANDOFF_MODES), default="latent", advanced=True),
            _inp("float", "drift_arrest",
                 "0 is off. 0.4 to 0.6 pulls each handoff's colour back toward segment 1. Needs the latent handoff.",
                 default=0.0, min=0.0, max=1.0, step=0.05, round=False, advanced=True),
        ],
        "outputs": [("custom", SETTINGS_TYPE, "settings")],
    },
    {
        "id": "SYH3RenderSegment", "name": "H3 Render Segment", "description": DESC_RENDER,
        "inputs": (
            [_inp("custom", "settings", "The bundle from H3 Chain Settings.", type=SETTINGS_TYPE),
             _inp("custom", "chain_state",
                  "The previous segment's chain_state. Leave empty on the first segment of a session.",
                  type=CHAIN_TYPE, optional=True),
             _inp("bool", "resume", "Reuse this segment if it is already rendered with the same settings.", default=True)]
            + _segment_inputs()
            + [_inp("bool", "unload_models_after",
                    "Unload the models after this segment. Only for the one segment where you run out of memory.",
                    default=False, advanced=True)]),
        "outputs": [("video", "VIDEO", "video"), ("custom", CHAIN_TYPE, "chain_state"), ("string", "STRING", "summary")],
    },
    {
        "id": "SYH3ChainToVideo", "name": "H3 Chain To Video", "description": DESC_JOIN,
        "inputs": [
            _inp("custom", "chain", "The chain to join: from a Render Segment (chain_state) or from Load Session.",
                 type=CHAIN_TYPE),
            _inp("float", "crf", "Quality of the joined file. Lower is better and bigger. 0 is lossless.",
                 default=14.0, min=0.0, max=51.0, step=1.0, advanced=True),
            _inp("float", "stabilize",
                 "0 is off. 0.7 to 1.0 flattens the slow colour drift of the finished cut. Colour only.",
                 default=0.0, min=0.0, max=1.0, step=0.05, round=False, advanced=True),
        ],
        "outputs": [("video", "VIDEO", "video"), ("string", "STRING", "path")],
    },
    {
        "id": "SYH3RepairSegment", "name": "H3 Repair Segment", "description": DESC_REPAIR,
        "inputs": (
            [_inp("custom", "settings", "The bundle from H3 Chain Settings.", type=SETTINGS_TYPE),
             _inp("string", "session_name", "Folder name of the session to repair, under output/h3_continuous/.",
                  default="my_chain", multiline=False),
             _inp("int", "segment_number", "Which segment to re-render. 1 is the first, matching seg_01.mp4.",
                  default=2, min=1, max=32)]
            + _segment_inputs()
            + [_inp("bool", "pin_ending",
                    "Keep the ending the next segment continues from. Turn off only for the last segment.",
                    default=True)]),
        "outputs": [("video", "VIDEO", "video"), ("custom", CHAIN_TYPE, "chain"), ("string", "STRING", "summary")],
    },
    {
        "id": "SYH3LoadSession", "name": "H3 Load Session", "description": DESC_LOAD,
        "inputs": [
            _inp("string", "session_name", "Folder name of the session to load, under output/h3_continuous/.",
                 default="my_chain", multiline=False),
            _inp("combo", "handoff_mode",
                 "Which form of the last ending to load. 'latent' falls back to 'pixel' if the session has none.",
                 options=list(common.HANDOFF_MODES), default="latent", advanced=True),
        ],
        "outputs": [("custom", CHAIN_TYPE, "chain"), ("string", "STRING", "summary")],
    },
]

# ---------------------------------------------------------------------------
# V1-style description of a spec (used by the stand-ins and by the tests)
# ---------------------------------------------------------------------------
_V1_TYPES = {"model": "MODEL", "clip": "CLIP", "vae": "VAE", "sampler": "SAMPLER", "sigmas": "SIGMAS",
             "int": "INT", "float": "FLOAT", "string": "STRING", "bool": "BOOLEAN", "image": "IMAGE",
             "audio": "AUDIO", "video": "VIDEO"}
_PLAIN_KEYS = ("default", "min", "max", "step", "round", "multiline", "dynamic_prompts", "advanced")


def _v1_input(item):
    kind = item["kind"]
    opts = {k: item[k] for k in _PLAIN_KEYS if k in item}
    opts["tooltip"] = item["tooltip"]
    if kind == "combo":
        opts.pop("options", None)
        return (list(item["options"]), opts)
    if kind == "custom":
        return (item["type"], opts)
    if kind == "autogrow":
        opts["template"] = {"input": {item["inner"]["id"]: _v1_input(item["inner"])},
                            "prefix": item["prefix"], "min": item["min"], "max": item["max"]}
        return ("COMFY_AUTOGROW_V3", opts)
    return (_V1_TYPES[kind], opts)


def v1_input_types(spec):
    """Plain INPUT_TYPES-style dict for one node spec."""
    out = {"required": {}, "optional": {}}
    for item in spec["inputs"]:
        out["optional" if item.get("optional") else "required"][item["id"]] = _v1_input(item)
    return out


def _output_type(o):
    kind, tname, _ = o
    return tname if kind in ("custom",) else _V1_TYPES[kind]


def check_spec(spec):
    """Return a list of plain-words problems with one spec (empty when it is fine)."""
    problems = []
    seen = set()
    if not spec["description"].strip():
        problems.append("%s has no description" % spec["id"])
    for item in spec["inputs"]:
        iid = item["id"]
        if iid in seen:
            problems.append("%s: input %s is listed twice" % (spec["id"], iid))
        seen.add(iid)
        tip = item.get("tooltip") or ""
        if not tip.strip() or len(tip) > MAX_TOOLTIP:
            problems.append("%s: input %s needs a tooltip of 1 to %d characters (has %d)"
                            % (spec["id"], iid, MAX_TOOLTIP, len(tip)))
        if item["kind"] == "autogrow":
            inner = item["inner"]
            itip = inner.get("tooltip") or ""
            if not itip.strip() or len(itip) > MAX_TOOLTIP:
                problems.append("%s: inner input %s needs a tooltip of 1 to %d characters"
                                % (spec["id"], inner["id"], MAX_TOOLTIP))
    return problems


# ---------------------------------------------------------------------------
# what each node does (plain functions; ComfyUI pieces are imported inside)
# ---------------------------------------------------------------------------
def run_settings(model, clip, vae, audio_vae, sampler, sigmas, width, height, chain_seed,
                 session_name, ref_image_size, handoff_mode="latent", drift_arrest=0.0):
    if ref_image_size not in common.REF_IMAGE_SIZES:
        raise ValueError("ref_image_size must be one of %s, got %r"
                         % (", ".join(common.REF_IMAGE_SIZES), ref_image_size))
    if handoff_mode not in common.HANDOFF_MODES:
        raise ValueError("handoff_mode must be one of %s, got %r"
                         % (", ".join(common.HANDOFF_MODES), handoff_mode))
    return ({
        "model": model, "clip": clip, "vae": vae, "audio_vae": audio_vae,
        "sampler": sampler, "sigmas": sigmas,
        "width": width, "height": height, "seed": chain_seed,
        "session_name": session_name, "ref_image_size": ref_image_size,
        "handoff_mode": handoff_mode, "drift_arrest": float(drift_arrest),
    },)


def with_model(settings, model):
    """The settings bundle this shot renders on, with its own model swapped in.

    A copy, never a change in place: one settings node feeds every segment in the chain, so writing into it
    would leak this shot's LoRA into all the others and into their cache keys.
    """
    if model is None:
        return settings
    return dict(settings, model=model)


def run_render_segment(settings, resume, prompt, seconds, handoff_seconds, seed_override,
                       unload_models_after, chain_state=None, model=None,
                       images=None, videos=None, video_audios=None, audios=None):
    import comfy.utils
    from comfy_api.input_impl import VideoFromFile

    # Before segment_key: model_digest reads settings["model"], so swapping it here is what makes changing a
    # shot's LoRA invalidate that shot's cache.
    settings = with_model(settings, model)
    segment = common.build_segment(prompt, seconds, handoff_seconds, seed_override,
                                   images, videos, video_audios, audios)
    handoff = segment["handoff"]

    if chain_state is None:
        sess = session_mod.Session(settings["session_name"])
        index, previous_key, anchor, records = 0, None, None, []
        reference = None
    else:
        sess = chain_state["sess_obj"]
        index = chain_state["index"] + 1
        previous_key = chain_state["key"]
        anchor = chain_state["anchor"]
        records = list(chain_state["segments"])
        # Segment 1's signature, carried down the whole chain. It is the only absolute reference a chain has.
        reference = chain_state.get("reference")

    segment["resolved_seed"] = common.resolve_seed(settings, segment, index)
    key = session_mod.segment_key(settings, segment, handoff, previous_key)
    manifest = sess.load() if resume else None

    if resume and sess.cached(manifest, index, key, needs_tail=bool(handoff)):
        common.log("%s -- reusing %s", common.describe(segment, index, anchor is not None),
                   os.path.basename(sess.segment_path(index)))
        rendered_length = video_io.frame_count(sess.segment_path(index))
        new_anchor = (video_io.anchor_from_disk(sess, index, settings["handoff_mode"])
                      if handoff else None)
        signature = session_mod.signature_from_record(manifest["segments"][index])
        # A reused segment still gets a thumbnail, so a resumed run visibly walks through what it keeps.
        preview_frame = video_io.last_frame(sess.segment_path(index))
    else:
        common.log("%s", common.describe(segment, index, anchor is not None))
        images_out, audio_out, samples = engine.render_segment(
            settings, segment, start_anchor=anchor)
        rendered_length = int(images_out.shape[0])
        video_io.save_clip(sess.segment_path(index), images_out, audio_out)

        # Both forms of the handoff go to disk whatever mode rendered it, so the session can be resumed,
        # repaired or extended in either mode later.
        pixel_tail = engine.take_tail(images_out, audio_out, handoff)
        lat_tail = engine.latent_tail(samples, handoff)
        signature = engine.latent_signature(samples)
        if pixel_tail is not None:
            video_io.save_clip(sess.tail_path(index), pixel_tail[0], pixel_tail[1],
                               exact_audio=True)
            # Saved uncorrected, deliberately: the file on disk is what this segment actually ended on, which
            # is what the repair node has to pin against. Drift correction is applied when the anchor is used.
            video_io.save_latent_tail(sess.tail_path(index), lat_tail)

        if handoff:
            new_anchor = (lat_tail if settings["handoff_mode"] == "latent"
                          else {"images": pixel_tail[0], "audio": pixel_tail[1]})
        else:
            new_anchor = None
        preview_frame = images_out[-1].clone()
        del images_out, audio_out, samples, pixel_tail, lat_tail
        engine.free_between_segments(unload_models_after)

    # Segment 1 seeds the reference and then it rides the chain unchanged.
    reference = reference or signature
    correction = 0.0
    if new_anchor is not None and settings.get("drift_arrest"):
        if new_anchor.get("video_latent") is None:
            common.log("drift_arrest is set but handoff_mode is 'pixel', which has no latent to correct -- "
                       "segment %d's handoff is going out uncorrected", index + 1)
        corrected = engine.arrest_drift(new_anchor, reference, signature, settings["drift_arrest"])
        correction = corrected.get("drift_correction", 0.0) if corrected else 0.0
        if correction:
            common.log("segment %d: drift correction %.4f per latent channel applied to the handoff",
                       index + 1, correction)
        new_anchor = corrected

    pbar = comfy.utils.ProgressBar(1)
    engine.push_preview(pbar, preview_frame, 1, 1)
    del preview_frame

    record = {
        "index": index, "key": key, "length": rendered_length, "handoff": handoff,
        "seconds": round(rendered_length / float(common.FPS), 3),
        "seed": segment["resolved_seed"], "prompt": segment["prompt"],
        "file": os.path.basename(sess.segment_path(index)),
        # Kept so a resumed run can still measure how far it has drifted without decoding every reused segment.
        "signature": session_mod.signature_to_record(signature),
    }
    if correction:
        record["drift_correction"] = round(correction, 6)
    # Slicing to `index` rather than appending covers rewiring in a shorter earlier segment upstream.
    records = records[:index] + [record]
    # Written every segment, not once at the end: a hard kill still leaves the manifest matching the disk.
    sess.save(records, extra={"width": settings["width"],
                              "height": settings["height"], "fps": common.FPS})

    chain = {"session": sess.name, "dir": sess.dir, "segments": records,
             "sess_obj": sess, "anchor": new_anchor, "index": index, "key": key,
             "reference": reference}
    summary = common.summarize_chain(chain)
    common.log("%s", summary.replace("\n", " | "))
    return (VideoFromFile(sess.segment_path(index)), chain, summary)


def run_chain_to_video(chain, crf, stabilize=0.0):
    records = chain["segments"]
    if not records:
        raise ValueError("this chain has no rendered segments")
    parts = []
    for index, record in enumerate(records):
        path = safe_join(chain["dir"], record["file"])
        if not os.path.exists(path):
            raise ValueError(
                "segment %d is missing from the session (%s). Run the chain again to render it."
                % (index + 1, path))
        skip = 0 if index == 0 else int(records[index - 1]["handoff"])
        parts.append((path, skip))

    from comfy_api.input_impl import VideoFromFile

    out_path = safe_join(chain["dir"], "%s.mp4" % chain["session"])
    out_path, frames = video_io.join(parts, out_path, crf=crf, stabilize=stabilize)
    common.log("joined %d segments -> %d frames (%.2fs) -> %s",
               len(parts), frames, frames / float(common.FPS), out_path)
    return (VideoFromFile(out_path), out_path)


def run_repair_segment(settings, session_name, segment_number, prompt, seconds,
                       handoff_seconds, seed_override, pin_ending, model=None, images=None,
                       videos=None, video_audios=None, audios=None):
    import comfy.utils
    from comfy_api.input_impl import VideoFromFile

    settings = with_model(settings, model)
    segment = common.build_segment(prompt, seconds, handoff_seconds, seed_override,
                                   images, videos, video_audios, audios)
    sess = session_mod.Session(session_name)
    manifest = sess.load()
    if not manifest:
        raise ValueError("there is no saved session in %s. Run the chain for this session_name first." % sess.dir)
    records = manifest["segments"]
    index = int(segment_number) - 1
    if index < 0 or index >= len(records):
        raise ValueError("session '%s' has %d segments; segment_number %d is out of range."
                         % (sess.name, len(records), segment_number))

    start_anchor = None
    if index > 0:
        previous_tail = sess.tail_path(index - 1)
        if not os.path.exists(previous_tail):
            raise ValueError(
                "segment %d has no handoff clip (%s), so segment %d has nothing to open on."
                % (index, previous_tail, segment_number))
        start_anchor = video_io.anchor_from_disk(sess, index - 1, settings["handoff_mode"])

    end_anchor = None
    is_last = index == len(records) - 1
    if pin_ending and not is_last:
        own_tail = sess.tail_path(index)
        if not os.path.exists(own_tail):
            raise ValueError(
                "segment %d has no handoff clip (%s) to pin its ending to." % (segment_number, own_tail))
        end_anchor = engine.picture_only(
            video_io.anchor_from_disk(sess, index, settings["handoff_mode"]))
        end_frames = engine.anchor_frames(end_anchor)
        if end_frames >= segment["length"]:
            raise ValueError(
                "the pinned ending is %d frames but the replacement segment is only %d long. "
                "Give the segment at least its original length." % (end_frames, segment["length"]))

    resolved = dict(segment, resolved_seed=common.resolve_seed(settings, segment, index))
    common.log("repairing segment %d of '%s'%s%s", segment_number, sess.name,
               " (opening pinned)" if start_anchor is not None else "",
               " (ending pinned)" if end_anchor is not None else "")

    pbar = comfy.utils.ProgressBar(1)
    images_out, audio_out, samples = engine.render_segment(
        settings, resolved, start_anchor=start_anchor, end_anchor=end_anchor)
    engine.push_preview(pbar, images_out[-1], 1, 1)

    target = sess.segment_path(index)
    if os.path.exists(target):
        shutil.copyfile(target, os.path.join(sess.dir, "seg_%02d.replaced.mp4" % (index + 1)))
    video_io.save_clip(target, images_out, audio_out)
    length = int(images_out.shape[0])

    # The handoff clip is NOT rewritten while the ending is pinned: the file on disk is what segment N+1
    # actually opens on, and the new ending was pinned to it.
    if not pin_ending and not is_last:
        handoff = records[index]["handoff"]
        tail = engine.take_tail(images_out, audio_out, handoff)
        if tail is not None:
            video_io.save_clip(sess.tail_path(index), tail[0], tail[1], exact_audio=True)
            video_io.save_latent_tail(sess.tail_path(index), engine.latent_tail(samples, handoff))
        common.log("pin_ending was off: segment %d's ending has moved, so segments %d..%d no longer join and "
                   "have to be re-rendered.", segment_number, segment_number + 1, len(records))

    del images_out, audio_out, samples
    engine.free_between_segments(False)

    records[index].update({
        "length": length,
        "seconds": round(length / float(common.FPS), 3),
        "seed": resolved["resolved_seed"],
        "prompt": resolved["prompt"],
        "repaired": True,
        "ending_pinned": end_anchor is not None,
    })
    sess.save(records, extra={k: v for k, v in manifest.items()
                              if k not in ("version", "session", "segments")})

    chain = {"session": sess.name, "dir": sess.dir, "segments": records}
    summary = common.summarize_chain(chain)
    common.log("%s", summary.replace("\n", " | "))
    return (VideoFromFile(target), chain, summary)


def fingerprint_load_session(session_name, handoff_mode="latent"):
    # The folder changes underneath the graph, so never trust a cached result.
    sess = session_mod.Session(session_name)
    try:
        return "%s:%s" % (os.path.getmtime(sess.manifest_path), handoff_mode)
    except OSError:
        return "missing"


def run_load_session(session_name, handoff_mode="latent"):
    if handoff_mode not in common.HANDOFF_MODES:
        raise ValueError("handoff_mode must be one of %s, got %r"
                         % (", ".join(common.HANDOFF_MODES), handoff_mode))
    sess = session_mod.Session(session_name)
    manifest = sess.load()
    if not manifest:
        raise ValueError("there is no saved session in %s. Check session_name." % sess.dir)
    records = manifest["segments"]
    if not records:
        raise ValueError("the session in %s has no segments." % sess.dir)
    last = records[-1]
    anchor = None
    if last.get("handoff") and os.path.exists(sess.tail_path(last["index"])):
        anchor = video_io.anchor_from_disk(sess, last["index"], handoff_mode)
    chain = {"session": sess.name, "dir": sess.dir, "segments": records,
             "sess_obj": sess, "anchor": anchor, "index": last["index"],
             "key": last["key"],
             # Segment 1's signature, not the last one's. Extending a session has to keep measuring drift
             # against the same shot the original chain did, or the new segments would lock the drift in.
             "reference": session_mod.signature_from_record(records[0])}
    return (chain, common.summarize_chain(chain))


RUNNERS = {
    "SYH3ChainSettings": run_settings,
    "SYH3RenderSegment": run_render_segment,
    "SYH3ChainToVideo": run_chain_to_video,
    "SYH3RepairSegment": run_repair_segment,
    "SYH3LoadSession": run_load_session,
}

# ---------------------------------------------------------------------------
# building the classes
# ---------------------------------------------------------------------------


def _load_io():
    """The V3 schema module, or None if this ComfyUI is too old to have Autogrow."""
    try:
        from comfy_api.latest import io
    except Exception:
        return None
    return io if hasattr(io, "Autogrow") and hasattr(io, "Schema") else None


def _core_present():
    try:
        import importlib.util
        return importlib.util.find_spec("comfy_extras.nodes_minimax_h3") is not None
    except Exception:
        return False


_CUSTOM_TYPES = {}


def _custom(io, name):
    if name not in _CUSTOM_TYPES:
        _CUSTOM_TYPES[name] = io.Custom(name)
    return _CUSTOM_TYPES[name]


def _io_class(io, kind):
    return {"model": io.Model, "clip": io.Clip, "vae": io.Vae, "sampler": io.Sampler, "sigmas": io.Sigmas,
            "int": io.Int, "float": io.Float, "string": io.String, "combo": io.Combo, "bool": io.Boolean,
            "image": io.Image, "audio": io.Audio, "video": io.Video}[kind]


def _to_io_input(io, item):
    kw = {k: item[k] for k in _PLAIN_KEYS if k in item}
    kw["tooltip"] = item["tooltip"]
    if item.get("optional"):
        kw["optional"] = True
    kind = item["kind"]
    if kind == "autogrow":
        inner = _to_io_input(io, item["inner"])
        template = io.Autogrow.TemplatePrefix(input=inner, prefix=item["prefix"],
                                              min=item["min"], max=item["max"])
        return io.Autogrow.Input(item["id"], template=template, optional=bool(item.get("optional")),
                                 tooltip=item["tooltip"])
    if kind == "custom":
        return _custom(io, item["type"]).Input(item["id"], **kw)
    if kind == "combo":
        return io.Combo.Input(item["id"], options=list(item["options"]), **kw)
    return _io_class(io, kind).Input(item["id"], **kw)


def _to_io_output(io, out):
    kind, tname, display = out
    if kind == "custom":
        return _custom(io, tname).Output(display_name=display)
    return _io_class(io, kind).Output(display_name=display)


def _build_v3_class(io, spec):
    runner = RUNNERS[spec["id"]]

    def define_schema(cls):
        return io.Schema(
            node_id=spec["id"],
            display_name=spec["name"] + " SY",
            category=CATEGORY,
            description=spec["description"],
            inputs=[_to_io_input(io, i) for i in spec["inputs"]],
            outputs=[_to_io_output(io, o) for o in spec["outputs"]],
        )

    def execute(cls, **inputs):
        return io.NodeOutput(*runner(**inputs))

    ns = {"define_schema": classmethod(define_schema), "execute": classmethod(execute)}
    if spec["id"] == "SYH3LoadSession":
        def fingerprint_inputs(cls, **inputs):
            return fingerprint_load_session(**inputs)
        ns["fingerprint_inputs"] = classmethod(fingerprint_inputs)
    return type(spec["id"], (io.ComfyNode,), ns)


def _build_stand_in(spec):
    types_out = tuple(_output_type(o) for o in spec["outputs"])
    names_out = tuple(o[2] for o in spec["outputs"])

    def input_types(cls):
        return v1_input_types(spec)

    def execute(self, **inputs):
        raise ValueError("%s needs a ComfyUI with the V3 node schema and the MiniMax H3 core nodes."
                         % spec["name"])

    return type(spec["id"], (), {
        "DESCRIPTION": spec["description"], "CATEGORY": CATEGORY, "FUNCTION": "execute",
        "RETURN_TYPES": types_out, "RETURN_NAMES": names_out,
        "INPUT_TYPES": classmethod(input_types), "execute": execute,
    })


def _setup():
    io = _load_io()
    reason = ""
    if io is None:
        reason = "this ComfyUI has no V3 Autogrow inputs (comfy_api.latest.io.Autogrow)"
    elif not _core_present():
        reason = "this ComfyUI has no MiniMax H3 core nodes (needs ComfyUI 0.34.0 or newer)"
    classes = {}
    if not reason:
        try:
            for spec in SPECS:
                cls = _build_v3_class(io, spec)
                cls.GET_SCHEMA()  # fail here, at load time, not later inside the node menu
                classes[spec["id"]] = cls
        except Exception as exc:
            reason = "the V3 schema of this ComfyUI did not accept the H3 chain nodes (%s: %s)" % (type(exc).__name__, exc)
    if reason:
        classes = {spec["id"]: _build_stand_in(spec) for spec in SPECS}
    return classes, reason


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
_classes, SY_NOT_LOADED_REASON = _setup()
for _spec in SPECS:
    NODE_CLASS_MAPPINGS[_spec["id"]] = _classes[_spec["id"]]
    NODE_DISPLAY_NAME_MAPPINGS[_spec["id"]] = _spec["name"] + " SY"
# __init__.py registers these in ComfyUI only when this is True (the stand-ins are never registered).
SY_REGISTER = not SY_NOT_LOADED_REASON
