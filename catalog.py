"""Build `catalog.json`: Carbon's catalog of the extensions in this repository.

Every package (a folder with `extension.toml`) at the given commit is listed
with its version, the commit, its folder and its content hash, computed the
way Carbon computes it, from the committed files (not the working copy). A
package's `icon` is listed from the same folder with its SHA-256.

Versions listed in the existing `catalog.json` are kept, so older versions
stay installable; a version already listed is not changed (bump `version` in
`extension.toml` to publish new files).

Usage: python catalog.py [COMMIT]   (default: HEAD; push that commit first)
Then commit and push `catalog.json`. Carbon reads it from the default branch.
"""

import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "https://github.com/denizhoroz/carbon-extensions-basic"
CATALOG = ROOT / "catalog.json"


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True).stdout


def files_at(commit: str) -> dict[str, str]:
    """Path -> blob id of every file at `commit`."""
    out = git("ls-tree", "-r", "-z", commit)
    files = {}
    for entry in out.split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        _mode, kind, blob = meta.decode().split()
        if kind == "blob":
            files[path.decode()] = blob
    return files


def blob(blob_id: str) -> bytes:
    return git("cat-file", "blob", blob_id)


def content_hash(package: dict[str, bytes]) -> str:
    """Carbon's `content_hash`: per sorted path, path + NUL + sha256(file)."""
    total = hashlib.sha256()
    for path in sorted(package, key=lambda p: p.encode()):
        total.update(path.encode())
        total.update(b"\0")
        total.update(hashlib.sha256(package[path]).digest())
    return "sha256:" + total.hexdigest()


def main() -> int:
    rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    commit = git("rev-parse", rev).decode().strip()
    files = files_at(commit)
    old = json.loads(CATALOG.read_text("utf-8")) if CATALOG.is_file() else {"packages": []}
    old_by_id = {package["id"]: package for package in old.get("packages", [])}
    packages = []
    for manifest_path in sorted(p for p in files if p.endswith("/extension.toml")):
        folder = manifest_path.rsplit("/", 1)[0]
        prefix = folder + "/"
        package_files = {
            path[len(prefix):]: blob(blob_id)
            for path, blob_id in files.items()
            if path.startswith(prefix)
        }
        manifest = tomllib.loads(package_files["extension.toml"].decode("utf-8-sig"))
        suffixes, file_names = [], []
        for language in manifest.get("languages", []):
            suffixes += language.get("suffixes", [])
            file_names += language.get("file_names", [])
        entry = {
            "id": manifest["id"],
            "name": manifest["name"],
            "description": manifest.get("description", ""),
            "categories": manifest.get("categories", []),
            "suffixes": suffixes,
            "file_names": file_names,
        }
        icon = manifest.get("icon")
        if icon and icon in package_files:
            entry["icon"] = f"{folder}/{icon}"
            entry["icon_sha256"] = hashlib.sha256(package_files[icon]).hexdigest()
        versions = old_by_id.get(manifest["id"], {}).get("versions", [])
        if not any(v["version"] == manifest["version"] for v in versions):
            versions.append({
                "version": manifest["version"],
                "git": URL,
                "commit": commit,
                "path": folder,
                "hash": content_hash(package_files),
            })
            print(f"listed   {manifest['id']} {manifest['version']} ({folder})")
        else:
            print(f"kept     {manifest['id']} {manifest['version']}")
        entry["versions"] = versions
        packages.append({k: v for k, v in entry.items() if v != [] and v != ""})
    catalog = {"schema": 1, "packages": packages}
    CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", "utf-8", newline="\n")
    print(f"wrote {CATALOG.name}: {len(packages)} packages at {commit[:10]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
