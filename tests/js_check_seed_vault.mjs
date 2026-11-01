import assert from "node:assert/strict";
import { stars, detailText, shortLabel, tableMarkdown, cleanView } from "../js/sy_seed_vault_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };
eq(stars(0), "☆☆☆☆☆"); eq(stars(5), "★★★★★"); eq(stars(3), "★★★☆☆");
eq(stars(9), stars(5)); eq(stars(-2), stars(0)); eq(stars("x"), stars(0)); eq(stars(2.9), stars(2));
eq(detailText({ note: "good", tags: ["a", "b"], prompt: "p" }), "good\ntags: a, b\nprompt: p"); eq(detailText({}), ""); eq(detailText(null), "");
eq(shortLabel({ note: "  a   b " }), "a b"); eq(shortLabel({ tags: ["x", "y"] }), "x, y"); eq(shortLabel({ prompt: "pp" }), "pp"); eq(shortLabel(null), "");
eq(shortLabel({ note: "x".repeat(60) }, 10), "xxxxxxx..."); eq(shortLabel({ note: "x".repeat(10) }, 10), "x".repeat(10));
const rows = [{ rank: 1, seed: "42", rating: 5, count: 2, note: "a|b", tags: ["t"] }, { rank: 2, seed: "7", rating: 1, count: 1, note: "", tags: [] }];
const md = tableMarkdown("looks", rows).split("\n");
eq(md[0], "## looks (2 saved)"); eq(md.length, 6); eq(md[4], "| 1 | 42 | ★★★★★ | 2 | a\|b | t |"); eq(md[5], "| 2 | 7 | ★☆☆☆☆ | 1 |  |  |");
eq(tableMarkdown("e", []).split("\n").length, 4);
eq(cleanView(null), { collections: [], collection: "", rows: [] }); eq(cleanView({ error: "x" }).rows, []); eq(cleanView("x").collections, []);
const v = cleanView({ collections: [{ name: "a", count: 2 }, null, { name: 3 }], collection: "a", rows: [{ seed: 9223372036854775807, rating: 4, count: 1 }, { seed: "nope" }, null, { seed: "5", tags: [1, 2] }] });
eq(v.collections, [{ name: "a", count: 2 }]); eq(v.rows.length, 2); eq(v.rows[1].tags, ["1", "2"]); eq(v.rows[1].rank, 2); eq(v.rows[0].rating, 4);
console.log("seed vault logic checks:", n);
