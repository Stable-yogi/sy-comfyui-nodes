# Resource Monitor SY (`SYResourceMonitor`)

Source: `nodes/sy_resource_monitor.py`

**What it does:** Shows small live meters in a corner of the screen: CPU, RAM, GPU load, VRAM and GPU temperature. Good for videos that show how much memory a model takes while it loads. Put one in the workflow; it has no wires.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| enabled | BOOLEAN | yes | Off hides the meters and stops reading. | default True |
| corner | COMBO | yes | Which corner of the screen holds the meters. | one of: top right, top left, bottom right, bottom left |
| interval | FLOAT | yes | Seconds between two readings. | 0.5 to 10.0, step 0.5, default 1.0 |

Outputs: none

## How to use

1. Put one Resource Monitor SY anywhere in the workflow. It has no wires.
2. Small meters show in a screen corner: CPU, RAM, GPU load, VRAM and GPU temperature. Meters the PC cannot read are left out.
3. Choose the **corner** and the **interval** (seconds between readings). Turn **enabled** off to hide the meters and stop reading.
4. Green is fine, yellow from 70 percent, red from 90 percent (temperature: yellow from 75, red from 85).
