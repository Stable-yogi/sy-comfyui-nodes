# Edge Detect SY (`SYEdgeDetect`)

Source: `nodes/sy_edge_detect.py`

**What it does:** Finds the outlines in a picture and draws them as a grey edge map. Strong edges are bright, flat areas are dark. Adds a noise filter (blur first), a threshold that drops faint edges, and an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to find edges in. | picture batch [B,H,W,3] |
| method | COMBO | yes | Sobel gives smooth thick edges. Laplacian gives thin sharp lines. | one of: sobel, laplacian |
| strength | FLOAT | yes | Brightness boost for the edges. Raise it to see faint edges. | 0.1 to 10.0, step 0.1, default 1.0 |
| invert | BOOLEAN | yes | Turn on for dark lines on a white background. | default False |
| blur_first | FLOAT | no | Blur radius applied before looking for edges. 1 to 3 hides grain and noise. | 0.0 to 20.0, step 0.5, default 0.0 |
| threshold | FLOAT | no | Edges weaker than this are dropped. 0.1 cleans faint lines. | 0.0 to 1.0, step 0.01, default 0.0 |

Outputs: `IMAGE`, `MASK`, `STRING`

## How to use

1. Connect your picture to image.
2. Pick method: sobel or laplacian. Set strength. Turn on invert to flip bright and dark.
3. blur_first filters noise before. threshold drops faint edges.
4. Outputs: image (a grey edge map), mask and info.
