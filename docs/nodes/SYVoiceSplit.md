# Voice Split SY (`SYVoiceSplit`)

Source: `nodes/sy_voice_split.py`

**What it does:** Cuts a long voice or song into up to 6 pieces of about the same length, each cut placed in the quietest moment near its even point, so no word is cut in half. Feed piece 1 to the first video segment, piece 2 to the second and so on. seconds gives each piece's length for the segment.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The whole voice or song. |  |
| pieces | INT | yes | How many pieces. Keep each piece under 15 s: a 50 s voice needs 4 or more. | 1 to 6, default 4 |
| search_seconds | FLOAT | no | How far a cut may move from the even point to find a pause. | 0.0 to 6.0, step 0.25, default 2.0 |
| overlap_seconds | FLOAT | no | Pieces 2 and later start this much early. Set it to the chain handoff_seconds (1.625). | 0.0 to 4.0, step 0.125, default 1.625 |

Outputs: `AUDIO`, `AUDIO`, `AUDIO`, `AUDIO`, `AUDIO`, `AUDIO`, `STRING`, `INT`, `STRING`

## How to use

1. Connect the whole voice or song to audio.
2. Set pieces so that each piece stays under 15 seconds: a 50 second voice needs 4 pieces or more. Info warns when a piece is too long.
3. Wire piece_1 into the audio of the first chain segment, piece_2 into the second and so on.
4. Use the numbers in seconds as the seconds of each segment, in the same order.
5. Keep overlap_seconds the same as the chain's handoff_seconds (1.625), so the replayed opening of each segment has its own voice under it.
