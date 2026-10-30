# Precision Info SY (`SYPrecisionInfo`)

Source: `nodes/sy_precision_info.py`

**What it does:** Shows how many bytes each number format uses per parameter and the file size for a model with N billion parameters.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| parameters_billion | FLOAT | yes | Model size in billions of parameters, for example 12. | 0.01 to 10000.0, step 0.1, default 12.0 |
| precision | COMBO | yes | Number format to look up, or show the whole table. | one of: all (show table), fp32, fp16, bf16, fp8, int8, nf4, fp4, Q8_0 (gguf), Q6_K (gguf), Q5_K_M (gguf), Q4_K_M (gguf) ... |

Outputs: `STRING`, `FLOAT`
