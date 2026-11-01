# List Folder Files SY (`SYListFolderFiles`)

Source: `nodes/sy_list_folder_files.py`

**What it does:** Lists the files in a folder inside the input or output folder, one per line, with a count. Optional sort_by (name, newest, oldest, largest, smallest), include_subfolders, a contains filter, with_subfolder to put the folder in front of each name, if_missing to stop on a wrong folder and if_too_many to cut a long list instead of failing. Also gives an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| root | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output |
| subfolder | STRING | yes | Folder inside it. Empty means the folder itself. | default '' |
| extensions | STRING | yes | File endings to keep, like png, jpg or txt. Empty lists every file. | default '' |
| sort_by | COMBO | no | Order of the list: by name, newest or oldest first, largest or smallest first. | one of: name, newest, oldest, largest, smallest |
| include_subfolders | BOOLEAN | no | On: also list files in the folders below (names show the folder). | default False |
| contains | STRING | no | Optional words that must all be in the file name, like 'hero blue'. | default '' |
| with_subfolder | BOOLEAN | no | On: put the subfolder in front of each name (handy for loaders). | default False |
| if_missing | COMBO | no | empty gives an empty list for a missing folder. error stops with a clear message. | one of: empty, error |
| if_too_many | COMBO | no | error refuses more than 5000 files. truncate keeps the first 5000. | one of: error, truncate |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Pick root (input or output) and type subfolder. Empty means the folder itself.
2. Type extensions like png, jpg or txt to keep only those. Empty lists every file.
3. Optional: sort_by, include_subfolders, a contains filter, and with_subfolder to put the folder before each name. if_missing sets whether a wrong folder gives an empty list or an error.
4. The list comes out one name per line, with a count and an info line. More than 5000 files is refused unless if_too_many is truncate.
