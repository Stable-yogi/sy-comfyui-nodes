import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_setup_doctor as m

GB = 1024 ** 3


def run():
    n = 0
    base = os.path.join("X:", os.sep, "ComfyUI", "custom_nodes")
    packs = [os.path.join(base, x) for x in ("ComfyUI-Manager", "sy-comfyui-nodes", "BrokenPack", "__pycache__", "old.disabled", ".git")]
    assert m.manager_found(packs); n += 1
    assert not m.manager_found(packs[1:]); n += 1
    failed = m.failed_packs(packs, [packs[0], packs[1]])
    assert failed == ["BrokenPack"], failed; n += 1
    assert m.failed_packs(packs[:2], packs[:2]) == []; n += 1

    assert m.flag_notes({}) == []; n += 1
    notes = m.flag_notes({"lowvram": True, "cpu": True})
    assert len(notes) == 2 and "--cpu" in notes[0] and "--lowvram" in notes[1]; n += 1
    assert len(m.flag_notes({"lowvram": True, "novram": True})) == 1; n += 1  # novram wins

    c = m.classify_misplaced
    assert c("checkpoints", "my_style_lora.safetensors", 0.2 * GB)[0] == "loras"; n += 1
    assert c("checkpoints", "sdxl_vae.safetensors", 0.3 * GB)[0] == "vae"; n += 1
    assert c("checkpoints", "model_with_vae.safetensors", 0.3 * GB) is None; n += 1
    assert c("checkpoints", "juggernaut_xl.safetensors", 6.5 * GB) is None; n += 1
    assert c("diffusion_models", "umt5_xxl_fp8.safetensors", 6 * GB)[0] == "text_encoders"; n += 1
    assert c("checkpoints", "4x-UltraSharp.pth", 0.06 * GB)[0] == "upscale_models"; n += 1
    assert c("loras", "big.safetensors", 6.4 * GB)[0].startswith("checkpoints"); n += 1
    assert c("loras", "ltx-22b-distilled-lora-384.safetensors", 7.1 * GB) is None; n += 1  # big video LoRAs are real
    assert c("vae", "t5xxl_fp16.safetensors", 9.1 * GB)[0] == "text_encoders"; n += 1
    assert c("vae", "minimax_h3_video_vae_fp16.safetensors", 4.9 * GB) is None; n += 1  # video VAEs are big
    assert c("loras", "small.safetensors", 0.2 * GB) is None; n += 1
    assert c("vae", "wan_vae.safetensors", 0.5 * GB) is None; n += 1
    assert c("vae", "huge_model.safetensors", 5 * GB) is not None; n += 1

    report, fixes, count = m.build_report("0.43.0", [], True, [], [], [], "1.25.0", "")
    assert count == 0 and fixes == "" and "Nothing to fix." in report and "0.43.0" in report; n += 1
    report, fixes, count = m.build_report("", ["BrokenPack"], False, ["note"], ["loras"],
                                          [("checkpoints", "a_lora.safetensors", "loras", "the name says LoRA")])
    assert count == 2, count; n += 1
    assert fixes.startswith("1. Node packs") and "2. Move a_lora.safetensors" in fixes; n += 1
    assert "TIP  ComfyUI Manager" in report and "models/loras is empty" in report and "(version unknown)" in report; n += 1

    node = m.SYSetupDoctor()
    try:
        import folder_paths  # noqa: F401  (inside ComfyUI the run is real; outside it must refuse)
    except ImportError:
        try:
            node.run()
        except ValueError as e:
            assert "only runs inside ComfyUI" in str(e)
            n += 1
        else:
            raise SystemExit("expected ValueError outside ComfyUI")
    return n


if __name__ == "__main__":
    print("checks:", run())
