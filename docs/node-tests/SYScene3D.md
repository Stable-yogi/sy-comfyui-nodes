# 3D Scene SY (`SYScene3D`)

Source: `nodes/sy_scene3d.py`

**What it does:** Place cubes, spheres, cylinders, planes and loaded .glb models in a small 3D editor. Gives a shaded picture, a depth picture and a text list of the objects.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| scene_json | STRING | yes | Filled in by the editor on the node: the objects and camera. Leave it alone. | default '' |
| render_data | STRING | yes | Filled in by the editor: the shaded picture of the scene. Leave it alone. | default '' |
| depth_data | STRING | yes | Filled in by the editor: the depth picture (near is white). Leave it alone. | default '' |
| width | INT | yes | Width in pixels of both output pictures. | 64 to 2048, step 8, default 768 |
| height | INT | yes | Height in pixels of both output pictures. | 64 to 2048, step 8, default 768 |

Outputs: `IMAGE`, `IMAGE`, `STRING`

## How it was tested

This node was not run by the harness. Reason: tested in a real ComfyUI page: added shapes, turned the camera, loaded a .glb cube, saved and reloaded the scene. The picture code has script tests.


## Verdict

Not run. tested in a real ComfyUI page: added shapes, turned the camera, loaded a .glb cube, saved and reloaded the scene. The picture code has script tests.
