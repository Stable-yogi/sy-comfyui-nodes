"""Tests for the H3 chain nodes: frame maths, seeds, summary text, session files, data table, stand-in classes.

Ported in part from the self-checks in ComfyUI-H3-Continuous (tools/test_latent_handoff.py, MIT, Loop Forge).
The tensor checks at the end only run when torch and a ComfyUI folder are reachable (set SY_COMFY_ROOT);
the plain selftest python has neither, so there they are skipped and not counted.
"""
import os
import sys
import tempfile

NODES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")
sys.path.insert(0, NODES)
if os.environ.get("SY_COMFY_ROOT") and os.path.isdir(os.environ["SY_COMFY_ROOT"]):
    sys.path.insert(0, os.environ["SY_COMFY_ROOT"])  # only for a run with a ComfyUI python; the selftest has none
import _sy_h3chain_common as common
import _sy_h3chain_engine as engine
import _sy_h3chain_session as sess_mod
import _sy_h3chain_video as video_io
import sy_h3_chain as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


class Fake:
    """A stand-in with a shape, for the checks that need no torch."""

    def __init__(self, *shape):
        self.shape = shape


def run():
    n = [0]

    def ok(cond, msg="check failed"):
        n[0] += 1
        assert cond, msg

    # ---- frame grid: 17k + 5 -------------------------------------------------
    for k in range(0, 22):
        f = 17 * k + 5
        ok(common.generation_length(f) == f, "generation_length(%d)" % f)
        ok(common.guide_length(f) == f, "guide_length(%d)" % f)
    ok(common.generation_length(96) == 107)
    ok(common.generation_length(1) == 5)
    ok(common.generation_length(0) == 5)
    ok(common.generation_length(192) == 192)  # 8 s at 24 fps is already on the grid
    ok(common.guide_length(38) == 22)
    ok(common.guide_length(4) == 0)
    ok(common.guide_length(-3) == 0)
    ok(common.guide_length(39) == 39)
    ok(common.guide_length(55) == 39)
    ok(common.seconds_to_frames(8) == 192)
    ok(common.seconds_to_frames(1.625) == 39)
    ok(common.seconds_to_frames("0.5") == 12)
    ok(common.audio_latent_frames(39) == 65)
    ok(common.audio_latent_frames(24) == 40)
    for k in range(0, 14):  # 17k+5 pixel frames are 5k+2 latent steps, and those steps cover them again
        ok(common.latent_cover_frames(5 * k + 2) == 17 * k + 5, "latent_cover_frames(%d)" % (5 * k + 2))

    # ---- autogrow ordering ---------------------------------------------------
    ok(common.ordered_autogrow({"image_3": "c", "image_0": "a", "image_1": None}) == [(0, "a"), (3, "c")])
    ok(common.ordered_autogrow(None) == [])
    ok(common.ordered_autogrow({}) == [])
    ok(common.ordered_autogrow({"video_audio_2": "x", "video_audio_10": "y"}) == [(2, "x"), (10, "y")])
    ok(common.ordered_autogrow({"weird": "w"}) == [(0, "w")])

    # ---- building a segment --------------------------------------------------
    seg = common.build_segment("hi", 8.0, 1.625, 0, images={"image_1": "B", "image_0": "A"}, audios={"audio_0": "S"})
    ok(seg["length"] == 192 and seg["handoff"] == 39)
    ok(seg["images"] == ["A", "B"])
    ok(seg["audios"] == ["S"] and seg["videos"] == [] and seg["video_audios"] == [])
    ok(seg["seed"] == 0 and seg["prompt"] == "hi")
    ok(common.build_segment("p", 5.0, 0.0, 7)["handoff"] == 0)
    ok(common.build_segment("p", 5.0, 0.0, 7)["seed"] == 7)
    ok(common.build_segment("p", 0.25, 0.0, 0)["length"] == 22)
    ok(raises(common.build_segment, "p", 1.0, 2.0, 0), "handoff as long as the shot must fail")
    ok(raises(common.build_segment, "p", 2.0, 4.0, 0), "handoff longer than the shot must fail")
    ok(raises(common.build_segment, "p", 0, 0.0, 0), "zero seconds must fail")
    ok(raises(common.build_segment, "p", 8.0, -1.0, 0), "negative handoff must fail")
    try:
        common.build_segment("p", 1.0, 2.0, 0)
    except ValueError as e:
        ok("must be shorter" in str(e))

    # ---- seeds ---------------------------------------------------------------
    ok(common.resolve_seed({"seed": 100}, {"seed": 0}, 0) == 100 + 9973)
    ok(common.resolve_seed({"seed": 100}, {"seed": 0}, 2) == 100 + 3 * 9973)
    ok(common.resolve_seed({"seed": 100}, {"seed": 55}, 3) == 55)
    ok(common.resolve_seed({"seed": (1 << 63) - 1}, {"seed": 0}, 0) == (9973 - 1))
    ok(common.resolve_seed({"seed": 5}, {"seed": 0}, 0) != common.resolve_seed({"seed": 5}, {"seed": 0}, 1))
    ok(common.resolve_seed({"seed": "12"}, {"seed": 0}, 0) == 12 + 9973)

    # ---- text ----------------------------------------------------------------
    ok(common.describe({"length": 192}, 0, False) == "segment 1: 192 frames (8.00s)")
    ok(common.describe({"length": 192}, 1, True).endswith("opening on the previous segment's tail"))
    chain = {"dir": "out/h3_continuous/t", "segments": [
        {"index": 0, "length": 192, "handoff": 39, "seconds": 8.0, "seed": 1},
        {"index": 1, "length": 192, "handoff": 0, "seconds": 8.0, "seed": 2, "repaired": True, "drift_correction": 0.0123},
    ]}
    text = common.summarize_chain(chain)
    ok(text.splitlines()[0] == "2 segments -> 14.38s (345 frames) once the replayed handoffs come off", text.splitlines()[0])
    ok("(repaired)" in text and "drift -0.012" in text)
    ok(text.splitlines()[1] == "   1   8.00s  handoff 1.62s  seed 1", text.splitlines()[1])
    ok(text.splitlines()[-1] == "  in out/h3_continuous/t")
    ok(common.summarize_chain({"dir": "d", "segments": [
        {"index": 0, "length": 107, "handoff": 0, "seconds": 4.458, "seed": 9}]}).startswith("1 segments -> 4.46s (107 frames)"))

    # ---- session: names, digests, keys --------------------------------------
    ok(sess_mod.sanitize("my chain") == "my_chain")
    ok(sess_mod.sanitize("../../evil") == "evil")
    ok(".." not in sess_mod.sanitize("a..b"))
    ok(sess_mod.sanitize("   ") == "session")
    ok(sess_mod.sanitize(None) == "session")
    ok(len(sess_mod.sanitize("x" * 200)) == 64)
    ok(sess_mod.sanitize("a/b\\c") == "a_b_c")
    ok(sess_mod.digest("abc") == sess_mod.digest("abc"))
    ok(sess_mod.digest("abc") != sess_mod.digest("abd"))
    ok(sess_mod.digest(["a", "b"]) == "[" + sess_mod.digest("a") + "," + sess_mod.digest("b") + "]")

    class Sampler:
        extra_options = {"b": 1, "a": 2}

    ok(sess_mod.sampler_digest(Sampler()) == sess_mod.sampler_digest(Sampler()))
    ok(len(sess_mod.sampler_digest(Sampler())) == 16)
    ok(sess_mod.model_digest(object()) != "")
    ok(sess_mod.model_digest(None) in ("unknown",) or len(sess_mod.model_digest(None)) == 16)

    class Patcher:
        model = Sampler()
        patches = {"layer.weight": [(0.8, "w", 1.0)]}

    class Patcher2(Patcher):
        patches = {"layer.weight": [(0.5, "w", 1.0)]}

    ok(sess_mod.model_digest(Patcher()) != sess_mod.model_digest(Patcher2()), "a LoRA strength change must change the key")

    settings = {"width": 864, "height": 480, "ref_image_size": "match", "sigmas": [1.0, 0.5], "sampler": Sampler(),
                "model": Patcher(), "handoff_mode": "latent", "drift_arrest": 0.0}
    segment = {"prompt": " hello ", "length": 192, "resolved_seed": 5, "images": [], "videos": [],
               "video_audios": [], "audios": []}
    k1 = sess_mod.segment_key(settings, segment, 39, None)
    ok(k1 == sess_mod.segment_key(settings, segment, 39, None))
    ok(len(k1) == 20)
    ok(k1 != sess_mod.segment_key(settings, dict(segment, prompt="other"), 39, None))
    ok(k1 != sess_mod.segment_key(settings, segment, 22, None))
    ok(k1 != sess_mod.segment_key(settings, dict(segment, resolved_seed=6), 39, None))
    ok(k1 == sess_mod.segment_key(settings, dict(segment, prompt="hello"), 39, None), "prompt is stripped")
    ok(k1 != sess_mod.segment_key(settings, segment, 39, "abc"), "the previous key is part of the key")
    # first segment keys stay the same whatever the handoff mode (so old sessions stay cached)
    ok(k1 == sess_mod.segment_key(dict(settings, handoff_mode="pixel", drift_arrest=0.5), segment, 39, None))
    k2 = sess_mod.segment_key(settings, segment, 39, "abc")
    ok(k2 != sess_mod.segment_key(dict(settings, handoff_mode="pixel"), segment, 39, "abc"))
    ok(k2 != sess_mod.segment_key(dict(settings, drift_arrest=0.5), segment, 39, "abc"))
    ok(k2 != sess_mod.segment_key(dict(settings, model=Patcher2()), segment, 39, "abc"))

    rec = sess_mod.signature_to_record({"mean": [0.123456789, 1], "std": [2, 3.0000004]})
    ok(rec == {"mean": [0.123457, 1.0], "std": [2.0, 3.0]}, rec)
    ok(sess_mod.signature_to_record(None) is None)
    ok(sess_mod.signature_from_record(None) is None)
    ok(sess_mod.signature_from_record({"index": 0}) is None)

    # ---- session: folder and manifest ---------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        s = sess_mod.Session("my chain", base_dir=tmp)
        ok(s.name == "my_chain")
        ok(os.path.isdir(s.dir) and os.path.basename(os.path.dirname(s.dir)) == "h3_continuous")
        ok(os.path.basename(s.segment_path(0)) == "seg_01.mp4")
        ok(os.path.basename(s.segment_path(11)) == "seg_12.mp4")
        ok(os.path.basename(s.tail_path(1)) == "seg_02.tail.mp4")
        ok(os.path.basename(s.joined_path()) == "my_chain.mp4")
        ok(os.path.basename(s.manifest_path) == "manifest.json")
        evil = sess_mod.Session("../../outside", base_dir=tmp)
        ok(os.path.realpath(evil.dir).startswith(os.path.realpath(tmp)), "a session name cannot leave the output folder")
        ok(s.load() is None, "no manifest yet")
        records = [{"index": 0, "key": "k0", "length": 192, "handoff": 39, "file": "seg_01.mp4"}]
        saved = s.save(records, extra={"width": 864})
        ok(saved["version"] == 2 and saved["width"] == 864 and saved["session"] == "my_chain")
        ok(s.load()["segments"] == records)
        ok(not s.cached(None, 0, "k0", False))
        manifest = s.load()
        ok(not s.cached(manifest, 0, "k0", False), "segment file is missing")
        open(s.segment_path(0), "wb").close()
        ok(s.cached(manifest, 0, "k0", False))
        ok(not s.cached(manifest, 0, "other", False), "a different key must not match")
        ok(not s.cached(manifest, 1, "k0", False), "index past the end")
        ok(not s.cached(manifest, 0, "k0", True), "tail clip is missing")
        open(s.tail_path(0), "wb").close()
        ok(s.cached(manifest, 0, "k0", True))
        with open(s.manifest_path, "w", encoding="utf-8") as f:
            f.write('{"version": 1, "segments": []}')
        ok(s.load() is None, "an old manifest version is ignored")
        with open(s.manifest_path, "w", encoding="utf-8") as f:
            f.write("not json")
        ok(s.load() is None, "a broken manifest is ignored")
        ok(video_io.latent_path("a/seg_01.tail.mp4").endswith("seg_01.tail.latent.safetensors"))
        ok(video_io._wav_path("a/seg_01.tail.mp4").endswith("seg_01.tail.wav"))
        ok(video_io.ceil_div(7, 2) == 4)
        # a chain entry that points outside the session folder is refused by the join node
        chain_bad = {"dir": tmp, "session": "x", "segments": [{"file": "../escape.mp4", "handoff": 0}]}
        ok(raises(m.run_chain_to_video, chain_bad, 14.0), "a segment file outside the session folder is refused")
        ok(raises(m.run_chain_to_video, {"dir": tmp, "session": "x", "segments": []}, 14.0), "an empty chain is refused")

    # ---- engine, parts that need no tensors ---------------------------------
    ok(engine.anchor_frames(None) == 0)
    ok(engine.anchor_frames({"video_latent": Fake(1, 24, 7, 2, 2)}) == 22)
    ok(engine.anchor_frames({"images": Fake(39, 4, 4, 3)}) == 39)
    ok(engine.picture_only(None) is None)
    ok(engine.picture_only({"images": "i", "audio": "a"}) == {"images": "i", "audio": None})
    ok(engine.picture_only({"video_latent": "v", "audio_latent": "a"}) == {"video_latent": "v", "audio_latent": None})
    ok(engine.take_tail("images", None, 0) is None)
    ok(engine.slice_audio(None, 0, 1) is None)
    ok(engine.arrest_drift(None, {"mean": 1}, {"mean": 1}, 0.5) is None)
    anchor = {"video_latent": "v"}
    ok(engine.arrest_drift(anchor, None, {"mean": 1}, 0.5) is anchor)
    ok(engine.arrest_drift(anchor, {"mean": 1}, {"mean": 1}, 0.0) is anchor)
    ok(engine.arrest_drift({"images": "i"}, {"mean": 1}, {"mean": 1}, 0.5) == {"images": "i"})
    ok(engine.latent_tail("samples", 0) is None)
    ok(engine.latent_tail("samples", -5) is None)
    ok(raises(engine._av_streams, _NoAudio()), "an AV latent needs an audio stream")
    if _find_core() is None:  # on a ComfyUI without the H3 core the helper explains itself
        ok(raises(engine.core), "core() must raise ValueError when the H3 core nodes are missing")

    # ---- the data table, the stand-in classes and the names -----------------
    ids = [s_["id"] for s_ in m.SPECS]
    ok(ids == ["SYH3ChainSettings", "SYH3RenderSegment", "SYH3ChainToVideo", "SYH3RepairSegment", "SYH3LoadSession"])
    ok(len(set(ids)) == 5)
    names = [s_["name"] for s_ in m.SPECS]
    ok(names == ["H3 Chain Settings", "H3 Render Segment", "H3 Chain To Video", "H3 Repair Segment", "H3 Load Session"])
    ok(set(m.NODE_CLASS_MAPPINGS) == set(ids))
    for s_ in m.SPECS:
        ok(m.check_spec(s_) == [], "%s: %s" % (s_["id"], m.check_spec(s_)))
        ok(m.NODE_DISPLAY_NAME_MAPPINGS[s_["id"]] == s_["name"] + " SY")
        cls = m.NODE_CLASS_MAPPINGS[s_["id"]]
        ok(cls.CATEGORY == "SY/Utility")
        ok(bool(cls.DESCRIPTION.strip()))
        ok(hasattr(cls, cls.FUNCTION))
        types = cls.INPUT_TYPES()
        listed = set(types.get("required", {})) | set(types.get("optional", {}))
        ok(listed == {i["id"] for i in s_["inputs"]})
        for section in ("required", "optional"):
            for iid, d in types.get(section, {}).items():
                tip = d[1].get("tooltip", "")
                ok(0 < len(tip) <= 120, "%s.%s tooltip is %d characters" % (s_["id"], iid, len(tip)))
        ok(len(list(cls.RETURN_TYPES)) == len(list(cls.RETURN_NAMES)) == len(s_["outputs"]))
        ok(runner_exists(s_["id"]))
    def options(d):  # classic form keeps the list first, the V3 form keeps it in the dict
        return list(d[0]) if isinstance(d[0], (list, tuple)) else list(d[1]["options"])

    settings_in = m.NODE_CLASS_MAPPINGS["SYH3ChainSettings"].INPUT_TYPES()["required"]
    ok(options(settings_in["handoff_mode"]) == ["latent", "pixel"])
    ok(options(settings_in["ref_image_size"]) == ["match", "max"])
    ok(settings_in["chain_seed"][1]["max"] == 0xffffffffffffffff)
    ok("seed" not in settings_in, "the input must not be called seed (the page would add a randomise control)")
    ok(tuple(m.NODE_CLASS_MAPPINGS["SYH3ChainSettings"].RETURN_TYPES) == ("SY_H3_SETTINGS",))
    render = m.NODE_CLASS_MAPPINGS["SYH3RenderSegment"]
    ok(tuple(render.RETURN_TYPES) == ("VIDEO", "SY_H3_CHAIN", "STRING"))
    ok(tuple(render.RETURN_NAMES) == ("video", "chain_state", "summary"))
    r_in = render.INPUT_TYPES()
    ok(r_in["required"]["settings"][0] == "SY_H3_SETTINGS")
    ok(r_in["optional"]["chain_state"][0] == "SY_H3_CHAIN")
    ok(r_in["optional"]["images"][0] == "COMFY_AUTOGROW_V3")
    ok(r_in["optional"]["images"][1]["template"]["prefix"] == "image_")
    ok(r_in["optional"]["images"][1]["template"]["max"] == 9)
    ok(r_in["optional"]["videos"][1]["template"]["max"] == 3)
    ok(r_in["optional"]["video_audios"][1]["template"]["prefix"] == "video_audio_")
    ok(r_in["optional"]["audios"][1]["template"]["prefix"] == "audio_")
    ok(r_in["required"]["seconds"][1]["default"] == 8.0)
    ok(r_in["required"]["handoff_seconds"][1]["default"] == 1.625)
    ok(r_in["required"]["resume"][1]["default"] is True)
    repair_in = m.NODE_CLASS_MAPPINGS["SYH3RepairSegment"].INPUT_TYPES()
    ok(repair_in["required"]["segment_number"][1]["min"] == 1)
    ok(repair_in["required"]["pin_ending"][1]["default"] is True)
    ok(m.NODE_CLASS_MAPPINGS["SYH3ChainToVideo"].INPUT_TYPES()["required"]["chain"][0] == "SY_H3_CHAIN")
    ok(tuple(m.NODE_CLASS_MAPPINGS["SYH3LoadSession"].RETURN_NAMES) == ("chain", "summary"))
    ok(m.SY_REGISTER == (m.SY_NOT_LOADED_REASON == ""))
    if not m.SY_REGISTER:
        ok(raises(m.NODE_CLASS_MAPPINGS["SYH3ChainSettings"]().execute), "a stand-in never runs")

    # a spec with a long tooltip or a missing one is reported
    bad = {"id": "SYX", "description": "d", "inputs": [
        {"kind": "int", "id": "a", "tooltip": "x" * 121}, {"kind": "int", "id": "b", "tooltip": " "},
        {"kind": "int", "id": "a", "tooltip": "fine"}]}
    problems = m.check_spec(bad)
    ok(len(problems) == 3, problems)

    # runner checks that need no ComfyUI
    ok(raises(m.run_settings, 1, 2, 3, 4, 5, 6, 864, 480, 0, "x", "huge"), "bad ref_image_size")
    ok(raises(m.run_settings, 1, 2, 3, 4, 5, 6, 864, 480, 0, "x", "match", "both"), "bad handoff_mode")
    out = m.run_settings("M", "C", "V", "A", "S", "G", 864, 480, 7, "sess", "match")[0]
    ok(out["seed"] == 7 and out["handoff_mode"] == "latent" and out["drift_arrest"] == 0.0 and out["model"] == "M")
    ok(m.with_model({"model": "M"}, None) == {"model": "M"})
    base = {"model": "M", "x": 1}
    swapped = m.with_model(base, "L")
    ok(swapped["model"] == "L" and base["model"] == "M", "with_model must not change the shared settings")
    ok(raises(m.run_load_session, "s", "both"))

    _tensor_checks(ok)
    return n[0]


class _NoAudio:
    is_nested = False

    def unbind(self):
        return (1,)


def runner_exists(node_id):
    return callable(m.RUNNERS.get(node_id))


def _find_core():
    try:
        import importlib.util
        return importlib.util.find_spec("comfy_extras.nodes_minimax_h3")
    except Exception:
        return None


def _tensor_checks(ok):
    """The ported latent-handoff self-checks. Skipped (and not counted) without torch and a ComfyUI folder."""
    root = os.environ.get("SY_COMFY_ROOT")
    if not root or not os.path.isdir(root):
        return 0
    try:
        import torch
    except ImportError:
        return 0
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        import comfy.nested_tensor
        video_latent_t = engine.core().video_latent_t
    except Exception:
        return 0
    chk = ok

    FPS, AFPS = common.FPS, common.AUDIO_LATENT_FPS

    def make(frames, h=30, w=54, seed=0):
        g = torch.Generator().manual_seed(seed)
        t = video_latent_t(frames)
        at = int(round(frames / float(FPS) * AFPS))
        return comfy.nested_tensor.NestedTensor((torch.randn(1, 24, t, h, w, generator=g),
                                                 torch.randn(1, 32, 2, at, generator=g)))

    for k in range(0, 22):
        chk(video_latent_t(17 * k + 5) == 5 * k + 2)
    for k in range(1, 14):
        segment = 17 * k + 5
        samples = make(segment)
        source = samples.unbind()[0]
        for mm in range(0, k):
            handoff = 17 * mm + 5
            anchor = engine.latent_tail(samples, handoff)
            chk(engine.anchor_frames(anchor) == handoff)
            tokens = video_latent_t(handoff)
            chk(torch.equal(anchor["video_latent"], source[:1, :, source.shape[2] - tokens:]))
            chk(anchor["audio_latent"].shape[-1] == common.audio_latent_frames(handoff))
    chk(engine.latent_tail(make(107), 0) is None)
    chk(raises(engine.latent_tail, make(22), 39))
    anchor = engine.latent_tail(make(107), 22)
    bare = engine.picture_only(anchor)
    chk(bare["audio_latent"] is None and torch.equal(bare["video_latent"], anchor["video_latent"]))
    reference = engine.latent_signature(make(107, seed=1))
    current = engine.latent_signature(make(107, seed=2))
    chk(tuple(reference["mean"].shape) == (24,) and tuple(reference["std"].shape) == (24,))
    anchor = engine.latent_tail(make(107, seed=2), 22)
    same = engine.arrest_drift(anchor, reference, reference, 0.5)
    chk(float((same["video_latent"] - anchor["video_latent"]).abs().max()) == 0.0)
    chk(engine.arrest_drift(anchor, reference, current, 0.0) is anchor)
    half = engine.arrest_drift(anchor, reference, current, 0.5)
    full = engine.arrest_drift(anchor, reference, current, 1.0)
    d_half = (half["video_latent"] - anchor["video_latent"]).mean(dim=(0, 2, 3, 4))
    d_full = (full["video_latent"] - anchor["video_latent"]).mean(dim=(0, 2, 3, 4))
    chk(torch.allclose(d_half * 2, d_full, atol=1e-5))
    wild = {"mean": reference["mean"] + 99.0, "std": reference["std"]}
    clamped = engine.arrest_drift(anchor, wild, current, 1.0)
    shift = (clamped["video_latent"] - anchor["video_latent"]).mean(dim=(0, 2, 3, 4))
    chk(bool((shift.abs() <= wild["std"] * 0.35 + 1e-4).all()))
    return 0
