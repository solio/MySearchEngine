#!/usr/bin/env python3
"""
Update SearXNG config to enable only Google search and configure proxy
"""
from pathlib import Path
import re

# Load config
config_file = Path("settings.yml")
content = config_file.read_text(encoding="utf-8")

# Engines to keep enabled
enabled_engines = {"google", "google news"}

lines = content.split("\n")
new_lines = []
i = 0
in_engines_section = False

while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # Check if we're entering the engines section
    if stripped == "engines:":
        in_engines_section = True
        new_lines.append(line)
        i += 1
        continue

    # If we're in engines section and see another top-level section, exit
    if in_engines_section and re.match(r'^\w+:$', stripped):
        in_engines_section = False

    new_lines.append(line)

    # If we're in engines section and found an engine name, process it
    if in_engines_section and stripped.startswith("- name: "):
        engine_name = stripped[len("- name: "):]

        # Look ahead to see if there's already a disabled line
        has_disabled = False
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            next_stripped = next_line.strip()
            # Stop when we hit next engine or end of section
            if next_stripped.startswith("- name: ") or re.match(r'^\w+:$', next_stripped):
                break
            if next_stripped.startswith("disabled: "):
                has_disabled = True
                break
            j += 1

        # Add disabled: true if not already present and not in enabled list
        if not has_disabled and engine_name not in enabled_engines:
            # Find the indentation level
            indent = re.match(r'(\s*)- name:', line).group(1)
            new_lines.append(f"{indent}  disabled: true")

    i += 1

# Save the output
config_file.write_text("\n".join(new_lines), encoding="utf-8")
print("Config updated successfully!")
print(f"Enabled engines: {list(enabled_engines)}")
