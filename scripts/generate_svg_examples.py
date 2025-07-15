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


def create_svg_terminal_plain(content, filename, width=600, height=300):
  """Create an SVG file with plain text content (no terminal styling)."""

  # Terminal colors (based on common dark theme)
  bg_color = "#1e1e1e"
  text_color = "#d4d4d4"

  # Start SVG
  svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="{bg_color}" rx="8"/>
  <g font-family="'Courier New', monospace" font-size="14" fill="{text_color}">
'''

  # Add the content as simple text
  y_offset = 25
  svg_content += (
    f'    <text x="15" y="{y_offset}" fill="{text_color}">{content}</text>\n'
  )

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

  # Demo Step 1: Initial git status
  demo_initial = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/main.py ({Colors.PURPLE}1{Colors.OFF})
{Colors.PURPLE}2{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/utils.py ({Colors.PURPLE}2{Colors.OFF})
{Colors.PURPLE}3{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}build/ ({Colors.PURPLE}3{Colors.OFF})"""

  create_svg_terminal(demo_initial, "docs/images/demo-01-status.svg", 550, 120)

  # Demo Step 2: File reference output (plain text)
  file_ref_output = "src/main.py"
  create_svg_terminal_plain(
    file_ref_output, "docs/images/demo-02-reference.svg", 200, 60
  )

  # Demo Step 3: After gst -a 0 (add README.md)
  demo_after_add_0 = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Added     {Colors.OFF}{Colors.RED}        {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/main.py ({Colors.PURPLE}1{Colors.OFF})
{Colors.PURPLE}2{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/utils.py ({Colors.PURPLE}2{Colors.OFF})
{Colors.PURPLE}3{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}build/ ({Colors.PURPLE}3{Colors.OFF})"""

  create_svg_terminal(demo_after_add_0, "docs/images/demo-03-after-add.svg", 550, 120)

  # Demo Step 4: After gst -r 0 (reset README.md)
  demo_after_reset = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/main.py ({Colors.PURPLE}1{Colors.OFF})
{Colors.PURPLE}2{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/utils.py ({Colors.PURPLE}2{Colors.OFF})
{Colors.PURPLE}3{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}build/ ({Colors.PURPLE}3{Colors.OFF})"""

  create_svg_terminal(demo_after_reset, "docs/images/demo-04-after-reset.svg", 550, 120)

  # Demo Step 5: After gst -c 1 (checkout src/main.py)
  demo_after_checkout = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/utils.py ({Colors.PURPLE}1{Colors.OFF})
{Colors.PURPLE}2{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}build/ ({Colors.PURPLE}2{Colors.OFF})"""

  create_svg_terminal(
    demo_after_checkout, "docs/images/demo-05-after-checkout.svg", 550, 100
  )

  # Demo Step 6: After gst -D 2 (delete build/)
  demo_after_delete = f"""{Colors.YELLOW}#   INDEX     CUR_TREE  FILE{Colors.OFF}
{Colors.PURPLE}0{Colors.OFF}   {Colors.GREEN}Untrackd  {Colors.OFF}{Colors.RED}Untrackd  {Colors.OFF}README.md ({Colors.PURPLE}0{Colors.OFF})
{Colors.PURPLE}1{Colors.OFF}   {Colors.GREEN}        {Colors.OFF} {Colors.RED}Modified  {Colors.OFF}src/utils.py ({Colors.PURPLE}1{Colors.OFF})"""

  create_svg_terminal(
    demo_after_delete, "docs/images/demo-06-after-delete.svg", 550, 80
  )

  # Demo Step 7: Git diff output for src/utils.py
  demo_diff = f'''{Colors.WHITE}diff --git a/src/utils.py b/src/utils.py{Colors.OFF}
{Colors.WHITE}index a1b2c3d..e4f5g6h 100644{Colors.OFF}
{Colors.WHITE}--- a/src/utils.py{Colors.OFF}
{Colors.WHITE}+++ b/src/utils.py{Colors.OFF}
{Colors.BLUE}@@ -1,5 +1,7 @@{Colors.OFF}
 def format_output(data):
     """Format data for display"""
{Colors.GREEN}+    # Added new validation{Colors.OFF}
{Colors.GREEN}+    if not data:{Colors.OFF}
{Colors.GREEN}+        return "No data"{Colors.OFF}
     return str(data)
{Colors.RED}-    # TODO: Add validation{Colors.OFF}'''

  create_svg_terminal_diff(demo_diff, "docs/images/demo-07-diff.svg", 650, 180)

  # Keep the original examples for backward compatibility
  create_svg_terminal(demo_initial, "docs/images/gst-basic.svg", 550, 120)
  create_svg_terminal(demo_after_add_0, "docs/images/gst-after-add.svg", 550, 120)
  create_svg_terminal_diff(demo_diff, "docs/images/gst-diff.svg", 650, 180)


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
