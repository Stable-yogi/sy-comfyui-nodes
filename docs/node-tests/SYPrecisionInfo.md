# Precision Info SY (`SYPrecisionInfo`)

Source: `nodes/sy_precision_info.py`

**What it does:** Shows how many bytes each number format uses per parameter and the file size for a model with N billion parameters.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| parameters_billion | FLOAT | yes | Model size in billions of parameters, for example 12. | 0.01 to 10000.0, step 0.1, default 12.0 |
| precision | COMBO | yes | Number format to look up, or show the whole table. | one of: all (show table), fp32, fp16, bf16, fp8, int8, nf4, fp4, Q8_0 (gguf), Q6_K (gguf), Q5_K_M (gguf), Q4_K_M (gguf) ... |

Outputs: `STRING`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'Size for 12 billion parameters (estimate): fp32: 4 bytes per parameter = 48.0...'; FLOAT=float 24 |
| 2 | parameters_billion = 0.01 (min) | PASS | STRING=str 'Size for 0.01 billion parameters (estimate): fp32: 4 bytes per parameter = 0....'; FLOAT=float 0.02 |
| 3 | parameters_billion = 10000.0 (max) | PASS | STRING=str 'Size for 10000 billion parameters (estimate): fp32: 4 bytes per parameter = 4...'; FLOAT=float 20000 |
| 4 | parameters_billion = 5000.005 (mid) | PASS | STRING=str 'Size for 5000.01 billion parameters (estimate): fp32: 4 bytes per parameter =...'; FLOAT=float 10000 |
| 5 | precision = 'fp32' | PASS | STRING=str 'Size for 12 billion parameters (estimate): fp32: 4 bytes per parameter = 48.0...'; FLOAT=float 48 |
| 6 | precision = 'fp16' | PASS | STRING=str 'Size for 12 billion parameters (estimate): fp16: 2 bytes per parameter = 24.0...'; FLOAT=float 24 |
| 7 | precision = 'bf16' | PASS | STRING=str 'Size for 12 billion parameters (estimate): bf16: 2 bytes per parameter = 24.0...'; FLOAT=float 24 |
| 8 | precision = 'fp8' | PASS | STRING=str 'Size for 12 billion parameters (estimate): fp8: 1 bytes per parameter = 12.00...'; FLOAT=float 12 |
| 9 | precision = 'int8' | PASS | STRING=str 'Size for 12 billion parameters (estimate): int8: 1 bytes per parameter = 12.0...'; FLOAT=float 12 |
| 10 | precision = 'nf4' | PASS | STRING=str 'Size for 12 billion parameters (estimate): nf4: 0.5 bytes per parameter = 6.0...'; FLOAT=float 6 |
| 11 | precision = 'fp4' | PASS | STRING=str 'Size for 12 billion parameters (estimate): fp4: 0.5 bytes per parameter = 6.0...'; FLOAT=float 6 |
| 12 | precision = 'Q8_0 (gguf)' | PASS | STRING=str 'Size for 12 billion parameters (estimate): Q8_0 (gguf): 1.062 bytes per param...'; FLOAT=float 12.75 |
| 13 | precision = 'Q6_K (gguf)' | PASS | STRING=str 'Size for 12 billion parameters (estimate): Q6_K (gguf): 0.82 bytes per parame...'; FLOAT=float 9.84 |
| 14 | precision = 'Q5_K_M (gguf)' | PASS | STRING=str 'Size for 12 billion parameters (estimate): Q5_K_M (gguf): 0.71 bytes per para...'; FLOAT=float 8.52 |
| 15 | precision = 'Q4_K_M (gguf)' | PASS | STRING=str 'Size for 12 billion parameters (estimate): Q4_K_M (gguf): 0.61 bytes per para...'; FLOAT=float 7.32 |
| 16 | precision = 'Q3_K_M (gguf)' | PASS | STRING=str 'Size for 12 billion parameters (estimate): Q3_K_M (gguf): 0.49 bytes per para...'; FLOAT=float 5.88 |
| 17 | precision = 'Q2_K (gguf)' | PASS | STRING=str 'Size for 12 billion parameters (estimate): Q2_K (gguf): 0.33 bytes per parame...'; FLOAT=float 3.96 |

## Verdict

All 17 cases behaved as expected (17 passed, 0 rejected with a clear message).
