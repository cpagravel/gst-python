#!/usr/bin/env python3
"""Generate SVG examples of gst output for README.md"""

import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gst import Colors


def create_svg_terminal(content, filename, width=600, height=300):
  """Create an SVG file that looks like a terminal with colored output."""

  # Terminal colors (based on common dark theme)
  bg_color = "#1e1e1e"
  text_color = "#d4d4d4"

  # Convert ANSI colors to SVG colors (more vibrant versions)
  color_map = {
    Colors.BLUE: "#4FC3F7",  # Bright blue
    Colors.CYAN: "#26C6DA",  # Bright cyan
    Colors.GREEN: "#66BB6A",  # Bright green
    Colors.PURPLE: "#CE93D8",  # Bright purple
    Colors.RED: "#EF5350",  # Bright red
    Colors.YELLOW: "#FFEE58",  # Bright yellow
    Colors.WHITE: "#ffffff",
    Colors.OFF: text_color,
    Colors.RESET: text_color,
  }

  # Start SVG
  svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="{bg_color}" rx="8"/>
  <g font-family="'Courier New', monospace" font-size="14" fill="{text_color}">
'''

  # Process content line by line
  lines = content.split("\n")
  y_offset = 25
  line_height = 18

  for line in lines:
    if not line.strip():
      y_offset += line_height
      continue

    # Define column positions for alignment
    col_positions = {
      "index": 15,  # Index number position
      "brackets": 26,  # Opening bracket position
      "index_status": 45,  # INDEX column (aligns with "INDEX" in header)
      "tree_status": 140,  # CUR_TREE column (aligns with "CUR_TREE" in header)
      "filename": 235,  # FILE column (aligns with "FILE" in header)
      "end_bracket": None,  # Will be calculated
    }

    # Parse the line to handle gst output format
    if line.startswith(Colors.YELLOW):
      # Header line - render each part in the correct column
      svg_content += f'    <text x="{col_positions["index"]}" y="{y_offset}" fill="{color_map[Colors.YELLOW]}" font-weight="bold">#</text>\n'
      svg_content += f'    <text x="{col_positions["index_status"]}" y="{y_offset}" fill="{color_map[Colors.YELLOW]}" font-weight="bold">INDEX</text>\n'
      svg_content += f'    <text x="{col_positions["tree_status"]}" y="{y_offset}" fill="{color_map[Colors.YELLOW]}" font-weight="bold">CUR_TREE</text>\n'
      svg_content += f'    <text x="{col_positions["filename"]}" y="{y_offset}" fill="{color_map[Colors.YELLOW]}" font-weight="bold">FILE</text>\n'
    else:
      # Status line - parse each component
      parts = parse_status_line(line)
      if parts:
        # Index number (colored)
        svg_content += f'    <text x="{col_positions["index"]}" y="{y_offset}" fill="{color_map[Colors.PURPLE]}" font-weight="bold">{parts["index"]}</text>\n'

        # Opening bracket (normal text)
        svg_content += f'    <text x="{col_positions["brackets"]}" y="{y_offset}" fill="{text_color}">   </text>\n'

        # Index status (colored)
        svg_content += f'    <text x="{col_positions["index_status"]}" y="{y_offset}" fill="{color_map[Colors.GREEN]}" font-weight="bold">{parts["index_status"]}</text>\n'

        # Tree status (colored)
        svg_content += f'    <text x="{col_positions["tree_status"]}" y="{y_offset}" fill="{color_map[Colors.RED]}" font-weight="bold">{parts["tree_status"]}</text>\n'

        # Filename (normal text)
        svg_content += f'    <text x="{col_positions["filename"]}" y="{y_offset}" fill="{text_color}">{parts["filename"]} </text>\n'

        # Calculate end bracket position
        end_bracket_x = col_positions["filename"] + len(parts["filename"]) * 8.4 + 8

        # Opening parenthesis (normal text)
        svg_content += (
          f'    <text x="{end_bracket_x}" y="{y_offset}" fill="{text_color}">(</text>\n'
        )

        # Index number in parentheses (colored)
        svg_content += f'    <text x="{end_bracket_x + 8.4}" y="{y_offset}" fill="{color_map[Colors.PURPLE]}" font-weight="bold">{parts["index"]}</text>\n'

        # Closing parenthesis (normal text)
        svg_content += f'    <text x="{end_bracket_x + 8.4 + len(parts["index"]) * 8.4}" y="{y_offset}" fill="{text_color}">)</text>\n'

    y_offset += line_height

  svg_content += """  </g>
</svg>"""

  # Write to file
  with open(filename, "w") as f:
    f.write(svg_content)

  print(f"Generated {filename}")


def parse_status_line(line):
  """Parse a gst status line to extract components."""
  # Remove ANSI codes for parsing
  clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)

  # Look for pattern: index   status1  status2  filename (index)
  match = re.match(r"^(\d+)\s+(.{9})\s+(.{9})\s+(.+?)\s+\(\d+\)$", clean_line)
  if match:
    return {
      "index": match.group(1),
      "index_status": match.group(2),
      "tree_status": match.group(3),
      "filename": match.group(4),
    }
  return None


def generate_examples():
  """Generate SVG examples for different gst commands."""

  # Example 1: Basic gst output
  basic_output = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}gst.py ({Colors.PURPLE}1{Colors.OFF})
{Colors.PURPLE}2{Colors.OFF}   {Colors.GREEN}Added     {Colors.OFF}{Colors.RED}Modified  {Colors.OFF}tests/test_gst.py ({Colors.PURPLE}2{Colors.OFF})
{Colors.PURPLE}3{Colors.OFF}   {Colors.GREEN}Deleted   {Colors.OFF}{Colors.RED}        {Colors.OFF}old_file.py ({Colors.PURPLE}3{Colors.OFF})
{Colors.PURPLE}4{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}dist/ ({Colors.PURPLE}4{Colors.OFF})"""

  create_svg_terminal(basic_output, "docs/images/gst-basic.svg", 550, 140)

  # Example 2: After adding files
  after_add = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Added     {Colors.OFF}{Colors.RED}        {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}Added     {Colors.OFF}{Colors.RED}        {Colors.OFF}gst.py ({Colors.PURPLE}1{Colors.OFF})
{Colors.PURPLE}2{Colors.OFF}   {Colors.GREEN}Added     {Colors.OFF}{Colors.RED}Modified  {Colors.OFF}tests/test_gst.py ({Colors.PURPLE}2{Colors.OFF})
{Colors.PURPLE}3{Colors.OFF}   {Colors.GREEN}Deleted   {Colors.OFF}{Colors.RED}        {Colors.OFF}old_file.py ({Colors.PURPLE}3{Colors.OFF})
{Colors.PURPLE}4{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}dist/ ({Colors.PURPLE}4{Colors.OFF})"""

  create_svg_terminal(after_add, "docs/images/gst-after-add.svg", 550, 140)

  # Example 3: Git diff output
  diff_output = f'''{Colors.WHITE}diff --git a/gst.py b/gst.py{Colors.OFF}
{Colors.WHITE}index e697793..295fbeb 100644{Colors.OFF}
{Colors.WHITE}--- a/gst.py{Colors.OFF}
{Colors.WHITE}+++ b/gst.py{Colors.OFF}
{Colors.BLUE}@@ -20,6 +20,7 @@ class Colors:{Colors.OFF}
 class Colors:
   BLUE = "\\033[1;34m"
   BOLD = "\\033[;1m"
{Colors.GREEN}+  CYAN = "\\033[1;36m"{Colors.OFF}
   GREEN = "\\033[1;32m"
   OFF = "\\033[1;;m"
{Colors.RED}-  PURPLE = "\\033[1;35m"{Colors.OFF}
{Colors.GREEN}+  PURPLE = "\\033[1;95m"  # Brighter purple{Colors.OFF}'''

  create_svg_terminal_diff(diff_output, "docs/images/gst-diff.svg", 650, 220)


def create_svg_terminal_diff(content, filename, width=600, height=300):
  """Create an SVG file for diff output with proper line-by-line coloring."""

  # Terminal colors (based on common dark theme)
  bg_color = "#1e1e1e"
  text_color = "#d4d4d4"

  # Convert ANSI colors to SVG colors (more vibrant versions)
  color_map = {
    Colors.BLUE: "#4FC3F7",  # Bright blue
    Colors.CYAN: "#26C6DA",  # Bright cyan
    Colors.GREEN: "#66BB6A",  # Bright green
    Colors.PURPLE: "#CE93D8",  # Bright purple
    Colors.RED: "#EF5350",  # Bright red
    Colors.YELLOW: "#FFEE58",  # Bright yellow
    Colors.WHITE: "#ffffff",
    Colors.OFF: text_color,
    Colors.RESET: text_color,
  }

  # Start SVG
  svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="{bg_color}" rx="8"/>
  <g font-family="'Courier New', monospace" font-size="14" fill="{text_color}">
'''

  # Process content line by line
  lines = content.split("\n")
  y_offset = 25
  line_height = 18

  for line in lines:
    if not line.strip():
      y_offset += line_height
      continue

    # Determine line color and content
    if line.startswith(Colors.WHITE):
      # Header line
      clean_line = line.replace(Colors.WHITE, "").replace(Colors.OFF, "")
      svg_content += f'    <text x="15" y="{y_offset}" fill="{color_map[Colors.WHITE]}" font-weight="bold">{clean_line}</text>\n'
    elif line.startswith(Colors.BLUE):
      # Context line
      clean_line = line.replace(Colors.BLUE, "").replace(Colors.OFF, "")
      svg_content += f'    <text x="15" y="{y_offset}" fill="{color_map[Colors.BLUE]}" font-weight="bold">{clean_line}</text>\n'
    elif line.startswith(Colors.GREEN):
      # Added line
      clean_line = line.replace(Colors.GREEN, "").replace(Colors.OFF, "")
      svg_content += f'    <text x="15" y="{y_offset}" fill="{color_map[Colors.GREEN]}" font-weight="bold">{clean_line}</text>\n'
    elif line.startswith(Colors.RED):
      # Removed line
      clean_line = line.replace(Colors.RED, "").replace(Colors.OFF, "")
      svg_content += f'    <text x="15" y="{y_offset}" fill="{color_map[Colors.RED]}" font-weight="bold">{clean_line}</text>\n'
    else:
      # Normal line
      svg_content += (
        f'    <text x="15" y="{y_offset}" fill="{text_color}">{line}</text>\n'
      )

    y_offset += line_height

  svg_content += """  </g>
</svg>"""

  # Write to file
  with open(filename, "w") as f:
    f.write(svg_content)

  print(f"Generated {filename}")


if __name__ == "__main__":
  # Create docs/images directory if it doesn't exist
  os.makedirs("docs/images", exist_ok=True)
  generate_examples()
