#!/usr/bin/env python

import hashlib
import json
import os
import shutil
import sys

def scan_for_files(path):
    files = []
    for root, directories, filenames in os.walk(path):
        relative_name = os.path.basename(root)
        for filename in filenames:
            files.append({"name": os.path.join(relative_name, filename),
                          "path": os.path.realpath(os.path.join(root, filename))})
    return files

def hash_file(path):
    with open(path, "r") as f:
        return hashlib.sha256(f.read()).hexdigest()

def build_manifest(files):
    file_entries = []
    for entry in files:
        name = entry["name"]
        checksum = hash_file(entry["path"])
        file_entries.append({"sha256": checksum, "path": name})
    return {"files": file_entries}

if __name__ == "__main__":
    all_files = []
    for dname in ["commands", "bin", "mist"]:
        all_files = all_files + scan_for_files(dname)
    manifest = build_manifest(all_files)
    with open("manifest.json", "w") as f:
        f.truncate()
        f.write(json.dumps(manifest, sort_keys=True, indent=2, separators=(", ", ": ")))
        f.write("\n")
