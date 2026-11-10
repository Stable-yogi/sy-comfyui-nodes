import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_checkpoint_contact_sheet as m


def _refused(fn, *args, part=""):
    try:
        fn(*args)
    except ValueError as e:
        assert part in str(e), str(e)
        return
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.clean_lines(" a \n\n# note\nb\n") == ["a", "b"]; n += 1
    assert m.clean_lines(None) == []; n += 1
    avail = ["SDXL/juggernautXL_v9.safetensors", "SDXL/realvisXL_v5.safetensors", "SD15/realvis_v6.safetensors", "dream.ckpt"]
    picked, probs = m.match_checkpoints(["juggernaut", "dream.ckpt", "realvisxl_v5.safetensors"], avail)
    assert picked == [avail[0], avail[3], avail[1]] and probs == [], (picked, probs); n += 1
    picked, probs = m.match_checkpoints(["realvis", "nothing"], avail)
    assert picked == [] and len(probs) == 2 and "matches 2" in probs[0] and "no checkpoint" in probs[1]; n += 1
    picked, probs = m.match_checkpoints(["ultra"], ["a/Ultra XL.safetensors", "b/Ultra XL.safetensors"])
    assert picked == ["a/Ultra XL.safetensors"] and probs[0].startswith("note: 2 copies"), probs; n += 1  # copies of one file
    picked, _ = m.match_checkpoints(["juggernaut", "JUGGERNAUT"], avail)
    assert picked == [avail[0]]; n += 1  # the same file twice is kept once
    assert m.model_label("SDXL/juggernautXL_v9.safetensors") == "juggernautXL_v9"; n += 1
    assert m.model_label("plain") == "plain"; n += 1
    m.check_plan(["a"], ["p"], 1024, 1024); n += 1
    _refused(m.check_plan, [], ["p"], 64, 64, part="no checkpoint"); n += 1
    _refused(m.check_plan, ["a"], [], 64, 64, part="no prompt"); n += 1
    _refused(m.check_plan, ["a"] * 13, ["p"], 64, 64, part="limit is 12"); n += 1
    _refused(m.check_plan, ["a"], ["p"], 1000, 1020, part="multiples of 8"); n += 1
    t = m.sheet_text(["x/a.safetensors"], ["cat"], [3.25], ["skipped: no checkpoint matches 'b'"])
    assert "1 checkpoint x 1 prompt" in t and "a: 3.2 s" in t and "prompt 1: cat" in t and "Skipped: no checkpoint" in t, t; n += 1
    try:
        import folder_paths  # noqa: F401
    except ImportError:
        _refused(m.SYCheckpointContactSheet().run, "a", "p", "", 512, 512, 1, 1.0, "euler", "normal", 1, 20, part="only runs inside ComfyUI")
        n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
