import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sampler_sweep as m

SAMPLERS = ["euler", "euler_ancestral", "er_sde", "dpmpp_2m"]
SCHEDULERS = ["simple", "normal", "beta", "karras"]


def refuses(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    p = m.parse_pairs("er_sde + simple\n\n# skip me\neuler, beta\ndpmpp_2m karras", SAMPLERS, SCHEDULERS)
    assert p == [("er_sde", "simple"), ("euler", "beta"), ("dpmpp_2m", "karras")]; n += 1
    assert m.parse_pairs("  euler+normal  ", SAMPLERS, SCHEDULERS) == [("euler", "normal")]; n += 1
    assert "at least one" in refuses(m.parse_pairs, "\n# only a note\n", SAMPLERS, SCHEDULERS); n += 1
    assert "line 2" in refuses(m.parse_pairs, "euler + simple\nfoo + simple", SAMPLERS, SCHEDULERS); n += 1
    assert "not a scheduler" in refuses(m.parse_pairs, "euler + bogus", SAMPLERS, SCHEDULERS); n += 1
    assert "sampler + scheduler" in refuses(m.parse_pairs, "euler", SAMPLERS, SCHEDULERS); n += 1
    assert "at most 24" in refuses(m.parse_pairs, "\n".join(["euler + simple"] * 25), SAMPLERS, SCHEDULERS); n += 1
    assert m.pair_caption("er_sde", "beta", 11.234) == "er_sde + beta  11.2 s"; n += 1
    t = m.time_table([("a", "x"), ("b", "y")], [9.0, 8.5], 25)
    lines = t.split("\n")
    assert lines[0].startswith("2 pairs, 25 steps") and lines[1].startswith("b + y") and "0.34 s per step" in lines[1]; n += 1
    assert "also loaded the model" not in t; n += 1
    t2 = m.time_table([("er_sde", "simple"), ("euler", "simple"), ("uni_pc", "beta")], [39.1, 10.1, 10.3], 25)
    assert t2.split("\n")[-1].startswith("The first pair (er_sde + simple) also loaded the model"); n += 1
    assert len(m.DEFAULT_PAIRS.splitlines()) == 5; n += 1
    it = m.SYSamplerSweep.INPUT_TYPES()
    assert it["required"]["pairs"][1]["multiline"] and "negative" in it["optional"]; n += 1
    assert m.SYSamplerSweep.RETURN_TYPES == ("LATENT", "STRING", "STRING"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSamplerSweep"] == "Sampler Sweep SY"; n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
