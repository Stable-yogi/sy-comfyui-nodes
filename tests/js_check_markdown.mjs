import assert from "node:assert/strict";
import { parseInline, parseMarkdown, plainText, MAX_TEXT } from "../js/sy_markdown_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };
const ok = (c, m) => { assert.ok(c, m); n++; };

// headers: the case from the customer's screenshot
eq(parseMarkdown("## Crafted by Animora. Forged by SY."), [{ type: "h2", inline: [{ k: "text", s: "Crafted by Animora. Forged by SY." }] }]);
eq(parseMarkdown("# A")[0].type, "h1");
eq(parseMarkdown("### A")[0].type, "h3");
eq(parseMarkdown("#### too deep")[0].type, "p");   // only three levels
eq(parseMarkdown("#nospace")[0].type, "p");         // needs a space after the hashes
eq(parseMarkdown("  ## indented a little")[0].type, "h2");
eq(parseMarkdown("#    \n")[0].type, "p");         // a lone hash is shown as typed
// paragraphs and lists
eq(parseMarkdown("one\ntwo\n\nthree").map((b) => plainText(b.inline.map((p) => p.s).join(""))), ["one two", "three"]);
eq(parseMarkdown("- a\n* b\n- c").map((b) => b.type), ["li", "li", "li"]);
eq(parseMarkdown("-nospace")[0].type, "p");
eq(parseMarkdown("text\n- item\nmore").map((b) => b.type), ["p", "li", "p"]);
eq(parseMarkdown(""), []); eq(parseMarkdown(null), []); eq(parseMarkdown(undefined), []); eq(parseMarkdown("\n\n  \n"), []);
eq(parseMarkdown("a\r\nb\r\n").length, 1);
// inline marks
eq(parseInline("a **b** c"), [{ k: "text", s: "a " }, { k: "b", s: "b" }, { k: "text", s: " c" }]);
eq(parseInline("*it* and `code`"), [{ k: "i", s: "it" }, { k: "text", s: " and " }, { k: "code", s: "code" }]);
eq(parseInline("2 * 3 * 4"), [{ k: "text", s: "2 * 3 * 4" }]);   // spaces around the star: not italic
eq(parseInline("**open"), [{ k: "text", s: "**open" }]);
eq(parseInline(""), []);
// nothing is read as HTML
eq(parseInline("<b>x</b><script>1</script>"), [{ k: "text", s: "<b>x</b><script>1</script>" }]);
eq(plainText("## Hi **there**"), "Hi there");
// very long text is cut
ok(parseMarkdown("x".repeat(MAX_TEXT * 2))[0].inline[0].s.length === MAX_TEXT);

console.log("markdown logic checks:", n);
