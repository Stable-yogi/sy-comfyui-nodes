# Negative Prompt Presets SY (`SYNegativePromptPresets`)

Source: `nodes/sy_negative_prompt_presets.py`

**What it does:** Gives a ready-made negative prompt for an image model. Add your own words after it, or replace it. Can take out terms you do not want, drop repeats, and write the list with a weight. Also gives the term count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | Which ready-made negative prompt to use. | one of: general clean, photo realism, portrait, full body, anime, landscape, product shot, architecture, painting, minimal, video, 3d render ... |
| mode | COMBO | yes | Put your custom words after the preset, or use them instead. | one of: add after preset, replace preset |
| custom | STRING | no | Your own words to avoid, separated by commas. | default '', multiline |
| remove_terms | STRING | no | Terms to take out of the result, separated by commas. Any case. | default '' |
| remove_duplicates | BOOLEAN | no | On: if a term appears twice, keep only the first. | default False |
| weight | FLOAT | no | 0 = off. Otherwise the list is written as (terms:weight), for example 1.2. | 0.0 to 2.0, step 0.05, default 0.0 |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Pick a ready-made negative prompt in preset.
2. Type your own words in custom. mode decides if they go after the preset or replace it.
3. Optional: remove_terms takes out terms, remove_duplicates keeps the first of repeated terms, and weight above 0 writes the list as (terms:weight).
Outputs: the negative prompt, the term count and an info line.
