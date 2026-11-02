# Grid Positions SY (`SYGridPositions`)

Source: `nodes/sy_grid_positions.py`

**What it does:** Works out where every cell of a grid sits, so you can place pictures or labels. Gives one line per cell as index,x,y,width,height plus the total size of the grid.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| columns | INT | yes | How many cells across. | 1 to 64, default 3 |
| rows | INT | yes | How many cells down. | 1 to 64, default 3 |
| cell_width | INT | yes | Width of one cell in pixels. | 1 to 16384, default 512 |
| cell_height | INT | yes | Height of one cell in pixels. | 1 to 16384, default 512 |
| gap | INT | yes | Space between neighbouring cells in pixels. | 0 to 1024, default 16 |
| margin | INT | yes | Empty border around the whole grid in pixels. | 0 to 4096, default 0 |
| order | COMBO | yes | Number the cells along the rows or down the columns. | one of: row by row, column by column |

Outputs: `STRING`, `INT`, `INT`, `INT`

## How to use

1. Set **columns** and **rows**.
2. Set the size of one cell with **cell_width** and **cell_height**.
3. Set **gap** (between cells) and **margin** (around the grid).
4. Pick **order** to number the cells along rows or down columns.
5. Use **positions** (one line per cell: index,x,y,width,height) and the totals to size your canvas.
