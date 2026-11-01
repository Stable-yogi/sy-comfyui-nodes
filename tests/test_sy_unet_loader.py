import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_unet_loader as m

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
    ok(m.unet_options("default") == {"dtype": None, "fp8_fast": False})
    ok(m.unet_options("fp8_e4m3fn") == {"dtype": "float8_e4m3fn", "fp8_fast": False})
    ok(m.unet_options("fp8_e4m3fn_fast") == {"dtype": "float8_e4m3fn", "fp8_fast": True})
    ok(m.unet_options("fp8_e5m2") == {"dtype": "float8_e5m2", "fp8_fast": False})
    raises(m.unet_options, "fp16")
    raises(m.SYUnetLoader().run, "a.safetensors", "bf4")
    raises(m.SYUnetLoader().run, "../a.safetensors", "default")
    ok(m.SYUnetLoader.RETURN_TYPES[0] == "MODEL")
    # --- value pass A2: LoRA refusal, GGUF refusal, info text
    import json, struct, tempfile
    lora = {"x.lora_down.weight": {"dtype": "F16", "shape": [2, 2], "data_offsets": [0, 8]}}
    dm = {"double_blocks.0.w": {"dtype": "BF16", "shape": [4, 4], "data_offsets": [0, 32]}}
    ok(m.check_is_diffusion_model("a", dm) is None and m.check_is_diffusion_model("a", None) is None)
    raises(m.check_is_diffusion_model, "lora.safetensors", lora)
    raises(m.SYUnetLoader().run, "model.gguf", "default")
    try:
        m.SYUnetLoader().run("model.gguf", "default")
    except ValueError as e:
        ok("Unet Loader GGUF SY" in str(e))
    t = m.unet_info("flux.safetensors", "fp8_e4m3fn", 12 * 1024 ** 3, dm)
    ok(t.split("\n")[0] == "flux.safetensors (12.00 GB)" and "File holds: diffusion model, bf16 (100%)" in t and "about half the memory" in t)
    ok(m.unet_info("a.gguf", "default").split("\n") == ["a.gguf", "File holds: GGUF (quantized)", "Loaded as: the type stored in the file"])
    ok("already fp8" in m.unet_info("a", "fp8_e5m2", None, {"w": {"dtype": "F8_E4M3", "shape": [2]}}))
    ok("looks like a VAE" in m.unet_info("a", "default", None, {"decoder.conv_in.weight": {"dtype": "F16", "shape": [1]}}))
    ok("RTX 40" in m.unet_info("a", "fp8_e4m3fn_fast", None, None, (8, 6)) and "RTX 40" not in m.unet_info("a", "fp8_e4m3fn_fast", None, None, (8, 9)))
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.safetensors")
        raw = json.dumps(dm).encode()
        with open(p, "wb") as f:
            f.write(struct.pack("<Q", len(raw)) + raw + b"\0" * 32)
        ok(m.peek_header(p) == dm)
        ok(m.peek_header(os.path.join(d, "x.gguf")) is None)
        bad = os.path.join(d, "bad.safetensors")
        open(bad, "wb").write(b"abc")
        ok(m.peek_header(bad) is None)
    ok(m.SYUnetLoader.RETURN_NAMES == ("model", "info"))
    return N[0]
