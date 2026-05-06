#!/usr/bin/env python3
"""
Update SearXNG config to enable only Google search and configure proxy
"""
from pathlib import Path
import re

# Load config
config_file = Path("settings.yml")
content = config_file.read_text(encoding="utf-8")

# Find the engines section
lines = content.split("\n")

# Find engines section start and end
engines_start = -1
engines_end = -1
in_engines = False

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == "engines:":
        engines_start = i
        in_engines = True
    elif in_engines and re.match(r'^\w+:$', stripped) and not stripped.startswith("-"):
        engines_end = i
        break

if engines_start == -1:
    print("Error: engines section not found")
    exit(1)

# Now find the google and google news engine definitions
enabled_engines = {"google", "google news"}
engine_definitions = {}
current_engine = None
current_lines = []

for i in range(engines_start + 1, engines_end if engines_end != -1 else len(lines)):
    line = lines[i]
    stripped = line.strip()

    if stripped.startswith("- name: "):
        if current_engine:
            engine_definitions[current_engine] = current_lines
        current_engine = stripped[len("- name: "):]
        current_lines = [line]
    elif current_engine:
        current_lines.append(line)

# Add the last engine
if current_engine:
    engine_definitions[current_engine] = current_lines

# Now build the new config
new_lines = lines[:engines_start + 1]

# Add only the enabled engines
for engine_name in enabled_engines:
    if engine_name in engine_definitions:
        # Make sure there's no disabled: true line
        cleaned = []
        for line in engine_definitions[engine_name]:
            if not line.strip().startswith("disabled: true"):
                cleaned.append(line)
        new_lines.extend(cleaned)

# Add the rest of the config
if engines_end != -1:
    new_lines.extend(lines[engines_end:])

# Save the output
config_file.write_text("\n".join(new_lines), encoding="utf-8")
print("Config updated successfully!")
print(f"Enabled engines: {list(enabled_engines)}")
