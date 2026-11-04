# Changelog

## 1.24.0
- New node (414 in all): Ref Image Size SY (Resize). Puts a reference picture into the shape and size of the video before a video model reads it: fit, fill (crop) or pad to the video shape, with a max side for speed. Warns when a lot of the picture is cut off.
- New node (415 in all): Pick Best References SY (Image). Takes the stills of a character datasheet and hands out three of them as Picture 1, 2 and 3, by shot name or number, plus the sentence that tells the model what each picture shows.
- New node (416 in all): Voice Split SY (Audio). Cuts a long voice or song into up to 6 pieces at its pauses, so each piece fits one chained video segment, with the length of each piece and an overlap for the chain handoff.
- Help pages with a How to use section for all three.

## 1.23.0
- New node (411 in all): H3 Swap Prompt SY (Text). Writes the prompt for swapping one person in a video with a character from a picture: who to swap, who to keep, how much of the new look to take (face and hair, or the whole look). It keeps the movement, timing, background and light of the source video, and warns when the target is too vague.
- New node (412 in all): H3 Look Sheet Prompt SY (Text). Writes one video prompt for a character look sheet: hard cuts to a still camera, one framing per shot (face, profiles, full body, back, details). Presets face set, body set, full set, or your own list. Also gives the frame where each shot starts and the shot names.
- New node (413 in all): Best Frames Per Shot SY (Image). Picks the sharpest (or middle) still from every shot of a clip with hard cuts, skips the blurred frames at each cut, joins tiny false shots, and can leave out pictures you do not want. Feed it into Image Grid SY for a labelled datasheet.
- Help pages with a How to use section for all three. Not yet in the master test workflows.

## 1.22.2
- H3 workflows Video, Turnaround, Upscale and Upscale RTX 4K: on ComfyUI 0.44 a run stopped at the Create Video node with "Value not in list", because ComfyUI 0.44 added a new setting to that node. Fixed: the workflows load and run on ComfyUI 0.44 and still on 0.43.

## 1.22.1
- H3 Forecast Speed Up SY now works together with ComfyUI's own H3 control nodes (Fun ControlNet). Before, when the speed-up node came after the control node, it replaced the control, so the layout video had no effect. Put the speed-up node after the control node: then the control is skipped on the skipped steps too. Using it together with H3 Speed Optimizer SY (or a second copy of itself) now stops with a clear message.
- H3 workflows: Video, Image v1, Image v2, Character Sheet, Turnaround and Voice now have a Speed up node (preset mild). Set it to off for the exact normal result.

## 1.22.0
- New node (410 in all): H3 Forecast Speed Up SY (Utility). Makes MiniMax H3 videos and H3 pictures faster: after a few normal steps it skips the full model on some steps and predicts them from the steps that ran. Presets off, mild, middle and strong, plus manual numbers. At 20 steps mild skips 6 model calls, middle 8 and strong 10. Use 20 or more steps: the 4-step fast mode has nothing to skip. Needs ComfyUI 0.44 or newer. Help page with a How to use section; in the master test workflows.
- H3 Speed Optimizer SY: on ComfyUI 0.44 a run stopped with "aimdo memory compile error". Fixed: the saved steps are now kept outside the memory plan of each model block, like ComfyUI's own H3 nodes do. Older ComfyUI works as before.
- MOSS Image Speed Up workflow: one word removed from the default negative prompt.

## 1.21.1
- Tested on ComfyUI v0.44.0: all 409 nodes pass the four master test workflows. MOSS Speed Up SY gives the same pictures and the same speed as on v0.43.0.

## 1.21.0
- New node (409 in all): MOSS Speed Up SY (Utility). Makes a MOSS-Image picture faster: after a few normal steps it skips the full model on some steps and predicts them from the steps that ran. Presets off, mild, middle and strong, plus manual numbers. The plan output shows how many steps each preset skips; after a run the node shows how many steps and model calls were skipped. Works with every sampler, er_sde included. Needs ComfyUI 0.43 or newer. Help page with a How to use section; in the master test workflows.
- New workflow: workflows/moss/SY - MOSS Image Speed Up v1 (text to picture with the speed-up node, Sampler SY, Decode SY and Save Result SY).

## 1.20.1
- Layout Box Draw SY: pressing Delete on a selected box removed the box but also deleted the whole node. It now removes only the box.

## 1.20.0
- Five new nodes (408 in all). Each has a help page with a How to use section and is in the master test workflows.
- Video and batch: Overlap Window Planner SY (cuts a long clip into overlapping windows, with start and end frames), Overlap Blend SY (joins two clips with a smooth cross-fade over the frames they share), Colour Drift Check SY (shows how much brightness and colour strength crept up or down along a clip).
- Utility: Workflow Check SY (paste a shared workflow before loading it and see which nodes and which model files are missing on this PC).
- Editors: Layout Box Draw SY (draw layout boxes with the mouse on a small canvas inside the node; the boxes come out as box text for the layout nodes).

## 1.19.0
- Thirty new nodes (403 in all). Each has a help page with a How to use section and is in the four master test workflows.
- Picture: Swirl Pinch Bulge Warp SY (twist, pinch or bulge around a point), Perspective Warp SY (pull the four corners of a picture), Dither SY (retro few-colour dots), Motion Blur SY (smear along a direction), Defocus Blur SY (round camera-lens blur), Split Toning SY (one tint for the shadows, another for the highlights), Shadows Highlights SY (opens dark areas and calms very bright ones), Dehaze SY (removes fog and haze).
- Mask: Mask Fill Holes SY (fills closed holes), Mask Keep Largest SY (keeps the biggest blobs), Mask Outline Ring SY (a band around the edge), Mask Noise Texture SY (a cloudy mask from a seed).
- Video and batch: Batch Average SY (all frames into one long-exposure picture), Batch Max Blend SY (light trails: the brightest value at every pixel), Split Screen SY (two clips side by side, stacked or split on a diagonal), Picture In Picture SY (a small clip inside a big one, with a border), Strobe Flash SY (flashes on a beat pattern).
- Audio: Audio Gain dB SY, Audio Reverse SY, Audio Speed Change SY, Audio Beat Finder SY (times and frame numbers of the loud hits), Audio Info SY, Audio Waveform Picture SY (the sound drawn as a picture), Audio High Low Pass SY (cuts rumble or hiss).
- Text: CSV To JSON SY (pasted table to JSON), Text Extract Numbers SY (pulls numbers out of text), Text Redact SY (hides names, emails, numbers and links before sharing).
- Utility: Date Add SY (days, weeks, months, years or business days), Unit Convert SY (length, weight, temperature, speed, data size, time), Cumulative Sum SY (running total, average, maximum, minimum or step).

## 1.18.0
- Twenty-five new nodes (373 in all), and a new group: SY/Audio. Each node has a help page with a How to use section and is in the four master test workflows.
- Picture: Vibrance SY (lifts dull colours more than strong ones), Colour Balance 3-Way SY (tints shadows, mid-tones and highlights separately), Selective Colour SY (changes only one range of colours), Clarity SY (local contrast without glow halos), Lens Distortion SY (barrel or pincushion warp), Ripple Warp SY (water-ripple waves), Cel Shade SY (cartoon look with ink outlines), Oil Paint SY (painterly smoothing that keeps edges).
- Mask: Mask Distance Falloff SY (a soft edge that depends on distance from the shape), Mask Shape Draw SY (draw a rectangle, ellipse or gradient mask from numbers).
- Video: Video Stabilise SY (cancels camera shake), Motion Mask SY (shows what moved), Duplicate Frame Drop SY (drops frames that did not change), Zoom Punch SY (a quick pulse zoom on chosen frames).
- Audio (new group): Audio Fade SY, Audio Normalise SY, Audio Trim Silence SY, Audio Loop To Length SY, Audio Mix SY.
- Text: Table Pick SY (one cell from pasted CSV), JSON To Lines SY (JSON as plain lines), Text Pad Align SY (lines of equal width).
- Utility and batch: Batch Shuffle SY (seeded order), Batch Interleave SY (weave two batches), Grid Positions SY (where each cell of a grid sits).
- Changed defaults: Halftone Dots SY dot size 8 to 5, Scene Cut Finder SY sensitivity 0.25 to 0.15 (it now catches smaller changes).

## 1.17.1
- Fixed the sampler in four H3 workflows (Character Sheet, Turnaround, Video, Voice). They came with a sampler that left the picture banded, smeared and over-saturated in the fast mode; they now use `euler`, which gives a clean result. Upscale was tested both ways and keeps its sampler. Each was run on a real GPU and compared by eye.

## 1.17.0
- Twenty-five new nodes (348 in all). Each has a help page with a How to use section and is in the four master test workflows.
- Picture: Halftone Dots SY (newspaper-print dots), High Pass SY (keeps only fine detail, for sharpening), Seamless Tile Blend SY (fades the edges so a texture repeats without a seam), Glitch Slices SY (shifted horizontal slices), Radial Zoom Blur SY (blur that streaks away from a centre point), Scanlines SY (old-monitor lines), Median Despeckle SY (removes specks and noise), Value Noise Image SY (cloud, paper or grain texture from a seed), Mask Island Cleanup SY (deletes tiny white specks and fills tiny black holes in a mask).
- Video: Echo Trail SY (ghost trails from earlier frames), Freeze Hold SY (holds one frame still for a while), Scene Cut Finder SY (finds the frames where the scene changes), Slide Transition SY (push or wipe from one clip into the next), Sharpest Frame Pick SY (keeps the sharpest frames of a clip).
- Text: Case Style Convert SY (rewrites a phrase into another naming style), Key Value Lookup SY (a tiny dictionary of key = text lines), Strip Markdown SY (plain text from marked-up text), Escape Text SY (make text safe for JSON, a web address or one line, or turn it back), Text Similarity SY (how alike two texts are, as a number).
- Utility and logic: Humanize Number SY (a big raw number as a file size, a duration or a count), Colour Harmony SY (a matching set of colours from one colour), Colour Contrast Check SY (is the text readable on this background), Range Bucket SY (turns a number into a label by the range it falls in), Coalesce Text SY (first text that is not empty), Latch Value SY (keeps a value until you tell it to take a new one).

## 1.16.0
- Fifteen new nodes (323 in all). Each has a help page with a How to use section and is in the four master test workflows.
- Picture: Letterbox SY (cinema bars or a crop to a wanted shape), Chromatic Aberration SY (colour fringes that grow toward the edges), Bloom SY (soft glow from the bright parts), Tilt Shift SY (miniature look: a sharp band with blur growing away from it), Palette Limit SY (reduce a picture to N colours, optional ordered dither).
- Video: Speed Ramp SY (playback speed that changes over time), Ken Burns SY (one picture into a slow zoom and pan clip), Deflicker SY (evens out brightness jumps between frames), Fade In Out SY (fade a clip in from and out to a colour), Frame Number Overlay SY (frame number and time burned into a corner).
- Text: Tag Remove SY (take unwanted tags out of a prompt), Prompt Conflict Check SY (warns about opposite pairs such as day and night), Prompt Variants SY ({red|blue} choices expanded into every combination), Prompt Slot Fill SY (fills [subject] style slots and drops empty ones cleanly), Text Diff Lines SY (which lines are only in A, only in B, or in both).
- H3 workflows: new SY - H3 Image v2 (the picture workflow rebuilt with fewer boxes). Image v1 now uses the euler sampler: with the 4-step fast mode the old sampler gave over-bright, banded pictures.

## 1.15.0
- Ten new nodes (308 in all).
- Progress Bar SY: a bar at the top or bottom of the screen with percent, step, the running node and the time. Good for screen recordings.
- Global Seed SY: one seed box that writes its seed into every other seed box in the graph before each run, then moves on by mode (fixed, random, increment, decrement). Nodes can be skipped by title.
- Resource Monitor SY: small live meters in a screen corner for CPU, RAM, GPU load, VRAM and GPU temperature. Reads through one read-only route.
- Crossfade Slideshow SY: turns a batch of pictures into a slideshow with a hold time and a soft melt between pictures, with an optional loop.
- Fade Mask Batch SY: a batch of masks that fades or wipes over time, for fading an effect in or out.
- Camera Shake SY: a hand-held shake for a clip, with strength, rotation, speed and a seed. Edges are cropped and zoomed so no empty border shows.
- Gradient Map SY: recolours a picture by its brightness with two or three colours, with strength, invert and an optional mask.
- Metadata Compare SY: compares the prompt, seed, steps, cfg, sampler, model and size stored in two PNG files and lists the differences.
- Seamless Loop Finder SY: finds the best start and end frame in a clip so it repeats without a visible jump.
- Save Video Formats SY: saves frames as mp4, webm, gif or animated webp into the output folder, never over an old file.
- Set SY / Get SY (wireless links) got helpers: double-click a Get to jump to its Set, a Set shows how many Gets read it, a missing or doubled name turns red, and the right-click menu can make a Get for a Set.

## 1.14.0
- Two new nodes (298 in all). LTX Latent Bridge SY: turns decoded video frames (for example from an H3 decode) into an LTX-shaped latent in one node. It fits the size to a multiple of 32, fits the frame count to 8n+1 (trim, pad, nearest or exact) and encodes with the LTX VAE you connect; the info line says what changed. Added after a user request, built from the plain idea, with no outside code.
- Mute/Bypass Switch SY: one small switch for the nodes you choose. Select nodes, press Add selected nodes, and on runs them while off mutes or bypasses them. Switches with the same pair name act like radio buttons (one on, the others off). The chosen nodes are saved with the workflow, and opening a workflow changes nothing.
- Seed Vault SY: a table of the saved seeds, best first, under the node (pick a collection, click a seed to copy it, Use puts it in the seed box, Copy table gives Markdown). It is read-only, loads before any run and refreshes after each run.
- Seed Vault SY: new action **export** writes the ranking of a collection to a Markdown file in `output/sy_seed_vault`. The vault is not changed.
- Link Fixer SY fix: repairs of a socket that remembers a wire that does not exist (and the matching case on an input) did nothing in the open workflow, because ComfyUI gives node numbers as text and the fixer looked for them as numbers. Now fixed, so the button and repair on open both work. Removing a wire that is missing its other end already worked.
- Label, Bookmark, Random Unmuter, Link Fixer (including repair on open), Mute/Bypass Switch and the Seed Vault table were checked in a real ComfyUI on two frontend versions (1.57.4 and the older 1.52.7).

## 1.13.0
- Eight new nodes (296 in all).
- Label SY: a big text label that floats in the workflow for titles and step names. Pick the words, size, colour and side. It runs nothing.
- Bookmark SY: marks a spot in a large workflow. Press its number key (1 to 9) while you are not typing and the view jumps there at the zoom you set. Two bookmarks with the same key show a warning.
- Random Unmuter SY: before each run it switches on one node out of a set (every node whose title holds one of your words) and switches the rest off (mute or bypass). Pick at random, or one after the other. A seed makes the order repeat. It also works when you press Queue.
- Link Fixer SY: looks for broken wires (a wire to a node that is gone, a socket that remembers a wire that does not exist, and so on) and removes them on a button press. It can also check a saved workflow file as it is on disk and open a repaired copy; the file itself is never changed. Wires that join two different kinds of data are only reported. This ComfyUI frontend already heals most broken wires when it loads a workflow, so the file check is where this node helps most.
- Seed Vault SY: a notebook for good seeds at the end of a workflow. Save a seed with a star rating, a note and tags, per collection and per prompt. It gives back a ranked Markdown list and the best seed (or the second best, and so on) to reuse. The vault is one file in the ComfyUI user folder and has a size limit with a choice of what to drop when it is full.
- Content Shuffle SY: keeps the colours and textures of a picture but scrambles where they are with a smooth random wobble (same seed, same result). Handy as a colour reference for control workflows.
- Sketch Lines SY: turns a photo into a clean line drawing, black lines on white paper (or the reverse).
- Repeater SY: one value in, the same value out on eight outputs.
- A separate Mute/Bypass Switch was left out here and added in 1.14.0.
- Label, Bookmark, Random Unmuter and Link Fixer are page nodes and were checked in a real ComfyUI (frontend 1.57.4) before release. Seed Vault and Repeater were also run in a real ComfyUI. Content Shuffle and Sketch Lines were run with the node test tool.
- The help pages in `docs/nodes/` and the full list in `docs/NODES.md` are updated (296 nodes).

## 1.12.1
- Apply LUT SY: eight more built-in looks, made from our own simple colour maths, no files needed: sunset glow, cold moon, night city, pastel, bleach bypass, vivid, film stock and noir (15 in all, with the old ones).
- Two older self-tests that disagreed with their nodes (Compare Metrics SY, Image Batch Split Every N SY) are corrected. The nodes were right.

## 1.12.0
- One new node. Stacking Keeper SY: ComfyUI forgets which node lies on top of which when a workflow is closed and opened again, so nodes you raised (Set and Get nodes for example) fall back behind others. Put one Stacking Keeper SY anywhere in the workflow: it notes every time a node is raised or lowered, saves the stacking with the workflow, and puts it back when the workflow opens. Nodes added after the save go on top, deleted nodes are skipped. It has no wires and never runs. A button puts the saved stacking back by hand, and **restore_on_open** turns the automatic part off. It also works inside a subgraph: put a Stacking Keeper SY inside that subgraph, and its stacking comes back when you open the subgraph. Each graph needs its own keeper. Tested on ComfyUI frontend 1.57.4, including real Set and Get nodes.
- Workflow Header SY: the subtitle and the three help texts now understand a few marks. A line that starts with `#`, `##` or `###` becomes a big, medium or small header, `- ` starts a list, `**bold**`, `*italic*` and `` `code` `` work, and a blank line starts a new paragraph. The subtitle box in the Edit window is now a multi-line box. Anything else is shown as typed, and no HTML is ever read. Saved headers keep working.
- Apply LUT SY also reads `.cube` files from a `luts` folder inside the node pack, next to `models/luts` and `input/luts`.
- The help pages in `docs/nodes/` and the full list in `docs/NODES.md` are updated (288 nodes).

## 1.11.0
- One new node. Control Panel SY: one box that holds many dials. Each row has its own name and its own kind (a number, a whole number, a switch, a text, a dropdown with your own list, or a seed) and is one output, named like the row. The slider range is only a slider: type any number in the box and it is never cut off. A row can be renamed on the panel, moved up or down with its wire, or deleted. "Take widgets from nodes" lists the widgets of the other nodes in the workflow, and the ones you tick move into the panel and are connected for you. A seed row can stay fixed, pick a new number each run, or count up, and it shows the seed that was used. It works with Set and Get nodes by plain wiring.
- One more new node. Group Picker SY: a list of the groups of the workflow where you pick ONE. The nodes of the picked group switch on and the nodes of the other listed groups switch off (mute or bypass; a node whose title has one of your words, like "image", is bypassed instead of muted). Nodes outside the listed groups are never touched. The pick is saved with the workflow and put back when the workflow opens, and the output is the name of the picked group. Set and Get nodes and subgraph nodes inside a group switch with it.
- The help pages in `docs/nodes/` and the full list in `docs/NODES.md` are updated (287 nodes).

## 1.10.0
- Twelve new nodes. Power Lora Loader SY: one box with a row for each LoRA (on/off, strength, optional separate CLIP strength, a picker for its trigger words) and a trigger-word text output. Bundle SY and Unbundle SY: pack model, CLIP, VAE, prompts, sampler numbers, picture and mask into one wire and take them apart again (Unbundle lists the keys that were empty). Review Pause SY: stops the run, shows the text, pictures or mask in a window, lets you edit, tick pictures to keep or draw a mask, then goes on (or stops). Done Alert SY: a sound and a note when the run is done, optional desktop notice, optional wait until the queue is empty. Drop Shadow SY, Outer Glow SY and Stroke SY: layer styles for a cut-out picture. Apply LUT SY: six built-in looks, .cube files from `models/luts` or `input/luts`, or pasted .cube text. Remove Background SY (needs a BiRefNet file in `models/background_removal`), Mask From Words SY (type what to select; needs a SAM3 file) and Face Detail SY (redraws each face at a better size and pastes it back softly).
- Two panels in the page, no server part: Fast Toggle SY (big on/off rows for nodes or groups, mute or bypass, "only one on", all on / all off / reverse) and the help window (Alt+H, or F1 on a selected SY node).
- Checked in a real ComfyUI before release: Remove Background SY with a real model, Review Pause SY (Cancel button and the time-out, the window now closes by itself when the time runs out), Done Alert SY (it now waits until no other run is queued, then alerts once).
- Model Downloader SY boxes are now inside the Character Sheet, Image, Turnaround, Upscale, Video and Voice H3 workflows, so the model files each one needs can be fetched with one click each.
- The help pages in `docs/nodes/` and the full list in `docs/NODES.md` are regenerated (285 nodes).

## 1.9.0
- Two new nodes. Model Downloader SY: a list of the models a workflow needs (folder, file name and link). It shows which ones are installed and has a Download button for each missing one, plus Download all missing. It only works when you press a button, never when a workflow runs or loads. It only accepts https links to Hugging Face, Civitai and GitHub and only .safetensors and .gguf files, it shows the size and your free disk space and asks before each download, and it never replaces a file you already have. Paste Back Box SY: takes the crop box from Outpaint Pad SY and either cuts the original area out of the padded picture or pastes a picture back into another one, with an optional soft edge or mask.
- Workflow Header SY now has an optional workflow number ("Workflow 3") and three link buttons: GitHub, Website and YouTube. Saved headers keep working; the number stays empty until you fill it in with the Edit button.
- Wildcard Prompt SY: weights. Write {3::red|1::blue|green} and red comes up three times as often as blue (an option without a number counts as 1). Step-through mode still walks every option once.
- The help pages in `docs/nodes/` and the full list in `docs/NODES.md` are regenerated (273 nodes).

## 1.8.0
- Twenty-one new nodes. Picture: Image Adjust SY (brightness, contrast, gamma, saturation, hue, warmth, tint, sharpen, vignette and grain in one box, with a mask and a mix), Mask Tools SY (threshold, grow or shrink, feather, invert in the right order, with a tinted preview), Tone Curve SY (auto levels, black and white point, midtone, curve points, per-channel, with a histogram picture), Before After SY (split, side by side, top and bottom or difference comparison with labels), Save Pack SY (name tokens, seed and a settings text file beside each picture), Outpaint Pad SY (pad a picture on any side or to a shape like 16:9, fill the new area, and get the mask and a crop box in one box). Text: Prompt Tidy SY (clean spaces and commas, remove duplicates, fix weights, token estimate), Wildcard Prompt SY (random choices like {red|blue}, nested choices, wildcard lists, the same seed gives the same prompt, and it shows what was picked). Models and sampling: Model Loader SY, LoRA SY, Sampler SY (fast, quality or custom), Decode SY, Load Clip SY, Reference Picture SY, Show SY, Save Result SY, Upscale SY. Video (H3): H3 Prompt SY, H3 Guides SY (start picture, end picture, voice and layout video in one box), H3 Tiled Upscale SY (any upscale model in tiles), RTX Upscale SY (a target like 4K instead of a factor). Date Parts SY now shows its proper name.
- Older nodes got more value: plain-word safety checks, an info text output where it helps, and extra optional inputs. Saved workflows keep working: no input or output was removed, renamed or reordered, and every default is the same as before. New inputs are optional and new outputs come last.
- Small fixes: Select By Index Text SY (two switches are now optional inputs), Load Clip SY (a wrong file and type pair gives a plain message), Resolution SY (1:1 now gives 1024 x 1024), Text Case Trim SY (apostrophes), Colour Match SY, Image Blend SY (alpha is kept), Tile Merge SY (dtype is kept), Tile Split SY (optional batch mode), H3 Guides SY (layout model name).
- Before After SY now has a draggable slider in the node itself: drag the line to compare two pictures. Image Compare SY: the slider shows picture A over picture B in the right order.
- Help pages for every node in `docs/nodes/` and the full list in `docs/NODES.md` are regenerated (271 nodes).

## 1.7.0
- Five new nodes. Group Switch SY: a panel with one on/off switch for each group of a workflow (off = bypass or mute, with an optional "one at a time" mode). H3 Length SY: turns seconds into a valid H3 frame count (5, 22, 39 and so on). VoiceLengthEstimate SY: guesses how long a spoken line takes and gives a matching frame count. H3PromptBuilder SY: builds one tidy video prompt from style, world, action, timeline and spoken lines, and warns about mistakes. ImageExists SY: tells you whether a file is in the input, output or temp folder.
- Seven H3 workflows in `workflows/h3/`: Character Sheet, Turnaround, Image, Voice, Video, Upscale and Upscale RTX 4K. Each has a header box, a fast-mode switch and optional groups that you switch on with Group Switch SY.

## 1.6.1
- Colour chips. Add Border SY, Checkerboard SY, Colour Overlay SY, Colour Swatch SY, Gradient Image SY and Hex Colour Mix SY now show a live colour chip under each colour text field, and a colour picker that fills in the hex text. Bad text shows "not a colour". The text field still works as before and a saved workflow is not changed.
- Index Switch SY: when you pick an input that has no link, it now stops with the clear message "input2 is not connected. Connect it or change select." Before, ComfyUI could show a cryptic "needs input" error.

## 1.6.0
- Result preview on every node. After a run, each SY node shows what it made right on the node: a small picture (up to four frames), a red tint for a mask, and the text and number results with a Copy text button. Picture nodes also get a Hold: before button that shows the picture before the node changed it. Switch it off in Settings (SY nodes: show the result on the node) or with the environment variable SY_NO_PREVIEW=1. A node can opt out with SY_NO_PREVIEW = True on its class. Nothing is added to a saved workflow, and a preview error never stops a node.
- Own buttons on 16 nodes. Seed SY: New random seed, Use last seed, and the seed of the last run. Resolution SY, Size Presets SY, Video Size Presets SY: a live shape and the exact size (width x height, megapixels), plus aspect, flip and resolution buttons. Switch SY: one big A/B button. Number Compare SY: a YES/NO lamp. Counter SY: -1, +1, Reset and the next eight values. Multiline Text SY and Prompt Cleaner SY: characters, words and lines. Load Text SY: pick a .txt file from a list. XY Grid Assemble SY: how many pictures it needs. Lora Loader Stack SY, Colour Match SY, Levels Adjust SY, Face Detect SY, XY Values List SY, Prompt Cleaner SY: save, load and delete your own setting presets.

## 1.5.0
- Eleven more nodes: Solarize SY, Sepia SY, Emboss SY (eight directions), Auto Contrast SY, Crop Percent SY, Text Truncate SY, Hash Text SY (sha256, sha1, md5, sha512), Base64 Text SY, Line Numbers SY, List Stats SY and Size Text SY (bytes as KB, MB, GB).
- The four browser test workflows in master/ were rebuilt. They now hold every node (245), including the newer H3, GGUF, tile and batch nodes that the old files lacked.
- Eleven more everyday nodes: Saturation SY (saturation or vibrance), Brightness Contrast SY, Mirror Image SY (left, right, top, bottom or four-way symmetry), Image Stats SY (mean, contrast, dark and bright share), Checkerboard SY, Colour Overlay SY (normal, multiply, screen, overlay, optional mask), Slugify SY, Text Wrap SY, Sort Dedupe Lines SY, Ease Curve SY (nine easing curves between two numbers) and Number Series SY (evenly spaced numbers as text).

## 1.4.0
- Tile Split SY and Tile Merge SY: cut a big picture into equal overlapping tiles, do any work on the tiles, and join them back with a soft blend. Works with tiles that were made bigger by a whole number (2x, 4x). Sizes and positions travel in a text line between the two nodes.

- H3 Chain SY: five nodes that join MiniMax H3 renders into one unbroken take (Settings, Render Segment, Chain To Video, Repair Segment, Load Session). Same on-disk session format as the original, so an old session can be resumed. Needs the H3 model files and a ComfyUI with the V3 node schema; on an older ComfyUI the five nodes stay out and the rest of the pack loads as usual.
- Eight small picture nodes: Edge Detect SY (Sobel or Laplacian, picture and mask), Pixelate SY, Duotone SY, Dominant Colors SY (hex list plus a swatch strip), Posterize SY, Luminance Mask SY, Hue Shift SY and Rounded Corners SY (picture plus mask). Alpha is never touched.
- Nine everyday nodes: Grayscale SY, Invert Image SY, Threshold SY (picture and mask), Gradient Image SY (linear or radial, picture and mask), Colour Temperature SY (warmth and tint), Add Border SY (outside or inside), Roll Image SY (shift with wrap, for seamless textures), Channel Split SY (red, green, blue, alpha as masks) and Seed From Text SY (same text and salt always give the same seed).

## 1.3.1
- Face Detect SY: the tooltip, docs and README now link to the optional face-finder file (https://github.com/Stable-yogi/sy-face-model). It is a separate download, not bundled.

## 1.3.0
- Face Detect SY: finds faces and makes a mask (box or oval) for Inpaint Crop SY. Built-in detector needs only the opencv package; an optional YuNet .onnx file in models/sy_face_detect gives better results. No face found gives an empty mask and no error.

## 1.2.0
- IndexSwitch SY: pick one of up to four inputs by number. Only the chosen branch runs.

## 1.1.0
- GGUF loaders: Unet, CLIP and Dual CLIP (SY versions, same file names and results as the outside loader). Needs the `gguf` pip package.
- H3 Speed Optimizer SY and H3 Low VRAM SY (speed-up and memory helpers for the H3 video model; the sparse kernel is not bundled).

## 1.0.0
- Repo skeleton, theme file, naming checker, standard.
- Seed SY (fixed / random / increment, up to 2^64-1).
- Wave 1 batch A: Resolution, Aspect From Size, Text, Text Join, Find Replace, Prompt Choice, Image Info, Compare Metrics, Run Timer, Free VRAM (all SY). Tensor and ComfyUI paths not run yet.
- Automatic test on every new ComfyUI release (kept outside this repo).
- Batch B2: Image Compare SY (5 modes), Load Image Mini SY, System Info SY (live VRAM and RAM bars, Free memory button), Batch Pick SY.
- Colour palette on right-click (with undo and reset), first-run tour, light and dark theme detection.
- Browser self-check built in for the 3-hour watcher.
- Batches C1-C9: 100+ new nodes: image tools, masks and crop/paste, text and prompt tools, values and logic, sizes and latents, file save/load, model and LoRA helpers, batch/grid/video helpers, dataset and layout helpers. Every node has a tooltip on each input, a description and a test.
- Image Compare slider and Load Image Mini upload/preview buttons (browser side).
- Batches D1 and D2: LLM text helpers (chat/system prompt builders, chunker, token trim, JSON build/get, negative prompts, caption request) and loaders (checkpoint, VAE, CLIP, Unet, name picker) plus video helpers (frame counter, loop, frame rate convert, split, range info). 137 nodes in total.
- Batch E: XY Values List, XY Pick, XY Grid Assemble, XY Label Strip; Paint Mask editor; Set SY / Get SY (wireless links); hover help cards (144 nodes).
- Batch F: 3D Scene SY (no-library 3D scene editor with shaded and depth output); real-file test of the 4 loaders; Paint backdrop and save/reload verified (145 nodes).
- Batch G: Timestamp, Seed Stepper, Seed List, Random Choice, Short ID, Text Stats, Orientation, Colour Swatch (everyday helpers, 153 nodes).
- 3D Scene SY loads .glb model files (up to 3000 triangles, shown as shaded and depth pictures).
- Status dot in the node title: gold ready, yellow missing link, green ran fine, red stopped (setting SY.StatusBadge).
- docs/nodes/: one help page per node (inputs and what it does).
- Batches H and I: Frame Count Snap, Duration Frames, Prompt Schedule, Prompt Schedule List, Video Size Fit, Time Code, Number Wrap, Text Repeat, Date Parts, Cycle Pick, Percent Of, Line Pick, Hex Colour Mix, Ratio Split (167 nodes with Set/Get). Node-test docs now cover file nodes in a throw-away folder.
- Batches J and K: LLM Reply Clean, JSON From Reply, Prompt Emphasis Strip, Prompt Diff, Tag Sort, Prompt Sections, Few Shot Block, Text Between, Sentence Pick, Edit Instruction, Multi Ref Label, Character Sheet Prompt, Text In Image, Edit Preset Pick, Edit Steps List (182 nodes with Set/Get). Lora Loader Stack and Sampler Settings Unpack were run in a real graph with a real checkpoint and LoRAs.
- Look update: nodes are coloured by job (loaders blue, working nodes green, text teal, numbers and logic purple, save brown, notes gold) with white titles; setting "SY.ColorMode" (Role colours, Group colours, Gold only, Off).
- Workflow Header SY: a title banner with three buttons (Nodes to Install, How to Use, Nodes Info) and an edit panel; the texts travel inside the workflow file.
- Save Image To Folder SY: token buttons (+Date +Time +Seed +Counter +Width +Height +Batch +Model +Input), live "Will save as" line, Open / Copy / Folder buttons, Browse folders, PNG / JPG / WebP and Save / Preview switches, date folder, picture grid with n/N badges and a size line. New tokens width, height, batch, model, input.
- Load Image From Folder SY: Browse folders button and a "picks picture n of m" line.
- Folder helper routes /sy/folder/list, /plan, /open: limited to the ComfyUI output and input folders, picture files only (the one audited place that opens Explorer).
- Time badge on each node after a run and a run clock in the top right corner (settings SY.TimeBadge, SY.RunClock).
- Browser parts (js/sy_header.js, js/sy_save.js, js/sy_runtime.js, js/sy_ui_kit.js) were run on the CPU test ComfyUI: banner, token buttons, Will save as, preview mode, picker window and graph reload checked. Open and Folder buttons (Explorer) were not clicked in the test.
- Krea 2 Turbo W01 replacement rebuilt with the header, role colours and a 20 px grid (181 nodes in the pack).
- Colour roles split: sampler, second sampler, seed, pick and save, decode, preview and save now have their own colours (js/sy_theme.json).
- Master test: one workflow with all 181 SY nodes plus sy_master_check.py, which runs it on a ComfyUI server and reports which node is broken (folder master/). Use it after every ComfyUI update.
- Master test split in 4 workflows (Text 52, Picture 51, Tools 48, Numbers and logic 29 nodes, plus the header in each) with a written pass rule. sy_master_check.py runs all four and checks that no SY node is missing; sy_master_fit.py fits all four to one computer; the 3-hour watcher runs the check after every ComfyUI update.
- CLIP Loader SY now reads the type list from your ComfyUI, so new model families (for example minimax) work without an update here.
- Older nodes now in this pack with the same ids as before, so saved workflows still load: Inpaint Crop SY, Inpaint Stitch SY, Krea2 One-Click SY. New: H3 Save Bundle SY and H3 Load Bundle SY (save and reload a latent, prompt, seed and up to 3 reference pictures as one folder). 186 nodes with Set/Get.
- Five Krea 2 nodes added, ported from open-source packs (licences and authors in NOTICE.md and third_party/): Krea2 Edit Model Patch SY, Krea2 Edit Grounded Encode SY, Krea2 Conditioning Rebalance SY, Krea2T Enhancer SY, Krea2T Enhancer Advanced SY. Same inputs and outputs as the originals, new SY ids so both can exist side by side. 191 nodes with Set/Get. Not run on a real Krea 2 model yet.
- Krea2T Enhancer Advanced SY: on a wrong text shape the node now passes its own saved forward function (the original raised an error there). Changed by Stable Yogi.
- Master test rebuilt so all 191 nodes are in the four test prompts (the 10 newest nodes were missing, which failed the ComfyUI v0.43.0 check). A node that cannot find a model file now counts as "needs a file", not as a fault.
- H3 Save Bundle SY now saves a latent that holds video and audio together (a nested tensor). Before, it stopped with "latent holds no tensor to save". H3 Load Bundle SY rebuilds it in the same order. Run on a real H3 preview file.
- H3 Latent Upscaler SY added (192 nodes). It makes an H3 video latent bigger (by a multiplier, to a size, or to a megapixel count) with the 3D upscale model, in chunks for long clips. Rebuilt from the MIT-licensed ComfyUI Minimax H3 Latent Upscaler by LBH-123-AI (licence in third_party/, row in NOTICE.md). Same result as the original on the real model file. Changed by Stable Yogi: clear errors, size planning, node name and grouping.
- Master test: the Tools part now holds H3LatentUpscaler SY too (192 nodes in the four test prompts). A node that needs a real H3 latent counts as "needs a file", not as a fault.
- README written: what you need (ComfyUI v0.42.1 or newer; tested on v0.42.1 and v0.43.0), install, update, groups, troubleshooting. Full node list in docs/NODES.md.
