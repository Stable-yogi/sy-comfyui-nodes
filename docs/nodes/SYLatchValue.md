# Latch Value SY (`SYLatchValue`)

Source: `nodes/sy_latch_value.py`

**What it does:** Remembers the first value it sees and keeps giving that same value on later runs until you reset it, so a random seed or a made-up name can be frozen on purpose. Memory only, nothing is saved to disk.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | STRING | yes | The value to freeze. Numbers go in as text. | default '' |
| latch_on | BOOLEAN | yes | On: keep the first value. Off: pass values through and forget. | default True |
| reset | BOOLEAN | yes | On: forget the stored value and take the new one now. | default False |

Outputs: `STRING`, `BOOLEAN`

## How to use

1. Connect the value to **value**; numbers go in as text.
2. Leave **latch_on** on: the first value seen is kept and given back on later runs.
3. Turn **reset** on for one run to forget the stored value and take the new one, then turn it off again.
4. Turn **latch_on** off to pass values straight through.
5. The outputs give the **value** and **is_frozen**. The memory lasts only while the program runs.
