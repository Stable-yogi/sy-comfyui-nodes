# Save Image To Folder SY (`SYSaveImageToFolder`)

Source: `nodes/sy_save_image_to_folder.py`

**What it does:** Saves pictures into a folder inside the ComfyUI output folder. The name can use {date} {time} {seed} {counter} {width} {height} {batch} {model} {input}. Preview mode saves nothing in the output folder.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to save. | picture batch [B,H,W,3] |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. No .. or drive letters. | default 'SY' |
| filename_pattern | STRING | yes | File name without extension. Tokens: {date} {time} {seed} {counter} {width} {height} {batch} {model} {input}. | default 'image_{counter}' |
| format | COMBO | yes | File type to save. | one of: png, jpg, webp |
| quality | INT | yes | Quality for jpg and webp. Png ignores it. | 1 to 100, default 95 |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |
| embed_workflow | BOOLEAN | yes | Store the prompt and workflow inside png files so you can reload them. | default True |
| output_mode | COMBO | no | Save writes to the output folder. Preview only shows the pictures and keeps no copy. | one of: save, preview |
| date_folder | BOOLEAN | no | Put the pictures in a folder named with today's date inside the subfolder. | default False |
| model_name | STRING | no | Text for the {model} token, for example a model file name. Folder and extension are cut off. | default '' |
| input_name | STRING | no | Text for the {input} token, for example the name of the source picture. | default '' |

Outputs: `STRING`
