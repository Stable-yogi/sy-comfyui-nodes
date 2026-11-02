# Key Value Lookup SY (`SYKeyValueLookup`)

Source: `nodes/sy_key_value_lookup.py`

**What it does:** A tiny dictionary. Type lines like 'knight = a tall man in steel armour', then give a key and get its text back. The first matching line wins.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| table | STRING | yes | One 'key = value' per line. Lines starting with # are ignored. | default '', multiline |
| key | STRING | yes | The key to look up. | default '' |
| default | STRING | yes | Text to give back when the key is not in the table. | default '' |
| ignore_case | BOOLEAN | yes | On: Knight and knight count as the same key. | default True |
| separator | STRING | yes | The mark between key and value on each line. | default '=' |

Outputs: `STRING`, `BOOLEAN`

## How to use

1. Type one 'key = value' per line in **table**; lines starting with # are ignored.
2. Type the key you want in **key**.
3. Type in **default** the text to give back if the key is missing.
4. Leave **ignore_case** on if Knight and knight should match, and change **separator** if you use a mark other than =.
5. The outputs give the **value** and **found**, which says whether the key was in the table.
