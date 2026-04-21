#!/usr/bin/env vpython3
# Copyright 2026 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import json
import yaml

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../agents"))
dest_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../.gemini/agents"))

# 1. Check if .gemini/agents is a symlink
if os.path.islink(dest_dir):
  print(f"Removing symlink at {dest_dir}")
  os.unlink(dest_dir)

os.makedirs(dest_dir, exist_ok=True)

for item in os.listdir(src_dir):
  item_path = os.path.join(src_dir, item)
  if os.path.isdir(item_path):
    agent_json_path = os.path.join(item_path, "agent.json")
    config_yaml_path = os.path.join(item_path, "config.yaml")

    if os.path.exists(agent_json_path) and os.path.exists(config_yaml_path):
      with open(agent_json_path, "r") as f:
        agent_json = json.load(f)
      with open(config_yaml_path, "r") as f:
        config_yaml = yaml.safe_load(f)

      name = agent_json.get("name")
      description = agent_json.get("description")

      custom_agent = config_yaml.get("custom_agent", {})
      system_prompt_sections = custom_agent.get("system_prompt_sections", [])
      tool_names = custom_agent.get("tool_names", [])

      # Concatenate system prompt sections
      body = ""
      for section in system_prompt_sections:
        body += f"# {section.get('title')}\n\n{section.get('content')}\n\n"

      # Map tools to Gemini CLI names
      gemini_tools = []
      for t in tool_names:
        if t == "view_file":
          gemini_tools.append("read_file")
        elif t == "run_command":
          gemini_tools.append("run_shell_command")
        elif t == "list_dir":
          gemini_tools.append("list_directory")
        else:
          gemini_tools.append(t)

      # Create frontmatter
      frontmatter = {
          "name": name,
          "description": description,
          "kind": "local",
          "tools": gemini_tools,
          "model": "inherit"
      }

      dest_file = os.path.join(dest_dir, f"{name}.md")
      with open(dest_file, "w") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, default_flow_style=False)
        f.write("---\n")
        f.write(body)

      print(f"Installed {name}.md for Gemini CLI")
    else:
      print(f"Skipping {item}: missing agent.json or config.yaml")
