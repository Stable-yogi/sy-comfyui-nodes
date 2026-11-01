// SY Nodes by Stable Yogi: Seed Vault SY table. Shows the saved seeds of one collection as a ranked table under the node.
// Click a seed to copy it, press Use to put it in the node's seed box. The table reads the vault through a read-only route.
// Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, setWidget, widgetValue } from "./sy_ui_kit.js";
import { stars, detailText, shortLabel, tableMarkdown, cleanView } from "./sy_seed_vault_logic.js";

const TYPE = "SYSeedVault";
const FONT = "'DM Sans', sans-serif";

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (_) {
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;opacity:0";
      document.body.append(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      return ok;
    } catch (e) {
      return false;
    }
  }
}

function setup(node) {
  const root = document.createElement("div");
  root.style.cssText = "display:flex;flex-direction:column;gap:6px;padding:4px;box-sizing:border-box;width:100%;font:12px " + FONT + ";color:" + tk("white");
  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;gap:6px;align-items:center;flex-wrap:wrap";
  const sel = document.createElement("select");
  sel.title = "Which collection to show.";
  sel.style.cssText = "background:" + tk("surface_3") + ";color:" + tk("white") + ";border:0;border-radius:6px;padding:3px;max-width:180px";
  const status = document.createElement("span");
  status.style.cssText = "color:" + tk("text_2") + ";font-size:11px";
  const list = document.createElement("div");
  list.style.cssText = "display:flex;flex-direction:column;gap:3px;max-height:260px;overflow-y:auto";
  let view = { collections: [], collection: "", rows: [] };

  const draw = () => {
    list.textContent = "";
    if (!view.rows.length) {
      const none = document.createElement("div");
      none.textContent = view.collections.length ? "Nothing saved in this collection yet." : "The vault is empty. Run with action save to keep a seed.";
      none.style.cssText = "color:" + tk("text_2") + ";padding:4px";
      list.append(none);
    }
    for (const r of view.rows) {
      const line = document.createElement("div");
      line.style.cssText = "display:flex;gap:6px;align-items:center;padding:3px 4px;border-radius:6px;background:" + tk("surface_2");
      line.title = detailText(r);
      const rank = document.createElement("span");
      rank.textContent = "#" + r.rank;
      rank.style.cssText = "width:26px;flex:none;color:" + tk("text_2");
      const seed = document.createElement("button");
      seed.type = "button";
      seed.textContent = r.seed;
      seed.title = "Click to copy this seed.";
      seed.style.cssText = "cursor:pointer;border:0;background:transparent;color:" + tk("gold") + ";font:600 12px " + FONT + ";padding:0;flex:none;text-align:left";
      seed.onclick = async (e) => {
        e.stopPropagation();
        status.textContent = (await copy(r.seed)) ? "Copied seed " + r.seed : "Could not copy";
      };
      const st = document.createElement("span");
      st.textContent = stars(r.rating);
      st.style.cssText = "flex:none;color:" + tk("gold");
      const cnt = document.createElement("span");
      cnt.textContent = "x" + r.count;
      cnt.title = "How many times it was saved.";
      cnt.style.cssText = "flex:none;color:" + tk("text_2");
      const what = document.createElement("span");
      what.textContent = shortLabel(r);
      what.style.cssText = "flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:" + tk("text_2");
      const use = button("Use", "ghost", "Put this seed in the seed box of this node.");
      use.style.padding = "1px 6px";
      use.onclick = (e) => {
        e.stopPropagation();
        setWidget(node, "seed", Number(r.seed));
        status.textContent = "Seed box set to " + r.seed;
      };
      line.append(rank, seed, st, cnt, what, use);
      list.append(line);
    }
    status.textContent = view.rows.length ? view.rows.length + " shown" : "";
    const want = 150 + Math.min(view.rows.length, 8) * 28;
    if (node.size && node.size[1] < want && !node._syUserSized) node.setSize?.([Math.max(node.size[0], 420), want]);
  };

  const refresh = async (name) => {
    try {
      const q = name !== undefined && name !== null ? "?collection=" + encodeURIComponent(name) : "";
      const res = await api.fetchApi("/sy/seed_vault/list" + q);
      view = cleanView(await res.json());
    } catch (err) {
      view = { collections: [], collection: "", rows: [] };
      status.textContent = "Could not read the vault";
      console.warn("[SY] seed vault table", err);
    }
    sel.textContent = "";
    for (const c of view.collections) {
      const o = document.createElement("option");
      o.value = c.name;
      o.textContent = c.name + " (" + c.count + ")";
      sel.append(o);
    }
    sel.value = view.collection;
    draw();
  };
  sel.onchange = () => refresh(sel.value);

  const bRefresh = button("Refresh", "ghost", "Read the vault again.");
  bRefresh.onclick = (e) => { e.stopPropagation(); refresh(sel.value || undefined); };
  const bCopy = button("Copy table", "ghost", "Copy this table as Markdown for your notes.");
  bCopy.onclick = async (e) => {
    e.stopPropagation();
    status.textContent = (await copy(tableMarkdown(view.collection, view.rows))) ? "Table copied" : "Could not copy";
  };
  const bMine = button("Show the node's collection", "ghost", "Switch the table to the collection typed in the node.");
  bMine.onclick = (e) => { e.stopPropagation(); refresh(String(widgetValue(node, "collection", "")).trim()); };
  bar.append(sel, bRefresh, bCopy, bMine, status);
  root.append(bar, list);
  const w = node.addDOMWidget("sy_seed_vault_table", "custom", root, { serialize: false });
  w.computeSize = (width) => [width, 130];
  node._syVault = { refresh };
  node._syVaultListener = () => setTimeout(() => refresh(sel.value || undefined), 500);
  api.addEventListener("execution_success", node._syVaultListener);
  return refresh;
}

app.registerExtension({
  name: "sy.seed_vault",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        const refresh = setup(this);
        setTimeout(() => refresh(String(widgetValue(this, "collection", "")).trim() || undefined), 400);
      } catch (e) {
        console.warn("[SY] seed vault table not added", e);
      }
      return r;
    };
    // after any run finishes, read the vault again (a save may have just happened)
    const removed = nodeType.prototype.onRemoved;
    nodeType.prototype.onRemoved = function () {
      if (this._syVaultListener) api.removeEventListener("execution_success", this._syVaultListener);
      return removed ? removed.apply(this, arguments) : undefined;
    };
    const resized = nodeType.prototype.onResize;
    nodeType.prototype.onResize = function () {
      this._syUserSized = true;
      return resized ? resized.apply(this, arguments) : undefined;
    };
  },
});
