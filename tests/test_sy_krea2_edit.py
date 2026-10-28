import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_krea2_edit as m

# Signature of the source node(s): inputs (name, type, options without tooltip), outputs, function.
EXPECTED = {'Krea2EditModelPatch': {'inputs': {'required': [['model', 'MODEL', {}], ['source_latent', 'LATENT', {}]],
                                    'optional': [['source_latent_b', 'LATENT', {}],
                                                 ['ref_boost',
                                                  'FLOAT',
                                                  {'default': 1.0,
                                                   'min': 0.0,
                                                   'max': 1000.0,
                                                   'step': 0.01,
                                                   'round': 0.001}],
                                                 ['ref_boost_a',
                                                  'FLOAT',
                                                  {'default': 1.0,
                                                   'min': 0.0,
                                                   'max': 1000.0,
                                                   'step': 0.01,
                                                   'round': 0.001}],
                                                 ['fit_mode', ['fit', 'crop (legacy)'], {'default': 'fit'}],
                                                 ['ref_boost_mask', 'MASK', {}],
                                                 ['vae', 'VAE', {}],
                                                 ['source_image', 'IMAGE', {}],
                                                 ['source_image_b', 'IMAGE', {}]]},
                         'returns': ['MODEL'],
                         'names': [],
                         'function': 'patch'},
 'Krea2EditGroundedEncode': {'inputs': {'required': [['clip', 'CLIP', {}],
                                                     ['prompt',
                                                      'STRING',
                                                      {'multiline': True, 'default': ''}]],
                                        'optional': [['image', 'IMAGE', {}],
                                                     ['image_b', 'IMAGE', {}],
                                                     ['grounding_px',
                                                      'INT',
                                                      {'default': 768, 'min': 0, 'max': 4096, 'step': 64}],
                                                     ['system_prompt',
                                                      'STRING',
                                                      {'multiline': True, 'default': ''}]]},
                             'returns': ['CONDITIONING'],
                             'names': [],
                             'function': 'encode'}}


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


def run():
    n = 0
    # 1. signature same as the source nodes
    for name, cls in (("Krea2EditModelPatch", m.SYKrea2EditModelPatch), ("Krea2EditGroundedEncode", m.SYKrea2EditGroundedEncode)):
        assert signature(cls) == EXPECTED[name], name
        n += 1
        names = [k for sec in EXPECTED[name]["inputs"].values() for k, _, _ in sec]
        n += source_text_order("comfyui-krea2edit/__init__.py", names)
    # 2. naming
    assert set(m.NODE_CLASS_MAPPINGS) == {"SYKrea2EditModelPatch", "SYKrea2EditGroundedEncode"}
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYKrea2EditModelPatch"] == "Krea2EditModelPatch SY"
    assert m.SYKrea2EditModelPatch.CATEGORY == "SY/Editors" and m.SYKrea2EditGroundedEncode.CATEGORY == "SY/Editors"
    n += 3
    # 3. centered crop box
    assert m.center_crop_box(100, 100, 50, 100) == (25, 0, 50, 100)
    assert m.center_crop_box(100, 200, 100, 100) == (0, 50, 100, 100)
    assert m.center_crop_box(64, 64, 64, 64) == (0, 0, 64, 64)
    assert m.center_crop_box(10, 10, 40, 20) == (0, 2, 10, 5)
    n += 4
    # 4. pixel fit plan
    assert m.plan_pixel_fit(1000, 1000, 512, 512, "crop") == {"box": (0, 0, 1000, 1000), "size": (512, 512)}
    assert m.plan_pixel_fit(800, 1200, 512, 512, "crop") == {"box": (0, 200, 800, 800), "size": (512, 512)}
    p = m.plan_pixel_fit(1000, 1010, 512, 512, "fit")  # near-matched shape: small centered crop, fills the grid
    assert p["size"] == (512, 512) and p["box"] is not None
    p = m.plan_pixel_fit(800, 1600, 512, 512, "fit")  # real mismatch: no crop, snapped to 16 and capped by the target
    assert p == {"box": None, "size": (256, 512)}, p
    p = m.plan_pixel_fit(10, 10, 512, 512, "fit")
    assert p["size"][0] <= 512 and p["size"][1] <= 512
    n += 5
    # 5. offsets and boosts
    assert m.centered_offset(10, 10, 20, 30) == (5, 10)
    assert m.centered_offset(30, 30, 20, 20) == (0, 0)
    assert m.ref_boost_list(2.0, 1.5, 1) == [2.0]
    assert m.ref_boost_list(2.0, 1.5, 3) == [1.5, 1.5, 2.0]
    assert m.ref_block_offsets(10, [4, 6]) == ([10, 14], 20)
    assert abs(m.boost_bias_value(1.0)) < 1e-12 and abs(m.boost_bias_value(0.0) - (-9.210340371976182)) < 1e-9
    n += 6
    # 6. path modes
    assert m.path_modes("fit", True, True) == (True, "stride1")
    assert m.path_modes("fit", False, True) == (False, "stride1")
    assert m.path_modes("crop (legacy)", True, True) == (False, "anchor")
    n += 3
    # 7. prompt template
    one = m.template_for(1)
    two = m.template_for(2, "  custom system  ")
    assert one.count(m.VISION_BLOCK) == 1 and two.count(m.VISION_BLOCK) == 2
    assert one.startswith("<|im_start|>system\n" + m.DEFAULT_SYSTEM + "<|im_end|>")
    assert "custom system<|im_end|>" in two and one.endswith("{}<|im_end|>\n<|im_start|>assistant\n")
    assert one == ("<|im_start|>system\nDescribe the image by detailing the color, shape, size, "
                   "texture, quantity, text, spatial relationships of the objects and background:"
                   "<|im_end|>\n<|im_start|>user\n<|vision_start|><|image_pad|><|vision_end|>"
                   "{}<|im_end|>\n<|im_start|>assistant\n")
    n += 4
    # 8. the warning lists unknown names sorted
    assert "(aa, zz)" in m.future_inputs_warning({"zz", "aa"}, "x")
    n += 1
    return n
