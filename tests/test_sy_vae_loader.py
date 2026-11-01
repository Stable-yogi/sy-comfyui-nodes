import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_vae_loader as m

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
    raises(m.SYVAELoader().run, "../x.safetensors")
    raises(m.SYVAELoader().run, "/abs/path.safetensors")
    raises(m.SYVAELoader().run, "")
    ok(m.SYVAELoader.RETURN_TYPES[0] == "VAE")
    ok("tooltip" in m.SYVAELoader.INPUT_TYPES()["required"]["vae_name"][1])
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYVAELoader"] == "VAE Loader SY")
    # --- value pass A2: not-a-VAE refusal, family hint, info text
    vae = {"decoder.conv_in.weight": {"dtype": "F32", "shape": [4, 4]}, "encoder.down.0.x": {"dtype": "F32", "shape": [2]}}
    ok(m.check_is_vae("ae.safetensors", vae) is None and m.check_is_vae("x", None) is None)
    ok(m.check_is_vae("x", {"w": {"dtype": "F16", "shape": [1]}}) is None)  # unknown kinds pass: some VAEs have unusual names
    raises(m.check_is_vae, "l.safetensors", {"a.lora_up.weight": {"dtype": "F16", "shape": [1]}})
    raises(m.check_is_vae, "m.safetensors", {"model.diffusion_model.x": {"dtype": "F16", "shape": [1]}})
    raises(m.check_is_vae, "t.safetensors", {"text_model.x": {"dtype": "F16", "shape": [1]}})
    try:
        m.check_is_vae("l.safetensors", {"a.lora_up.weight": {"dtype": "F16", "shape": [1]}})
    except ValueError as e:
        ok(str(e).startswith("'l.safetensors' looks like a LoRA, not a VAE"))
    raises(m.SYVAELoader().run, "ae.gguf")
    ok(m.family_hint("flux/ae.safetensors") == "" and m.family_hint("Flux_vae.safetensors") == "Flux" and m.family_hint("sdxl_vae.safetensors") == "SDXL")
    ok(m.family_hint("wan_2.1_vae.safetensors") == "Wan" and m.family_hint("kl-f8-anime.ckpt") == "")
    t = m.vae_info("sdxl_vae.safetensors", 335 * 1024 ** 2, vae)
    ok(t.split("\n")[0] == "sdxl_vae.safetensors (335 MB)" and "File holds: fp32 (100%)" in t and "The name points to SDXL. Use this VAE only with a SDXL model." in t)
    ok("does not say which model family" in m.vae_info("ae.safetensors") and "unusually big" in m.vae_info("x", 3 * 1024 ** 3))
    ok("unusually big" not in m.vae_info("x", 300 * 1024 ** 2))
    ok(m.SYVAELoader.RETURN_NAMES == ("vae", "info") and len(m.SYVAELoader.RETURN_TYPES) == 2)
    return N[0]
