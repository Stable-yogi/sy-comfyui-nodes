import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_clip_loader as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    L = m.CLIP_TYPES
    ok("stable_diffusion" in L and "wan" in L and "flux2" in L)
    ok(len(set(L)) == len(L))
    ok(m.check_choice("cpu", m.CLIP_DEVICES, "device") == "cpu")
    raises(m.check_choice, "gpu", m.CLIP_DEVICES, "device")
    node = m.SYCLIPLoader()
    raises(node.run, "a.safetensors", "not_a_type", "default")
    raises(node.run, "a.safetensors", "wan", "gpu")
    raises(node.run, "../a.safetensors", "wan", "default")
    spec = m.SYCLIPLoader.INPUT_TYPES()["required"]
    ok(spec["type"][0] == L)
    ok("minimax" in L and "ideogram4" in L)
    ok(m.clip_types() == L)
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYCLIPLoader"] == "CLIP Loader SY")
    # added value: info text, family warnings, name filter
    ok(m.SYCLIPLoader.RETURN_TYPES == ("CLIP", "STRING") and m.SYCLIPLoader.RETURN_NAMES == ("clip", "info"))
    spec = m.SYCLIPLoader.INPUT_TYPES()
    ok(list(spec["required"]) == ["clip_name", "type", "device"] and list(spec["optional"]) == ["name_filter"])
    t = m.build_info("umt5_xxl_fp8_e4m3fn_scaled.safetensors", 6 * 1024 ** 3, "wan", "default")
    ok("6.0 GB" in t and "fp8" in t and "Family: wan, device: default" in t and "Warning" not in t)
    t = m.build_info("umt5_xxl_fp16.safetensors", 10 * 1024 ** 3, "stable_diffusion", "cpu")
    ok("Warning: The file name says umt5" in t and "set the family to wan" in t)
    t = m.build_info("t5xxl_fp16.safetensors", 10 * 1024 ** 3, "wan", "default")
    ok("does not look like a wan text encoder" in t)
    ok(m.text_encoder_warning("t5xxl_fp16.safetensors", "sd3") == "")
    ok(m.text_encoder_warning("clip_l.safetensors", "flux") == "")
    ok(m.text_encoder_warning("my_encoder.safetensors", "wan") == "")  # unknown name: no guess
    ok("Qwen" in m.text_encoder_warning("qwen_2.5_vl_7b_fp8.safetensors", "stable_diffusion"))
    ok(m.text_encoder_warning("qwen_2.5_vl_7b_fp8.safetensors", "qwen_image") == "")
    ok("picked" in m.build_info("a.safetensors", 5, "wan", "default", "name_filter 'a' picked a.safetensors."))
    raises(m.check_size, "a.safetensors", 0)
    ok(m.pick_with_filter(["a.safetensors", "umt5_b.safetensors"], "a.safetensors", "UMT5", "text encoder")[0] == "umt5_b.safetensors")
    raises(m.pick_with_filter, ["a.safetensors"], "a.safetensors", "zzz", "text encoder")
    raises(node.run, "a.safetensors", "wan", "default", "umt5")  # nothing listed here: plain refusal
    return N[0]
