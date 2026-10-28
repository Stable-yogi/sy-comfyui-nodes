import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_krea2_conditioning as m

# Signature of the source node(s): inputs (name, type, options without tooltip), outputs, function.
EXPECTED = {'Krea2ConditioningRebalance': {'inputs': {'required': [['conditioning', 'CONDITIONING', {}],
                                                        ['preset',
                                                         ['balanced',
                                                          'detail',
                                                          'subtle',
                                                          'uniform',
                                                          'custom'],
                                                         {'default': 'balanced'}],
                                                        ['per_layer_weights',
                                                         'STRING',
                                                         {'default': '1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, '
                                                                     '2.5, 5.0, 1.1, 4.0, 1.0',
                                                          'multiline': False}],
                                                        ['multiplier',
                                                         'FLOAT',
                                                         {'default': 1.0,
                                                          'min': -1000.0,
                                                          'max': 1000.0,
                                                          'step': 0.01}],
                                                        ['renormalize', 'BOOLEAN', {'default': True}]],
                                           'optional': []},
                                'returns': ['CONDITIONING'],
                                'names': ['conditioning'],
                                'function': 'rebalance'}}


def signature(cls):
    out = {}
    for sec in ("required", "optional"):
        items = []
        for k, v in (cls.INPUT_TYPES().get(sec) or {}).items():
            t = v[0]
            o = dict(v[1]) if len(v) > 1 else {}
            o.pop("tooltip", None)
            items.append([k, list(t) if isinstance(t, (list, tuple)) else t, o])
        out[sec] = items
    return {"inputs": out, "returns": list(cls.RETURN_TYPES),
            "names": list(getattr(cls, "RETURN_NAMES", []) or []), "function": cls.FUNCTION}


def source_text_order(src_file, names):
    """Optional: when SY_KREA2_SRC points at the folder holding the source packs, the input names must appear in order in the source text."""
    base = os.environ.get("SY_KREA2_SRC")
    if not base:
        return 0
    text = open(os.path.join(base, src_file), encoding="utf-8").read()
    pos = text.index("def INPUT_TYPES")
    for n in names:
        i = text.find('"%s"' % n, pos)
        assert i >= 0, "input %s not found in source text" % n
        pos = i + 1
    return 1


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert signature(m.SYKrea2ConditioningRebalance) == EXPECTED["Krea2ConditioningRebalance"]
    n += 1
    names = [k for sec in EXPECTED["Krea2ConditioningRebalance"]["inputs"].values() for k, _, _ in sec]
    n += source_text_order("comfyui-krea2-conditioning/nodes.py", names)
    assert set(m.NODE_CLASS_MAPPINGS) == {"SYKrea2ConditioningRebalance"}
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYKrea2ConditioningRebalance"] == "Krea2ConditioningRebalance SY"
    assert m.SYKrea2ConditioningRebalance.CATEGORY == "SY/Utility"
    n += 3
    # presets: 12 values each, same numbers as the source
    assert all(len(v) == 12 for v in m.PRESET_WEIGHTS.values())
    assert m.PRESET_WEIGHTS["balanced"] == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.5, 5.0, 1.1, 4.0, 1.0]
    assert m.PRESET_WEIGHTS["detail"] == [0.8, 0.8, 0.9, 0.9, 1.0, 1.0, 1.2, 3.0, 6.0, 1.5, 5.0, 1.2]
    assert m.PRESET_WEIGHTS["subtle"] == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5, 2.0, 1.0, 1.5, 1.0]
    assert m.PRESET_WEIGHTS["uniform"] == [1.0] * 12
    assert m.PRESET_NAMES == ["balanced", "detail", "subtle", "uniform", "custom"]
    n += 6
    assert m.SYKrea2ConditioningRebalance.INPUT_TYPES()["required"]["per_layer_weights"][1]["default"] == \
        "1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.5, 5.0, 1.1, 4.0, 1.0"
    n += 1
    # parse_weights
    assert m.parse_weights("1, 2;3") == [1.0, 2.0, 3.0]
    assert m.parse_weights(" 0.5 ,, 2 ") == [0.5, 2.0]
    assert raises(m.parse_weights, None)
    assert raises(m.parse_weights, "1")
    assert raises(m.parse_weights, "1, x")
    assert raises(m.parse_weights, "")
    n += 6
    # resolve_weights
    assert m.resolve_weights("subtle", "ignored") == m.PRESET_WEIGHTS["subtle"]
    assert m.resolve_weights("nonsense", "") == m.PRESET_WEIGHTS["balanced"]
    assert m.resolve_weights("custom", "2, 3") == [2.0, 3.0]
    assert raises(m.resolve_weights, "custom", "5")
    n += 4
    # the maths, only when torch is installed (the selftest Python has none)
    try:
        import torch
    except ImportError:
        return n
    cond = [[torch.tensor([[[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]]]), {"k": 1}]]  # 1 token, 3 layers of 2 numbers
    out = m.scale_conditioning(cond, 2.0, [1.0, 2.0, 3.0], False)
    assert out[0][0].tolist() == [[[2.0, 4.0, 12.0, 16.0, 30.0, 36.0]]]
    assert out[0][1] == {"k": 1}
    out = m.scale_conditioning(cond, 1.0, [1.0, 2.0, 3.0], True)
    assert abs(float(out[0][0].pow(2).mean().sqrt()) - float(cond[0][0].pow(2).mean().sqrt())) < 1e-5
    out = m.scale_conditioning(cond, 3.0, [1.0, 2.0, 3.0, 4.0], True)  # 6 not divisible by 4: plain multiplier
    assert out[0][0].tolist() == [[[3.0, 6.0, 9.0, 12.0, 15.0, 18.0]]]
    n += 4
    return n
