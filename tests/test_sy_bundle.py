import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_bundle as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    # ---- make_bundle
    assert m.make_bundle() == {}; n += 1
    b = m.make_bundle(None, model="M", seed=5, text="hi")
    assert b == {"model": "M", "seed": 5, "text": "hi"}; n += 1
    assert m.make_bundle(None, model=None, seed=0) == {"seed": 0}; n += 1                # None left out, 0 kept
    assert m.make_bundle(None, text="") == {"text": ""}; n += 1                          # empty text kept
    b2 = m.make_bundle(b, seed=9, vae="V")
    assert b2 == {"model": "M", "seed": 9, "text": "hi", "vae": "V"}; n += 1              # override and add
    assert b == {"model": "M", "seed": 5, "text": "hi"}; n += 1                          # no mutation
    assert b2 is not b; n += 1
    same = m.make_bundle(b)
    assert same == b and same is not b; n += 1
    # chain of two bundles
    c = m.make_bundle(m.make_bundle(None, model="M", clip="C"), positive="P", clip="C2")
    assert c == {"model": "M", "clip": "C2", "positive": "P"}; n += 1
    # nested content is not copied or changed
    inner = {"a": [1, 2]}
    d = m.make_bundle(None, extra=inner)
    assert d["extra"] is inner; n += 1
    # refusals
    for bad in ("text", 5, [1], ("a", 1)):
        msg = refuses(m.make_bundle, bad)
        assert msg and "Bundle SY" in msg, bad
    n += 1
    assert "base bundle" in refuses(m.make_bundle, 3); n += 1
    assert refuses(m.keys_text, "x") and refuses(m.missing_keys, 1, ["a"]) and refuses(m.bundle_get, None, "a"); n += 1
    # ---- bundle_get / keys_text / missing_keys
    assert m.bundle_get(b, "seed", 0) == 5 and m.bundle_get(b, "vae", "none") == "none" and m.bundle_get(b, "vae") is None; n += 1
    assert m.keys_text({}) == "" and m.keys_text(b) == "model, seed, text"; n += 1
    assert m.missing_keys(b, ["model", "vae", "seed", "clip"]) == ["vae", "clip"]; n += 1
    assert m.missing_keys({}, []) == [] and m.missing_keys(b, ["model"]) == []; n += 1
    assert m.custom_keys({"model": 1, "mine": 2, "extra": 3}) == ["mine", "extra"]; n += 1
    # ---- extra name
    assert m.clean_extra_name("") == "extra" and m.clean_extra_name(None) == "extra" and m.clean_extra_name("  my thing ") == "my thing"; n += 1
    assert "already used" in refuses(m.clean_extra_name, "model") and refuses(m.clean_extra_name, "seed"); n += 1
    assert m.extra_value({"extra": 1, "mine": 2}) == 1 and m.extra_value({"mine": 2}) == 2 and m.extra_value({"model": 1}) is None; n += 1
    # ---- unbundle
    assert m.UNBUNDLE_ORDER == ("bundle", "model", "clip", "vae", "positive", "negative", "latent", "image", "mask", "seed", "steps",
                                "cfg", "denoise", "width", "height", "sampler_name", "scheduler", "text", "text2", "extra", "keys", "missing"); n += 1
    full = {"model": "M", "clip": "C", "vae": "V", "positive": "P", "negative": "N", "latent": "L", "image": "I", "mask": "K",
            "seed": 7, "steps": 20, "cfg": 4.5, "denoise": 0.8, "width": 512, "height": 768, "sampler_name": "euler",
            "scheduler": "simple", "text": "a", "text2": "b", "extra": [1]}
    frozen = copy.deepcopy(full)
    o = m.unbundle(full)
    assert len(o) == 22 and o[0] is full; n += 1
    assert o[1:9] == ("M", "C", "V", "P", "N", "L", "I", "K"); n += 1
    assert o[9:15] == (7, 20, 4.5, 0.8, 512, 768); n += 1
    assert o[15:19] == ("euler", "simple", "a", "b") and o[19] == [1]; n += 1
    assert o[20] == m.keys_text(full) and o[21] == ""; n += 1
    assert full == frozen; n += 1                                                      # unbundle does not change the bundle
    # round trip through make_bundle
    rt = m.make_bundle(None, **{k: v for k, v in full.items() if k != "extra"})
    assert m.unbundle(rt)[1:19] == o[1:19]; n += 1
    # missing keys
    e = m.unbundle({})
    assert len(e) == 22 and e[0] == {}; n += 1
    assert e[1:9] == (None,) * 8; n += 1
    assert e[9:15] == (0, 0, 0.0, 0.0, 0, 0) and isinstance(e[9], int) and isinstance(e[11], float); n += 1
    assert e[15:19] == ("", "", "", "") and e[19] is None and e[20] == ""; n += 1
    assert e[21] == ", ".join(m.OBJECT_KEYS + m.NUMBER_KEYS + m.STRING_KEYS + ("extra",)); n += 1
    part = m.unbundle({"model": "M", "seed": 3, "text": "t"})
    assert part[1] == "M" and part[2] is None and part[9] == 3 and part[17] == "t"; n += 1
    assert "clip" in part[21] and "model" not in part[21].split(", ") and "seed" not in part[21].split(", ") and "text" not in part[21].split(", "); n += 1
    assert "extra" in part[21].split(", "); n += 1
    named = m.unbundle({"my thing": 42})
    assert named[19] == 42 and "extra" not in named[21].split(", "); n += 1              # a named extra counts as present
    assert m.unbundle({"seed": "12", "cfg": 7})[9:12] == (12, 0, 7.0); n += 1             # number types fixed
    assert isinstance(m.unbundle({"cfg": 7})[11], float); n += 1
    assert m.unbundle({"text": 5})[17] == "5"; n += 1
    msg = refuses(m.unbundle, "oops")
    assert msg and "Bundle SY" in msg; n += 1
    assert refuses(m.unbundle, None) is not None; n += 1
    # ---- node classes
    B, U = m.SYBundle, m.SYUnbundle
    assert B.RETURN_TYPES == ("SY_BUNDLE", "STRING") and B.RETURN_NAMES == ("bundle", "keys"); n += 1
    assert len(U.RETURN_TYPES) == 22 and U.RETURN_NAMES == m.UNBUNDLE_ORDER; n += 1
    assert U.RETURN_TYPES[0] == "SY_BUNDLE" and U.RETURN_TYPES[9] == "INT" and U.RETURN_TYPES[11] == "FLOAT" and U.RETURN_TYPES[20] == "STRING"; n += 1
    assert str(U.RETURN_TYPES[19]) == "*" and U.RETURN_TYPES[19] is m.ANY; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYBundle"] == "Bundle SY" and m.NODE_DISPLAY_NAME_MAPPINGS["SYUnbundle"] == "Unbundle SY"; n += 1
    assert m.NODE_CLASS_MAPPINGS["SYBundle"] is B and m.NODE_CLASS_MAPPINGS["SYUnbundle"] is U; n += 1
    assert B.CATEGORY == "SY/Utility" and U.CATEGORY == "SY/Utility"; n += 1
    bs = B.INPUT_TYPES()
    assert bs["required"] == {} and list(bs["optional"])[:9] == ["bundle", "model", "clip", "vae", "positive", "negative", "latent", "image", "mask"]; n += 1
    for k in m.NUMBER_KEYS + m.STRING_KEYS:
        assert bs["optional"][k][1]["forceInput"] is True, k
    n += 1
    assert bs["optional"]["extra_name"][0] == "STRING" and bs["optional"]["extra"][0] == "*"; n += 1
    assert bs["optional"]["cfg"][0] == "FLOAT" and bs["optional"]["seed"][0] == "INT" and bs["optional"]["sampler_name"][0] == "STRING"; n += 1
    for sect in ("required", "optional"):
        for k, dd in bs[sect].items():
            assert 0 < len(dd[1]["tooltip"]) <= 120, k
    for k, dd in U.INPUT_TYPES()["required"].items():
        assert 0 < len(dd[1]["tooltip"]) <= 120, k
    n += 1
    assert "None" in U.DESCRIPTION and "missing" in U.DESCRIPTION and "0" in U.DESCRIPTION; n += 1
    # run through the classes
    out, keys = B().run(model="M", seed=4, text="hello", extra_name="note", extra=[9])
    assert out == {"model": "M", "seed": 4, "text": "hello", "note": [9]} and keys == "model, seed, text, note"; n += 1
    out2, _ = B().run(bundle=out, seed=5, extra=77)
    assert out2["seed"] == 5 and out2["extra"] == 77 and out["seed"] == 4 and "extra" not in out; n += 1
    assert B().run() == ({}, ""); n += 1
    assert "already used" in refuses(B().run, extra_name="clip", extra=1); n += 1
    assert refuses(B().run, bundle="nope") is not None; n += 1
    res = U().run(out2)
    assert len(res) == 22 and res[1] == "M" and res[9] == 5 and res[19] == 77; n += 1
    # a wired-in extra_name with no extra: nothing added
    assert B().run(extra_name="note")[0] == {}; n += 1
    return n
