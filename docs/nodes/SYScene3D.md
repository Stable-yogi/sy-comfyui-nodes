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

## How to use

1. Open the editor on the node and add cubes, spheres, cylinders, planes or .glb models. Place them and set the camera.
2. Leave scene_json, render_data and depth_data alone, the editor fills them.
3. Set width and height for the output pictures.
4. Outputs: image (shaded picture), depth (near is white) and summary (text list of the objects).
