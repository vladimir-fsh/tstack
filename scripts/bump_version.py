#!/usr/bin/env python3
"""Bump the plugin's release version without committing or publishing it."""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    ROOT / ".codex-plugin/plugin.json",
    ROOT / ".claude-plugin/plugin.json",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=("patch", "minor", "major"))
    args = parser.parse_args()

    manifests = {path: json.loads(path.read_text(encoding="utf-8")) for path in MANIFESTS}
    versions = {manifest["version"] for manifest in manifests.values()}
    if len(versions) != 1:
        parser.error(
            "manifest versions differ: "
            + ", ".join(f"{p.relative_to(ROOT)}={m['version']}" for p, m in manifests.items())
        )
    current = versions.pop()
    if not isinstance(current, str) or not re.fullmatch(
        r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", current
    ):
        parser.error("the manifest version must be a stable major.minor.patch version")

    parts = list(map(int, current.split(".")))
    index = {"major": 0, "minor": 1, "patch": 2}[args.part]
    parts[index] += 1
    parts[index + 1 :] = [0] * (2 - index)
    updated = ".".join(map(str, parts))
    for path, manifest in manifests.items():
        manifest["version"] = updated
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"tstack: {current} -> {updated}")


if __name__ == "__main__":
    main()
