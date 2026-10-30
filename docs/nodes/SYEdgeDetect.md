# Edge Detect SY (`SYEdgeDetect`)

Source: `nodes/sy_edge_detect.py`

**What it does:** Finds the outlines in a picture and draws them as a grey edge map. Strong edges are bright, flat areas are dark.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to find edges in. | picture batch [B,H,W,3] |
| method | COMBO | yes | Sobel gives smooth thick edges. Laplacian gives thin sharp lines. | one of: sobel, laplacian |
| strength | FLOAT | yes | Brightness boost for the edges. Raise it to see faint edges. | 0.1 to 10.0, step 0.1, default 1.0 |
| invert | BOOLEAN | yes | Turn on for dark lines on a white background. | default False |

Outputs: `IMAGE`, `MASK`
