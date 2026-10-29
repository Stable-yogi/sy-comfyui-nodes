import json
import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_bundle as m

NOW = datetime(2026, 10, 28, 14, 5, 9)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.clean_bundle_name("h3-preview-001") == "h3-preview-001"; n += 1
    assert m.clean_bundle_name("my bundle!") == "my_bundle_"; n += 1
    for bad in ("", "   ", "..", "a/b", "a\\b", "../x", "a..b", "***"):
        assert raises(m.clean_bundle_name, bad), bad
        n += 1
    meta = m.build_meta(7, "hello", [3, 1], NOW)
    assert meta == {"seed": 7, "prompt_chars": 5, "has_refs": [1, 3], "created": "2026-10-28T14:05:09"}; n += 1
    assert m.build_meta(2 ** 64 - 1, "", [], NOW)["seed"] == 2 ** 64 - 1; n += 1
    assert raises(m.build_meta, -1, "x", []); n += 1
    assert raises(m.build_meta, 2 ** 64, "x", []); n += 1
    assert raises(m.build_meta, 1, "x", [4]); n += 1
    assert m.parse_meta(json.dumps(meta)) == (7, [1, 3]); n += 1
    assert raises(m.parse_meta, "not json"); n += 1
    assert raises(m.parse_meta, "{}"); n += 1
    assert raises(m.parse_meta, '{"seed": 1, "has_refs": [9]}'); n += 1
    assert raises(m.parse_meta, '{"seed": true}'); n += 1
    assert m.bundle_choices([]) == ["(none)"]; n += 1
    assert m.bundle_choices([("b", True), ("a", True), ("c", False)]) == ["a", "b"]; n += 1
    assert m.bundle_choices([("c", False)]) == ["(none)"]; n += 1
    # real folder work in a temporary folder (no torch needed)
    with tempfile.TemporaryDirectory() as tmp:
        assert m.list_bundles(tmp) == ["(none)"]; n += 1
        root = os.path.join(tmp, "sy_bundles")
        os.makedirs(os.path.join(root, "one"))
        os.makedirs(os.path.join(root, "two"))
        open(os.path.join(root, "two", m.LATENT_FILE), "wb").close()
        assert m.list_bundles(tmp) == ["two"]; n += 1
        assert m.bundle_folder(tmp, "two") == os.path.realpath(os.path.join(root, "two")); n += 1
        assert raises(m.bundle_folder, tmp, "(none)"); n += 1
        assert raises(m.bundle_folder, tmp, "../x"); n += 1
        assert raises(m.read_bundle, tmp, "one"); n += 1  # missing latent.safetensors raises before any torch use
        open(os.path.join(root, "one", m.LATENT_FILE), "wb").close()
        assert raises(m.read_bundle, tmp, "one"); n += 1  # missing meta.json
        with open(os.path.join(root, "one", m.META_FILE), "w", encoding="utf-8") as f:
            f.write("{}")
        assert raises(m.read_bundle, tmp, "one"); n += 1  # bad meta
    # nested latent (video + audio together): saved as numbered parts, rebuilt in the same order
    class Part:
        def __init__(self, tag):
            self.tag = tag

        def detach(self):
            return self

        def cpu(self):
            return self

        def contiguous(self):
            return self

    class Nested:
        is_nested = True

        def __init__(self, tensors):
            self.tensors = list(tensors)

    flat = m.flatten_latent({"samples": Nested([Part("v"), Part("a")]), "noise_mask": Part("m"), "batch_index": [0]})
    assert sorted(flat) == ["noise_mask", "samples.nested.0", "samples.nested.1"]; n += 1
    back = m.restore_latent(flat, Nested)
    assert [p.tag for p in back["samples"].tensors] == ["v", "a"] and back["noise_mask"].tag == "m"; n += 1
    assert m.flatten_latent({"batch_index": [0]}) == {}; n += 1
    assert m.SYH3SaveBundle.OUTPUT_NODE is True; n += 1
    assert m.SYH3LoadBundle.RETURN_NAMES == ("latent", "prompt", "seed", "bundle_folder", "reference_1"); n += 1
    return n
