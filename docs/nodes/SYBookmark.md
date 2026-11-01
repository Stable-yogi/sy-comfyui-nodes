# Bookmark SY (`SYBookmark`)

Source: `nodes/sy_bookmark.py`

**What it does:** Marks a spot in a big workflow. Press its number key (1 to 9) while you are not typing, and the view jumps to this node at the zoom you set. It runs nothing and has no wires.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| key | COMBO | yes | The number key that jumps here. Two bookmarks should not share a key. | one of: 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| zoom | FLOAT | yes | How close the view is after the jump. 1 is normal size. | 0.2 to 3.0, step 0.1, default 1.0 |

Outputs: none

## How to use

1. Add Bookmark SY next to the part of the workflow you want to reach quickly.
2. Pick a key from 1 to 9 and a zoom (1 is normal size, smaller is further away).
3. Click on an empty part of the canvas, then press the number key: the view jumps to this node at that zoom.
The key does nothing while you are typing in a box. If two bookmarks share a key, the node shows a warning and the first one wins. It runs nothing and has no wires.
