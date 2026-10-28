import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_krea2t_enhancer as m

# Signature of the source node(s): inputs (name, type, options without tooltip), outputs, function.
EXPECTED = {'Krea2TEnhancer': {'inputs': {'required': [['model', 'MODEL', {}],
                                            ['enabled', 'BOOLEAN', {'default': True}],
                                            ['strength',
                                             'FLOAT',
                                             {'default': 1.0, 'min': 0.0, 'max': 2.0, 'step': 0.05}],
                                            ['debug', 'BOOLEAN', {'default': False}]],
                               'optional': []},
                    'returns': ['MODEL'],
                    'names': ['model'],
                    'function': 'apply'},
 'Krea2TEnhancerAdvanced': {'inputs': {'required': [['model', 'MODEL', {}],
                                                    ['enabled', 'BOOLEAN', {'default': True}],
                                                    ['strength',
                                                     'FLOAT',
                                                     {'default': 1.0, 'min': 0.0, 'max': 2.0, 'step': 0.05}],
                                                    ['text_scale',
                                                     'FLOAT',
                                                     {'default': 1.0, 'min': 0.25, 'max': 4.0, 'step': 0.05}],
                                                    ['debug', 'BOOLEAN', {'default': False}]],
                                       'optional': []},
                            'returns': ['MODEL'],
                            'names': ['model'],
                            'function': 'apply'}}


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


class _Fake:
    pass


def run():
    n = 0
    for name, cls in (("Krea2TEnhancer", m.SYKrea2TEnhancer), ("Krea2TEnhancerAdvanced", m.SYKrea2TEnhancerAdvanced)):
        assert signature(cls) == EXPECTED[name], name
        n += 1
        names = [k for sec in EXPECTED[name]["inputs"].values() for k, _, _ in sec]
        n += source_text_order("ComfyUI-Krea2T-Enhancer/__init__.py" if name == "Krea2TEnhancer" else "ComfyUI-Krea2T-Enhancer/advanced.py", names)
    assert set(m.NODE_CLASS_MAPPINGS) == {"SYKrea2TEnhancer", "SYKrea2TEnhancerAdvanced"}
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYKrea2TEnhancerAdvanced"] == "Krea2TEnhancerAdvanced SY"
    assert m.SYKrea2TEnhancer.CATEGORY == "SY/Utility" and m.SYKrea2TEnhancerAdvanced.CATEGORY == "SY/Utility"
    n += 3
    # constants same as the source
    assert m.KREA2_TAP_LAYERS == (2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35)
    assert (m.KREA2_TAP_DIM, m.KREA2_CHUNK_COUNT, m.KREA2_CHUNK_DIM) == (2560, 24, 1280)
    assert m.ENHANCER_PROFILE_12 == (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.5, 5.0, 1.1, 4.0, 1.0)
    assert m.ENHANCER_CHUNK_PROFILE == m.ENHANCER_PROFILE_12 + m.ENHANCER_PROFILE_12
    assert (m.ENHANCER_GLOBAL_MULTIPLIER, m.TXTFUSION_TOKEN_REL_CAP) == (15.0, 0.75)
    assert m.WRAPPER_KEY == "krea2t_prompt_adherence_enhancer"
    assert m.ADV_CONFIG_KEY == m.ADV_WRAPPER_KEY == "krea2t_prompt_adherence_enhancer_advanced"
    assert m.ADV_ORIGINAL_TXTFUSION_ATTR == "_krea2t_enhancer_advanced_original_forward"
    n += 8
    # bounded float
    assert m._bounded_float(5, 1.0, 0.0, 2.0) == 2.0
    assert m._bounded_float(-1, 1.0, 0.0, 2.0) == 0.0
    assert m._bounded_float("abc", 1.0, 0.0, 2.0) == 1.0
    assert m._bounded_float(float("nan"), 1.0, 0.0, 2.0) == 1.0
    assert m._bounded_float(float("inf"), 1.0, 0.0, 2.0) == 1.0
    assert m._bounded_float(None, 0.5, 0.0, 2.0) == 0.5
    assert m._bounded_float(0.75, 1.0, 0.0, 2.0) == 0.75
    n += 7
    # gains
    g0, g1, g2 = m.chunk_gain_values(0.0), m.chunk_gain_values(1.0), m.chunk_gain_values(2.0)
    assert g0 == [1.0] * 24 and g1 == list(m.ENHANCER_CHUNK_PROFILE) and len(g1) == 24
    assert g2[8] == 1.0 + 2.0 * 4.0
    assert m.global_multiplier_for(0.0) == 1.0 and m.global_multiplier_for(1.0) == 15.0 and m.global_multiplier_for(2.0) == 29.0
    assert m.token_scale_value(0.5) == 1.0 and m.token_scale_value(1.5) == 0.5
    n += 4
    # configs
    assert m.basic_config(1, 9, 0) == {"enabled": True, "strength": 2.0, "debug": False, "max_debug_prints": 8}
    assert m.advanced_config(0, "x", 10, 1) == {"enabled": False, "strength": 1.0, "text_scale": 4.0, "debug": True}
    assert m.advanced_config(1, 1, 0.01, 0)["text_scale"] == 0.25
    n += 3
    # model check by the shape of the object
    ok = _Fake()
    ok.txtfusion = ok.txtmlp = ok.blocks = 1
    ok._unpack_context = 1
    ok.txtlayers, ok.txtdim = 12, 2560
    assert m._is_krea2_dm(ok)
    ok.txtdim = 1024
    assert not m._is_krea2_dm(ok)
    assert not m._is_krea2_dm(_Fake())
    n += 3
    return n
