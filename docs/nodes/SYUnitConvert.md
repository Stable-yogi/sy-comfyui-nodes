# Unit Convert SY (`SYUnitConvert`)

Source: `nodes/sy_unit_convert.py`

**What it does:** Converts a number between common units of length, weight, temperature, speed, data size or time. Type the unit names; a unit that does not fit the quantity is refused with a list.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to convert. | -1000000000000000.0 to 1000000000000000.0, step 0.001, default 1.0 |
| quantity | COMBO | yes | What kind of unit this is. Data size uses steps of 1024. | one of: length, weight, temperature, speed, data size, time |
| from_unit | STRING | yes | Unit of the value. length: m km cm mm in ft yd mi. weight: kg g mg lb oz. temperature: c f k. | default 'm' |
| to_unit | STRING | yes | Unit you want. speed: m/s km/h mph kn. data size: b kb mb gb tb. time: ms s min h d. | default 'ft' |
| precision | INT | yes | How many decimals the result is rounded to. | 0 to 12, default 4 |

Outputs: `FLOAT`, `STRING`

## How to use

1. Pick the **quantity**.
2. Type **from_unit** and **to_unit** using the names listed above.
3. Set the **value** and **precision**.
4. Use **result**, or **text** for a ready sentence.
