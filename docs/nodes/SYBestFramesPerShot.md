# Best Frames Per Shot SY (`SYBestFramesPerShot`)

Source: `nodes/sy_best_frames_per_shot.py`

**What it does:** Picks the best still frames from every shot of a clip with hard cuts (a look sheet or turnaround video). Give it the shot start frames from H3 Look Sheet Prompt SY or Scene Cut Finder SY. It skips the blurred frames next to each cut, keeps the sharpest (or middle) frames per shot, and can leave out pictures you do not want. Feed the result and labels into Image Grid SY for a datasheet.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | All frames of the clip, in order. | picture batch [B,H,W,3] |
| shot_starts | STRING | yes | Frame where each shot starts, split by commas (0 is added for you). Connect shot_starts or cut_indices here. | default '0' |
| frames_per_shot | INT | yes | How many stills to keep from each shot. | 1 to 16, default 1 |
| mode | COMBO | yes | sharpest: the least blurry frames of each shot. middle: frames spread evenly through each shot. | one of: sharpest, middle |
| edge | INT | yes | Frames to skip at the start and end of each shot (cuts often blur these). | 0 to 48, default 3 |
| shot_labels | STRING | no | Shot names, one per line (from H3 Look Sheet Prompt SY). Empty gives shot 1, shot 2 ... | default '', multiline |
| drop | STRING | no | Picture numbers to leave out after a look, like 2, 5 (1 = first picture). | default '' |
| min_shot | INT | no | Shots shorter than this many frames join the shot before (stops false cuts from titles or flashes). 0 keeps all. | 0 to 240, default 8 |

Outputs: `IMAGE`, `STRING`, `STRING`, `INT`, `STRING`

## How to use

1. Connect all frames of the video to images.
2. Connect shot_starts from H3 Look Sheet Prompt SY (best: the planned cuts), or cut_indices from Scene Cut Finder SY.
3. Keep min_shot at 8 or higher. Moving titles or flashes can make the cut finder fire many times in a row; min_shot joins those tiny shots into one.
4. mode sharpest keeps the least blurry frame of each shot; edge skips the blurred frames right next to each cut.
5. Feed images and labels into Image Grid SY (labels input) for a datasheet. Look at it, then write the picture numbers you do not want in drop and run again.
