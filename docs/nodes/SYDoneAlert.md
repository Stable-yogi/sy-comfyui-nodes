# Done Alert SY (`SYDoneAlert`)

Source: `nodes/sy_done_alert.py`

**What it does:** Put this at the end of a workflow. When the run gets here it plays a sound and shows a note, so you can leave the screen. The value passes through unchanged.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| anything | * | yes | Any value. It is passed on unchanged; the alert fires once this value is ready. |  |
| message | STRING | yes | The note shown on screen when the run is finished. | default 'Your workflow is finished.' |
| sound | COMBO | yes | Which sound to play. None plays no sound. | one of: beep, two beeps, chime, none |
| show_message | BOOLEAN | yes | Show the note in the corner of the screen for a few seconds. | default True |
| desktop_notice | BOOLEAN | yes | Asks the browser for permission to show a system notice when the tab is in the background. | default False |
| volume | FLOAT | yes | How loud the sound is, from 0 (silent) to 1 (full). | 0.0 to 1.0, step 0.05, default 0.4 |
| only_when_idle | BOOLEAN | yes | Only alert when this is the last node of the run: waits until the queue is empty. | default True |

Outputs: `*`

## How to use

1. Put this node at the end of the workflow and connect any value to anything.
2. Set message, sound (beep, two beeps, chime, none) and volume.
3. show_message shows a note. desktop_notice shows a desktop notice. only_when_idle is on by default.
4. The value passes through unchanged.
