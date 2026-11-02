# Dither SY (`SYDither`)

Source: `nodes/sy_dither.py`

**What it does:** Gives the picture a retro few-colour look made of dots instead of smooth bands. Fewer levels means a rougher look. Ordered methods make a regular pattern, floyd-steinberg a grainy one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to dither. | picture batch [B,H,W,3] |
| method | COMBO | yes | Ordered makes a regular dot pattern. Floyd-steinberg makes a grainy, natural one. | one of: ordered 4x4, ordered 8x8, floyd-steinberg |
| levels | INT | yes | Steps per colour channel. 2 gives pure black and white dots. | 2 to 16, default 4 |
| mono | BOOLEAN | yes | On: the result is grey instead of colour. | default False |
| strength | FLOAT | yes | How much of the dither is used. 0 keeps the original. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Choose **method** and set **levels**: 2 to 4 for a strong retro look.
3. Turn on **mono** for a grey result, or lower **strength** to blend back towards the original.
4. Floyd-steinberg is refused on pictures wider than 4096 pixels; pick an ordered method or shrink the picture. An alpha channel is passed through.
