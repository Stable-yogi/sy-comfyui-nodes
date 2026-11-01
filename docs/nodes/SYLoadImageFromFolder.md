# Load Image From Folder SY (`SYLoadImageFromFolder`)

Source: `nodes/sy_load_image_from_folder.py`

**What it does:** Loads one picture from a folder inside the ComfyUI input folder. The index picks which one and wraps around. Extra sort options (newest, largest, smallest) and an index_mode (wrap, clamp, error) are optional. Also gives the index really used, the number of pictures and an info line. A damaged picture gets a plain message.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| subfolder | STRING | yes | Folder inside the input folder. Empty means the input folder itself. | default '' |
| index | INT | yes | Which picture to load, from 0. Too big a number wraps to the start. | 0 to 2147483647, default 0 |
| sort_by | COMBO | yes | Order of the pictures: by file name, date (oldest first), newest first, largest or smallest. | one of: name, date, newest, largest, smallest |
| index_mode | COMBO | no | wrap goes round at the end. clamp stays on the last picture. error stops. | one of: wrap, clamp, error |

Outputs: `IMAGE`, `MASK`, `STRING`, `INT`, `INT`, `STRING`
