// Makes the four test workflows and their API prompts in one go. Run it in the browser console of a ComfyUI test copy
// that has the pack loaded, after you copied build_master.js into that ComfyUI's user folder (user/default/master_build.js):
//   (0, eval)(await (await fetch('/api/userdata/build_all_parts.js')).text())
// It saves the files in that ComfyUI's user folder (workflows/StableYogi-SY-Test-*.json and prompt_*.json).
// Copy them into the master folder of the repo.
(async () => {
  const src = await (await fetch('/api/userdata/master_build.js')).text();
  const PARTS = [['text', '1-Text', 'prompt_1_text'], ['picture', '2-Picture', 'prompt_2_picture'], ['tools', '3-Tools', 'prompt_3_tools'], ['numbers', '4-Numbers-Logic', 'prompt_4_numbers']];
  const post = async (path, obj) => (await fetch('/api/userdata/' + encodeURIComponent(path) + '?overwrite=true', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(obj) })).status;
  const out = [];
  for (const [key, wfname, pname] of PARTS) {
    window.__masterPart = key;
    const res = JSON.parse(await (0, eval)(src));
    const wf = window.app.graph.serialize();
    const prompt = (await window.app.graphToPrompt()).output;
    const s1 = await post('workflows/StableYogi-SY-Test-' + wfname + '.json', wf);
    const s2 = await post(pname + '.json', prompt);
    out.push({ key, nodes: wf.nodes.length, partNodes: res.partNodes, noInput: res.noInput, missing: res.missing, saved: [s1, s2] });
  }
  window.__masterPart = null;
  return JSON.stringify(out);
})();
