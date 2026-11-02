# Seamless Loop Finder SY (`SYSeamlessLoopFinder`)

Source: `nodes/sy_seamless_loop_finder.py`

**What it does:** Looks through a clip for the start and end frame that look most alike, so a loop between them is hardly visible. Gives the frames of the best loop and a ranked list of the best candidates.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The clip as a batch of frames. At least 8 frames. | picture batch [B,H,W,3] |
| min_length | INT | yes | Shortest loop to accept, in frames. | 2 to 100000, default 24 |
| max_length | INT | yes | Longest loop to accept, in frames. 0 means up to the whole clip. | 0 to 100000, default 0 |
| compare_size | INT | yes | Frames are shrunk to this many pixels on the long side before comparing. | 8 to 512, default 64 |
| top | INT | yes | How many of the best loop candidates to list in the report. | 1 to 20, default 3 |

Outputs: `IMAGE`, `INT`, `INT`, `INT`, `STRING`

## How to use

1. Connect the clip frames to **images** (at least 8 frames).
2. Set **min_length** and **max_length** to the loop length you can use, in frames. 0 for max_length means up to the whole clip.
3. The **IMAGE** output is the best loop. The two **INT** outputs are its first and last frame number, the third is its length. The **STRING** ranks the best candidates (**top**).
4. Play the result on repeat, or send it to a video save node.
