# Overlap Window Planner SY (`SYOverlapWindowPlanner`)

Source: `nodes/sy_overlap_window_planner.py`

**What it does:** Cuts a long clip into overlapping windows so a long video can be made or processed in pieces and joined later. Gives one line per window and can read out one window.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| total_frames | INT | yes | How many frames the whole clip has. | 1 to 100000, default 200 |
| window_frames | INT | yes | How many frames each piece holds. | 2 to 10000, default 56 |
| overlap_frames | INT | yes | How many frames two neighbouring pieces share. Must be smaller than the window. | 0 to 5000, default 5 |
| last_window | COMBO | yes | Last piece: move it back so it is full (more overlap), or let it be shorter. | one of: shift back so it is full, keep it short |
| pick | INT | yes | Window number to read out, counting from 1. 0 means none. | 0 to 100000, default 0 |

Outputs: `STRING`, `INT`, `INT`, `INT`, `INT`

## How to use

1. Set **total_frames** to the length of the whole clip.
2. Set **window_frames** to how many frames one piece can hold.
3. Set **overlap_frames** to how many frames neighbouring pieces should share. It must be smaller than the window.
4. Pick **last_window**: shift back so it is full, or keep it short.
5. Read the **plan** text. To work on one piece, set **pick** to its number and use **start** and **end_exclusive**.
