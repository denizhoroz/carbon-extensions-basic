# carbon-extensions-basic

The official extensions of [Carbon](https://github.com/denizhoroz/carbon): language support (tree-sitter grammars, language servers) and themes. Carbon ships without them; it installs the ones you pick from its extension catalog.

| Folder | Id | Contents |
|---|---|---|
| `languages/rust` | `carbon.rust` | Rust grammar; rust-analyzer (PATH first, else a pinned download for Windows, macOS, Linux x64/arm64) |
| `languages/toml` | `carbon.toml` | TOML grammar |
| `languages/markdown` | `carbon.markdown` | Markdown + inline grammars |
| `languages/yaml` | `carbon.yaml` | YAML grammar |
| `languages/python` | `carbon.python` | Python grammar |
| `languages/javascript` | `carbon.javascript` | JavaScript grammar |
| `languages/typescript` | `carbon.typescript` | TypeScript + TSX grammars |
| `languages/html` | `carbon.html` | HTML grammar |
| `languages/css` | `carbon.css` | CSS grammar |
| `languages/bash` | `carbon.bash` | Bash grammar |
| `themes/gruvbox` | `carbon.gruvbox` | Gruvbox themes (dark and light, hard / medium / soft) |

Packages are grouped by type: `languages/` (grammars, language servers), `themes/`; later `tools/` and others. Each package folder holds `extension.toml` (schema 1) at its root plus its files (`grammars/*.wasm` and `.scm` queries, `themes/*.json`), and optionally `icon = "icon.png"` (png, svg, jpg or webp, square, at most 256 KB; Carbon shows a placeholder without one). The catalog names each package by its folder (`path = "languages/rust"`), so there is no index file here.

## Grammars

The `.wasm` grammars are upstream tree-sitter release builds, pinned by SHA-256 in `grammars.toml`:

```
python fetch_grammars.py          # download missing or changed files
python fetch_grammars.py --check  # verify only (exit 1 on a mismatch)
```

Licenses of the third-party files: `LICENSES.md`.

## Publishing (the catalog)

This repo is also Carbon's default catalog: `catalog.json` at the root lists every package by folder, commit and content hash.

1. Commit and push the package changes (bump `version` in `extension.toml` for new files).
2. `python catalog.py` (lists the new versions at `HEAD`, keeps older ones).
3. Commit and push `catalog.json`.

Carbon fetches it when Extensions opens. Later: sign it (`minisign -Sm catalog.json`, commit `catalog.json.minisig`) and build the public key into Carbon.

## Developing

Carbon's tests and dev links look for a checkout of this repo at `carbon-extensions-basic/` in the root of the Carbon repo (ignored by git there):

```
cd carbon
git clone https://github.com/denizhoroz/carbon-extensions-basic
```

In Carbon, Extensions > Install > Link Development Folder… loads a package straight from its folder.
