import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_inpaint_crop_stitch as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    # box from flags
    assert m.box_from_flags([0, 1, 1, 0], [0, 0, 1, 0]) == (2, 1, 3, 3); n += 1
    assert m.box_from_flags([0, 0], [0, 0]) is None; n += 1
    # small mark in a big picture gets min_side room
    box = m.context_box((300, 1100, 400, 1200), 960, 1440, 1.5, 256)
    assert (box[2] - box[0], box[3] - box[1]) == (256, 256); n += 1
    assert box[0] <= 300 and box[2] >= 400 and box[1] <= 1100 and box[3] >= 1200; n += 1
    # edge box stays inside the picture
    b = m.context_box((920, 0, 960, 40), 960, 1440, 2.0, 256)
    assert b[0] >= 0 and b[1] >= 0 and b[2] <= 960 and b[3] <= 1440; n += 1
    # target sizes
    assert m.target_size(960, 1440, 1024) == (688, 1024); n += 1
    assert m.target_size(256, 256, 1024) == (1024, 1024); n += 1
    tw, th = m.target_size(100, 7, 256)
    assert tw % 16 == 0 and th % 16 == 0 and th >= 64; n += 1
    # blend maths
    assert m.blend(0.2, 0.8, 0.0) == 0.2 and m.blend(0.2, 0.8, 1.0) == 0.8; n += 1
    assert abs(m.blend(0.0, 1.0, 0.25) - 0.25) < 1e-9; n += 1
    # bad input
    assert raises(m.context_box, (0, 0, 1, 1), 100, 100, 0.5, 64); n += 1
    assert raises(m.target_size, 0, 10, 1024); n += 1
    assert raises(m.context_box, (0, 0, 1, 1), 0, 100, 1.5, 64); n += 1
    # node declarations identical to the old nodes
    assert m.STITCH_TYPE == "SY_STITCH"; n += 1
    assert list(m.SYInpaintCrop.INPUT_TYPES()["required"]) == ["image", "mask", "context", "size", "min_box"]; n += 1
    assert m.SYInpaintCrop.RETURN_NAMES == ("stitch", "cropped_image", "cropped_mask"); n += 1
    assert m.SYInpaintCrop.RETURN_TYPES == ("SY_STITCH", "IMAGE", "MASK"); n += 1
    assert m.SYInpaintStitch.RETURN_NAMES == ("image",); n += 1
    assert list(m.SYInpaintStitch.INPUT_TYPES()["required"]) == ["stitch", "inpainted"]; n += 1
    assert set(m.NODE_CLASS_MAPPINGS) == {"SYInpaintCrop", "SYInpaintStitch"}; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYInpaintCrop"] == "InpaintCrop SY"; n += 1
    # stitch refuses a wrong stitch value
    assert raises(m.SYInpaintStitch().stitch, {}, None); n += 1
    return n
