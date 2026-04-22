#!/usr/bin/env vpython3
# Copyright 2026 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
agents_src = os.path.join(repo_root, "agents")
agents_dest = os.path.join(repo_root, ".agents")

# 1. Check if .agents is a symlink to agents
if os.path.islink(agents_dest):
  target = os.readlink(agents_dest)
  if target == "agents" or target == agents_src:
    print(f"Removing symlink .agents -> {target}")
    os.unlink(agents_dest)

# 2. Ensure .agents is a real directory
os.makedirs(agents_dest, exist_ok=True)

# 3. Process top-level items in agents/
for item in os.listdir(agents_src):
  src_item = os.path.join(agents_src, item)
  dest_item = os.path.join(agents_dest, item)

  # Skip hidden files/dirs
  if item.startswith("."):
    continue

  if item in ["agents", "skills", "rules"]:
    # Create real directory in .agents/
    os.makedirs(dest_item, exist_ok=True)

    # Cleanup dead symlinks
    for sub_item in os.listdir(dest_item):
      dest_sub = os.path.join(dest_item, sub_item)
      if os.path.islink(dest_sub) and not os.path.exists(dest_sub):
        print(f"Removing dead symlink {dest_sub}")
        os.unlink(dest_sub)

    # Symlink individual items inside
    for sub_item in os.listdir(src_item):
      src_sub = os.path.join(src_item, sub_item)
      dest_sub = os.path.join(dest_item, sub_item)
      if not os.path.exists(dest_sub):
        try:
          os.symlink(src_sub, dest_sub)
          print(f"Symlinked {src_sub} to {dest_sub}")
        except Exception as e:
          print(f"Failed to create symlink for {sub_item}: {e}")
  else:
    # For other items, symlink directly
    if not os.path.exists(dest_item):
      try:
        os.symlink(src_item, dest_item)
        print(f"Symlinked {src_item} to {dest_item}")
      except Exception as e:
        print(f"Failed to create symlink for {item}: {e}")

gemini_md_path = os.path.join(repo_root, "GEMINI.md")
if not os.path.exists(gemini_md_path):
  with open(gemini_md_path, "w") as f:
    f.write("@agents/prompts/templates/modular.md\n")
  print("Created GEMINI.md in the repository root.")
else:
  print("Skipping GEMINI.md creation since it already exists.")
