import json
import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_safetensors_header_info as m


def _write(path, header, extra=b"", raw_header=None):
    raw = raw_header if raw_header is not None else json.dumps(header).encode("utf-8")
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(raw)))
        f.write(raw)
        f.write(extra)


def run():
    n = 0
    with tempfile.TemporaryDirectory() as d:
        header = {
            "__metadata__": {"format": "pt", "ss_note": "x"},
            "a.weight": {"dtype": "F16", "shape": [4, 8], "data_offsets": [0, 64]},
            "b.weight": {"dtype": "F16", "shape": [10], "data_offsets": [64, 84]},
            "c.bias": {"dtype": "F32", "shape": [], "data_offsets": [84, 88]},
        }
        p = os.path.join(d, "t.safetensors")
        _write(p, header, extra=b"\0" * 88)
        s = m.summarize_header(m.read_header(p))
        assert s["tensor_count"] == 3
        assert s["dtype_counts"] == {"F16": 2, "F32": 1}
        assert s["total_params"] == 4 * 8 + 10 + 1
        assert s["metadata_keys"] == ["format", "ss_note"]
        n += 4
        rep = m.format_report(s, os.path.getsize(p))
        assert "Tensors: 3" in rep and "F16 x2" in rep and "format, ss_note" in rep
        n += 1
        p2 = os.path.join(d, "n.safetensors")
        _write(p2, {"x": {"dtype": "BF16", "shape": [2, 2], "data_offsets": [0, 8]}}, extra=b"\0" * 8)
        s2 = m.summarize_header(m.read_header(p2))
        assert s2["metadata_keys"] == [] and "none" in m.format_report(s2)
        n += 2
        # a header over the limit is refused without being read
        p3 = os.path.join(d, "big.safetensors")
        with open(p3, "wb") as f:
            f.write(struct.pack("<Q", m.MAX_HEADER_BYTES + 1))
            f.write(b"{}")
        p4 = os.path.join(d, "short.safetensors")
        with open(p4, "wb") as f:
            f.write(b"abc")
        p5 = os.path.join(d, "nojson.safetensors")
        _write(p5, None, raw_header=b"not json at all")
        p6 = os.path.join(d, "toolong.safetensors")
        with open(p6, "wb") as f:
            f.write(struct.pack("<Q", 5000))
            f.write(b"{}")
        p7 = os.path.join(d, "list.safetensors")
        _write(p7, None, raw_header=b"[1,2]")
        for bad in (p3, p4, p5, p6, p7):
            try:
                m.read_header(bad)
                raise SystemExit("bad file must raise: " + bad)
            except ValueError:
                n += 1
    try:
        m.summarize_header({"x": {"dtype": "F16"}})
        raise SystemExit("tensor without shape must raise")
    except ValueError:
        n += 1
    assert m.split_choice("loras/sub/a.safetensors") == ("loras", "sub/a.safetensors")
    n += 1
    for bad in ("nofolder", "other/a.safetensors", 5):
        try:
            m.split_choice(bad)
            raise SystemExit("bad choice must raise")
        except ValueError:
            n += 1
    try:
        m.SYSafetensorsHeaderInfo().run("None")
        raise SystemExit("None must raise")
    except ValueError:
        n += 1
    # --- value pass A2: kind guess, main data type, metadata, one-line summary
    import _sy_a2_files as hf
    lora = {"__metadata__": {"ss_network_dim": "16", "note": "a  b\nc"}, "lora_unet_x.lora_down.weight": {"dtype": "F16", "shape": [4, 4], "data_offsets": [0, 32]}}
    assert hf.kind_guess(lora) == "LoRA"; n += 1
    assert hf.kind_guess({"first_stage_model.encoder.x": {}, "model.diffusion_model.a": {}}).startswith("full checkpoint"); n += 1
    assert hf.kind_guess({"model.diffusion_model.a": {}}) == "diffusion model"; n += 1
    assert hf.kind_guess({"double_blocks.0.x": {}}) == "diffusion model"; n += 1
    assert hf.kind_guess({"decoder.conv_in.weight": {}, "encoder.down.0": {}}) == "VAE"; n += 1
    assert hf.kind_guess({"text_model.encoder.x": {}}) == "text encoder"; n += 1
    assert hf.kind_guess({"zzz": {}}) == "unknown" and hf.kind_guess({}) == "empty file"; n += 1
    assert hf.main_dtype_text({"a": {"dtype": "BF16", "shape": [2, 2]}}) == "bf16 (100%)"; n += 1
    mixed = {"a": {"dtype": "BF16", "shape": [10]}, "b": {"dtype": "F8_E4M3", "shape": [30]}}
    assert hf.main_dtype_text(mixed) == "mixed: fp8 e4m3 75%, bf16 25%"; n += 1
    assert hf.main_dtype_text({}) == "no tensors"; n += 1
    ml = hf.metadata_lines(lora)
    assert ml.split("\n") == ["note: a b c", "ss_network_dim: 16"]; n += 1
    assert hf.metadata_lines({"x": {"dtype": "F16", "shape": [1]}}) == ""; n += 1
    long_meta = {"__metadata__": {"k%02d" % i: "v" * 300 for i in range(33)}}
    out = hf.metadata_lines(long_meta).split("\n")
    assert len(out) == 31 and out[-1] == "... and 3 more keys" and out[0].endswith("..."); n += 1
    one = m.one_line_summary(lora, 2 * 1024 ** 3)
    assert one.startswith("LoRA, fp16 (100%), 0.00 billion parameters") and one.endswith("2.00 GB"); n += 1
    assert m.KINDS[-2:] == ("diffusion_models", "text_encoders") and m.split_choice("text_encoders/t5.safetensors")[0] == "text_encoders"; n += 1
    assert m.SYSafetensorsHeaderInfo.RETURN_NAMES == ("report", "summary", "metadata") and len(m.SYSafetensorsHeaderInfo.RETURN_TYPES) == 3; n += 1
    assert m.read_header is hf.read_header and m.MAX_HEADER_BYTES == 20 * 1024 * 1024; n += 1
    return n
