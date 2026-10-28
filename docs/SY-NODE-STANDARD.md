# SY Node Standard (v1)

One rule book for every SY node. `tests/run_selftest.py` enforces the parts marked [auto].

## 1. Names
| Thing | Rule | Example |
|---|---|---|
| Class id | `SY` + CamelCase name [auto] | `SYSeed` |
| Display name | `<Name> SY` [auto] | `Seed SY` |
| Menu folder | `SY/<Group>`, no emoji [auto] | `SY/Values` |
| Groups | Image, Text, Values, Logic, Resize, Utility, Editors, Notes | |
| Node file | `nodes/sy_<snake>.py` [auto] | `nodes/sy_seed.py` |
| Helper file | `nodes/_sy_<snake>.py` (no node inside) | `nodes/_sy_common.py` |
| Test file | `tests/test_sy_<snake>.py`, has `run()` that returns the number of checks [auto] | |
| JS folder | `js/<snake>/`, extension name `sy.<snake>` | `js/seed/` |
| CSS variables | `--sy-<token>` | `--sy-gold` |
| Server routes | `/sy/<snake>/...` | `/sy/seed/state` |
| User data | `<ComfyUI user dir>/sy/` | |
| Workflow files | `SY - <Title> v<N>.json` | `SY - Krea 2 Basic v1.json` |

Older repo `comfyui-stableyogi-prompt` uses `StableYogiPrompt` / category `StableYogi`. It stays as is. Its next version moves to `SY` names (ASSUMED, veto anytime).

## 2. Colours
- ONE file: `js/sy_theme.json` (it sits in js/ so the browser can load it). Python reads it through `nodes/_sy_common.py` (`theme()`). JS reads the same file.
- No hex colour inside a node file [auto]. Change a colour in the theme file only.
- Values come from the portal palette (skill `sy-brand`): gold `#d4a537` is the brand colour. Font DM Sans.
- Each group has a node colour and a body colour in `groups`.

## 3. Safety rules (every node)
1. Works headless: a run through the API gives the same result as the browser. No node needs JS to do its job.
2. No secret in a plain-text file.
3. No network call unless the user turns it on. No `requests`, `urllib`, `socket`, `http` [auto].
4. Every file write or open goes through `safe_join()` (path guard).
5. No code is downloaded or run at start-up.
6. No `eval`, `exec`, `compile`, `subprocess`, `os.system`, `os.startfile` [auto]. An audited exception goes into `ALLOW` in `tests/run_selftest.py` AND is written here.
7. Node modules do not import `comfy`, `folder_paths` or `server` at top level [auto]. Import inside the function. This keeps the logic testable without ComfyUI.
8. Every node has a `DESCRIPTION` [auto] and a test file [auto].
9. No AI-credit word in any file [auto] (core rule 14).
10. Before the first public release: scan with the registry scanner and fix every hit.

## 4. Node shape
- Pure function holds the logic (`resolve_seed(...)`). The class only wraps it. Tests call the pure function.
- Inputs get a safe `min`/`max`. Bad input raises a clear `ValueError`.
- Add `IS_CHANGED` when the output must change on every run.

## 5. Add a node (steps)
1. Write the behaviour list in plain words (clean-room: from the spec, never from GPL code).
2. Copy `docs/NODE-TEMPLATE.md` to `nodes/sy_<snake>.py`. Fill it.
3. Write `tests/test_sy_<snake>.py`.
4. Run `py -3.12 tests/run_selftest.py`. It must end `PASS`.
5. Add one line to `CHANGELOG.md`.
6. Commit as `Stable Yogi <noreply@stableyogi.com>`. Stage files by path.

## 6. Release gate
Owner OK on every public word. Selftest PASS. `os_home.py check` clean. Registry scanner clean. No push before the owner says.
