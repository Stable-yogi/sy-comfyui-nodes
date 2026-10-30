import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_face_detect as m


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


class _Arr:
    """Tiny stand-in for a picture array: only .shape is read."""
    shape = (100, 200, 3)


class _FakeDet:
    def __init__(self, faces):
        self.faces = faces
        self.size = None

    def setInputSize(self, size):
        self.size = size

    def detect(self, img):
        return 1, self.faces


class _FakeFD:
    def __init__(self, faces=None, fail=False):
        self.faces = faces
        self.fail = fail

    def create(self, path, cfg, size, score, nms_t, top_k):
        if self.fail:
            raise RuntimeError("bad model\nnot an onnx")
        return _FakeDet(self.faces)


class _FakeCV2:
    INTER_AREA = 3

    def __init__(self, faces=None, fail=False):
        self.FaceDetectorYN = _FakeFD(faces, fail)


def run():
    n = 0

    # nms
    boxes = [(0, 0, 10, 10), (1, 1, 11, 11), (50, 50, 60, 60)]
    assert m.nms(boxes, [0.5, 0.9, 0.7], 0.3) == [1, 2]; n += 1
    assert m.nms([], [], 0.3) == []; n += 1
    assert m.nms([(0, 0, 10, 10)], [0.1], 0.3) == [0]; n += 1
    assert m.nms([(0, 0, 10, 10), (0, 0, 10, 10)], [0.5, 0.5], 0.3) == [0]; n += 1  # two equal faces: one stays
    assert _raises(m.nms, boxes, [1.0], 0.3); n += 1
    assert _raises(m.nms, boxes, [1, 1, 1], 1.5); n += 1

    # drop_small
    assert m.drop_small([(0, 0, 40, 40), (0, 0, 20, 90), (0, 0, 32, 32)], 32) == [(0, 0, 40, 40), (0, 0, 32, 32)]; n += 1
    assert m.drop_small([], 32) == []; n += 1
    assert m.small_keep([(0, 0, 10, 10)], 10) == [0]; n += 1
    assert _raises(m.drop_small, [(0, 0, 5, 5)], 0); n += 1

    # pick_faces
    a, b = (0, 0, 20, 20), (90, 40, 110, 60)  # b is centred in a 200x100 picture
    assert m.pick_faces([a, b], [0.9, 0.5], 200, 100, "centre 1") == [b]; n += 1
    assert m.pick_faces([a, (0, 0, 50, 50)], [0.5, 0.5], 200, 100, "largest 1") == [(0, 0, 50, 50)]; n += 1
    assert m.pick_faces([a, b], [0.9, 0.5], 200, 100, "all") == [a, b]; n += 1
    assert m.pick_faces([], [], 200, 100, "all") == []; n += 1
    assert m.pick_faces([], [], 200, 100, "centre 1") == []; n += 1
    assert m.pick_faces([a], [0.5], 200, 100, "largest 1") == [a]; n += 1
    # tie on distance: higher score wins, then lower x
    l, r = (40, 40, 60, 60), (140, 40, 160, 60)
    assert m.pick_faces([l, r], [0.4, 0.8], 200, 100, "centre 1") == [r]; n += 1
    assert m.pick_faces([r, l], [0.5, 0.5], 200, 100, "centre 1") == [l]; n += 1
    assert m.pick_faces([r, l], [0.5, 0.5], 200, 100, "largest 1") == [l]; n += 1
    assert _raises(m.pick_faces, [a], [0.5], 200, 100, "smallest"); n += 1
    assert _raises(m.pick_faces, [a], [], 200, 100, "all"); n += 1

    # grow_box
    assert m.grow_box((50, 50, 100, 100), 10, 400, 400) == (40, 40, 110, 110); n += 1
    assert m.grow_box((0, 0, 20, 20), 10, 400, 400) == (0, 0, 30, 30); n += 1  # face at the border
    assert m.grow_box((380, 390, 400, 400), 10, 400, 400) == (370, 380, 400, 400); n += 1
    assert m.grow_box((50, 50, 100, 100), 9999, 300, 200) == (0, 0, 300, 200); n += 1  # bigger than the picture
    assert m.grow_box((10.4, 10.4, 20.2, 20.2), 0, 100, 100) == (10, 10, 21, 21); n += 1
    assert _raises(m.grow_box, (0, 0, 5, 5), -1, 10, 10); n += 1
    assert _raises(m.grow_box, (0, 0, 5), 1, 10, 10); n += 1
    assert _raises(m.grow_box, (0, 0, 5, 5), 1, 0, 10); n += 1

    # ellipse_row_span: agrees with the pixel-centre test x^2/a^2 + y^2/b^2 <= 1
    box = (10, 20, 50, 60)  # 40 x 40, circle radius 20, centre (30, 40)
    assert m.ellipse_row_span(box, 19) is None; n += 1
    assert m.ellipse_row_span(box, 60) is None; n += 1
    for y in (20, 25, 39, 40, 55, 59):
        got = m.ellipse_row_span(box, y)
        inside = [x for x in range(0, 80) if ((x + 0.5 - 30) / 20.0) ** 2 + ((y + 0.5 - 40) / 20.0) ** 2 <= 1.0 + 1e-12]
        want = (inside[0], inside[-1] + 1) if inside else None
        assert got == want, (y, got, want); n += 1
    mid = m.ellipse_row_span(box, 39)
    assert mid[0] >= 10 and mid[1] <= 50; n += 1
    assert (mid[1] - mid[0]) > (m.ellipse_row_span(box, 22)[1] - m.ellipse_row_span(box, 22)[0]); n += 1
    assert m.ellipse_row_span((5, 5, 5, 10), 6) is None; n += 1  # zero width
    # ellipse area is smaller than the box area (rows summed)
    area = sum((s[1] - s[0]) for s in (m.ellipse_row_span(box, y) for y in range(20, 60)) if s)
    assert 0 < area < 40 * 40; n += 1

    # build_mask_rows
    rows_box = m.build_mask_rows([(2, 1, 6, 4)], "box", 10, 10)
    assert rows_box == [(1, 2, 6), (2, 2, 6), (3, 2, 6)]; n += 1
    rows_el = m.build_mask_rows([(0, 0, 40, 40)], "ellipse", 100, 100)
    assert sum(e - s for _, s, e in rows_el) < 40 * 40; n += 1
    assert m.build_mask_rows([], "box", 10, 10) == []; n += 1
    assert _raises(m.build_mask_rows, [(0, 0, 2, 2)], "star", 10, 10); n += 1

    # format_boxes
    assert m.format_boxes([[(1, 2, 3, 4), (5, 6, 7, 8)], [], [(0, 0, 9, 9)]]) == "1,2,3,4;5,6,7,8\n\n0,0,9,9"; n += 1
    assert m.format_boxes([]) == ""; n += 1
    assert m.format_boxes([[]]) == ""; n += 1
    assert m.format_boxes([[(0.4, 0.6, 9.5, 9.4)]]) == "0,1,10,9"; n += 1
    assert _raises(m.format_boxes, [[(1, 2, 3)]]); n += 1

    # haar_min_neighbors
    assert m.haar_min_neighbors(0.05) == 2; n += 1
    assert m.haar_min_neighbors(0.5) == 6; n += 1
    assert m.haar_min_neighbors(0.99) == 10; n += 1
    assert _raises(m.haar_min_neighbors, 0.0); n += 1
    assert _raises(m.haar_min_neighbors, 1.0); n += 1

    # scale_for and rows_to_boxes
    assert m.scale_for(1000, 800) == 1.0; n += 1
    assert m.scale_for(2560, 1000) == 0.5; n += 1
    bx, sc = m.rows_to_boxes([[10, 10, 20, 20, 0.9], [-5, -5, 3, 3, 0.8], [0, 0, 0, 5, 0.5]], 0.5, 100, 100)
    assert bx == [(20.0, 20.0, 60.0, 60.0)] and sc == [0.9]; n += 1  # off-picture and empty boxes are dropped
    bx, _ = m.rows_to_boxes([[90, 90, 50, 50, 1.0]], 1.0, 100, 100)
    assert bx == [(90.0, 90.0, 100.0, 100.0)]; n += 1  # clipped to the picture

    # YuNet path with a stand-in cv2
    row = [10, 20, 30, 40] + [0] * 10 + [0.9]
    bx, sc = m.detect_yunet(_FakeCV2([row]), "x.onnx", _Arr(), 0.5)
    assert bx == [(10.0, 20.0, 40.0, 60.0)] and sc == [0.9]; n += 1
    assert m.detect_yunet(_FakeCV2(None), "x.onnx", _Arr(), 0.5) == ([], []); n += 1
    assert _raises(m.detect_yunet, _FakeCV2(fail=True), "x.onnx", _Arr(), 0.5); n += 1
    assert _raises(m.detect_yunet, _FakeCV2([[1, 2, 3, 4, 0.5]]), "x.onnx", _Arr(), 0.5); n += 1
    try:
        m.detect_yunet(_FakeCV2(fail=True), "x.onnx", _Arr(), 0.5)
    except ValueError as e:
        assert "is not a face detector OpenCV can read" in str(e); n += 1

    # node shape
    c = m.SYFaceDetect
    assert c.RETURN_TYPES == ("MASK", "INT", "STRING"); n += 1
    assert c.INPUT_TYPES()["required"]["detector"][0][0] == m.BUILTIN; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYFaceDetect"] == "Face Detect SY"; n += 1
    return n
