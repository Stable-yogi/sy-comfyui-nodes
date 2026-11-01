# SeedVault SY (`SYSeedVault`)

Source: `nodes/sy_seed_vault.py`

**What it does:** A notebook for good seeds. Save a seed with a star rating, a note and tags, see the ranked list as Markdown, hand back the best seed again, and export the ranking to a Markdown file. Keep it at the end of a workflow.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| action | COMBO | yes | Save adds or updates this seed. Show only reads. Export writes the ranking to a .md file in output/sy_seed_vault. | one of: save, show, export |
| collection | STRING | yes | Name of the group this seed belongs to, for example a look or a motion. | default 'my seeds' |
| seed | INT | yes | The seed to keep. | 0 to 9223372036854775807, default 0 |
| rating | INT | yes | Stars from 0 to 5. Higher stars rank first. | 0 to 5, default 3 |
| max_entries | INT | yes | Most entries kept in the whole vault. Extra ones are dropped. | 10 to 5000, default 500 |
| keep_best | BOOLEAN | yes | On drops the lowest rated, oldest entries when full. Off drops the oldest. | default True |
| pick_rank | INT | yes | 0 gives the best seed. 2 gives the second best, and so on. | 0 to 50, default 0 |
| prompt | STRING | no | The prompt used with this seed. Different prompts are kept apart. | default '', multiline |
| note | STRING | no | A short note. Left empty on a re-save keeps the old note. | default '', multiline |
| tags | STRING | no | Words separated by commas. Left empty on a re-save keeps the old tags. | default '' |

Outputs: `INT`, `STRING`, `INT`, `STRING`

## How to use

1. Put Seed Vault SY at the end of a workflow. Connect the seed you used to seed, and the prompt used to prompt.
2. Choose a collection name (a group, for example one look or one motion), give a rating of 0 to 5 stars, and add a short note and tags if you like.
3. Set action to save and run: the seed is kept in the vault. Saving the same seed with the same prompt in the same collection again updates it and adds 1 to its count.
4. Set action to show to read the vault without saving. The ranking output is a Markdown list of that collection. Higher stars rank first, then the seed saved more often, then the newer one.
5. best_seed gives back a seed from the ranking: pick_rank 0 is the best, 1 the second best and so on. Connect it to a sampler to reuse a good seed.
max_entries limits the vault size. When it is full, keep_best on drops the lowest rated and oldest entries, off drops the oldest.
Outputs: best_seed, ranking (Markdown), count (entries in this collection), info (what happened).
The vault is one file in your ComfyUI user folder, so it stays between sessions.
6. Set action to export to write the whole ranking of the collection (with the full prompts) to a Markdown file: `output/sy_seed_vault/<collection>.md`. The vault is not changed.
7. Under the node there is a table of the saved seeds, best first. It reads the vault by itself, also before any run, and refreshes after each run. Pick another collection in the box, press **Copy table** for a Markdown copy, click a seed to copy it, or press **Use** to put that seed in the node's seed box. It is a good view for a dashboard.
