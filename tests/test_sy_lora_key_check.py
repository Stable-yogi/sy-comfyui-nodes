import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lora_key_check as m


def run():
    n = 0
    assert m.part_name("diffusion_model.blocks.0.attn.q.lora_up.weight") == "diffusion_model.blocks.0.attn.q"; n += 1
    assert m.part_name("lora_unet_blocks_0_attn_q.lora_down.weight") == "lora_unet_blocks_0_attn_q"; n += 1
    assert m.part_name("x.lora_A.weight") == "x"; n += 1
    assert m.part_name("x.alpha") == "x"; n += 1
    assert m.part_name("plainkey") == "plainkey"; n += 1
    assert m.group_parts(["a.lora_up.weight", "a.lora_down.weight", "a.alpha", "b.alpha"]) == ["a", "b"]; n += 1
    assert m.top_prefixes(["te.a", "te.b", "dm.c"]) == [("te", 2), ("dm", 1)]; n += 1
    assert m.top_prefixes(["lora_te_x", "lora_te_y"], depth=2) == [("lora_te_x", 1), ("lora_te_y", 1)]; n += 1
    assert m.top_prefixes(["lora_te1_a_b", "lora_te1_c", "lora_unet_d"]) == [("lora_te1", 2), ("lora_unet", 1)]; n += 1
    assert m.verdict(0, 0) == "EMPTY: the LoRA file holds no keys."; n += 1
    assert m.verdict(10, 0) == "OK: all 10 LoRA keys fit this model."; n += 1
    assert m.verdict(10, 10).startswith("NO MATCH: none of the 10"); n += 1
    assert m.verdict(10, 4) == "PARTLY: 6 of 10 LoRA keys fit this model (60%); 4 do not."; n += 1
    assert m.verdict(10, 0, 2).startswith("PARTLY: 10 of 10") and "2 matched parts" in m.verdict(10, 0, 2); n += 1
    r = m.build_report("x.safetensors", 6, ["te.a.lora_up.weight", "te.a.lora_down.weight", "te.b.alpha"])
    assert "LoRA: x.safetensors" in r and "PARTLY: 3 of 6" in r and "Parts that do not fit: 2" in r and "te (2)" in r; n += 1
    assert "OK: all 4" in m.build_report("y", 4, []) and "Tip" not in m.build_report("y", 4, []); n += 1
    many = ["k%03d.alpha" % i for i in range(205)]
    t = m.list_text(many, limit=200)
    assert t.splitlines()[-1] == "... and 5 more" and len(t.splitlines()) == 201; n += 1
    assert m.list_text([]) == ""; n += 1
    c = m._MissCatcher()
    import logging
    c.emit(logging.LogRecord("r", logging.WARNING, "", 0, "lora key not loaded: abc.alpha", None, None))
    c.emit(logging.LogRecord("r", logging.WARNING, "", 0, "something else", None, None))
    assert c.keys == ["abc.alpha"]; n += 1
    out = m.SYLoraKeyCheck().run("MODEL", "None")
    assert out["result"] == ("MODEL", "No LoRA picked.", "", 0.0); n += 1
    assert m.SYLoraKeyCheck.RETURN_NAMES == ("model", "report", "unmatched_parts", "match_percent"); n += 1
    return n


if __name__ == "__main__":
    print(run())
