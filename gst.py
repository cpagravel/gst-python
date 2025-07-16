#! /usr/bin/env python3
import argparse
import logging
import os
import subprocess
import sys

from typing import Dict, List, Optional, Tuple, Union
from collections import Counter

LOGGER = logging.getLogger(__name__)
sh = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(sh)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

StatusDictType = List[Dict[str, str]]


class Colors:
  BLUE = "\033[1;34m"
  BOLD = "\033[;1m"
  CYAN = "\033[1;36m"
  GREEN = "\033[1;32m"
  OFF = "\033[1;;m"
  PURPLE = "\033[1;35m"
  RED = "\033[1;31m"
  RESET = "\033[0;0m"
  REVERSE = "\033[;7m"
  WHITE = "\033[1;37m"
  YELLOW = "\033[1;33m"

  @staticmethod
  def colorize(text: str, color: str) -> str:
    return color + str(text) + Colors.OFF


def bash(command: Union[List[str], str]) -> Tuple[bytes, bytes]:
  if isinstance(command, list):
    command_array = [cmd.replace('"', "") for cmd in command]
  else:
    command_array = command.split()
  LOGGER.debug("Bash: %s", " ".join(command_array))
  proc = subprocess.Popen(
    command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
  )
  (output, err) = proc.communicate()
  return (output, err)


# credit: https://stackoverflow.com/questions/3305287/python-how-do-you-view-output-that-doesnt-fit-the-screen
# slight modification
class Less:
  def __init__(self, num_lines: int = 40):
    self.num_lines = num_lines

  def __ror__(self, msg: str):
    if len(msg.split("\n")) <= self.num_lines:
      LOGGER.info(msg)
    else:
      with subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE) as less:
        try:
          if less.stdin:
            less.stdin.write(msg.encode("utf-8"))
            less.stdin.close()
          less.wait()
        except KeyboardInterrupt:
          less.kill()
          bash("stty echo")


def open_in_editor(file_path: str) -> None:
  """Open a file in the default editor"""
  # Try to get the default editor from environment variables
  editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")

  if editor:
    cmds = editor.split()
    cmds.append(file_path)
    # Run editor in foreground so it can take over the terminal
    subprocess.run(cmds)
  else:
    LOGGER.info(Colors.colorize("No default editor found", Colors.YELLOW))


def check_valid_ref(num: Union[str, int], item_count: int) -> int:
  """Check if a reference number is valid."""
  num = int(num)
  if num < 0:
    raise argparse.ArgumentTypeError("%s is an invalid positive int value" % num)
  elif num > item_count:
    raise argparse.ArgumentTypeError("%s is an out of range" % num)
  return num


def parse_range(range_string: str, item_count: int) -> List[int]:
  """Parse a range string into a list of integers."""
  output: List[int] = []
  parts = range_string.split(",")  # singles
  for part in parts:
    bounds = part.split(":")  # range selection
    if len(bounds) == 2:  # defined range
      if bounds[1] == "":  # unbounded range
        output += range(int(bounds[0]), item_count + 1)
      else:  # bounded range
        output += range(int(bounds[0]), int(bounds[1]) + 1)
    else:  # single int
      output.append(int(part))
  return sorted(output)


def check_valid_range(range_string: str, item_count: int) -> str:
  """Check if a range string is valid."""
  values = parse_range(range_string, item_count)
  for value in values:
    check_valid_ref(value, item_count)
  return range_string


def get_file_basename(file_path: str) -> str:
  """Get the basename of a file, ensuring it ends with a slash if it's a directory."""
  # Using os.path.basename on a string that ends with / will return an
  # empty string. We want to keep the trailing slash for directories,
  # so we use os.path.normpath and append / to indicate directories.
  basename = os.path.basename(os.path.normpath(file_path))
  return basename + "/" if os.path.isdir(file_path) else basename


class GitStatusTool:
  def __init__(self) -> None:
    self._status_list: StatusDictType = []
    self._item_count: int = 0
    self._parser: argparse.ArgumentParser = self._create_parser()
    self._args: argparse.Namespace
    self._less = Less(20)
    self._git_flag_decode = {
      "M": "Modified",
      "A": "Added   ",
      "D": "Deleted ",
      "R": "Renamed ",
      "C": "Copied  ",
      "U": "Unmerged",
      "T": "TypeChg ",
      "?": "Untrackd",
      "!": "Ignored ",
      "m": "Sub Mod ",
      " ": "        ",
    }

  @property
  def _ref_help_message(self) -> str:
    return """
    {0}   - accepts an {2} for a file reference
    {1} - accepts an {2}, a {3}, and/or a range in the form {4}
                where x is the start index and y is the end index (inclusive)""".format(
      Colors.colorize("REF_INT", Colors.RESET),
      Colors.colorize("REF_RANGE", Colors.RESET),
      Colors.colorize("integer", Colors.BOLD),
      Colors.colorize("comma separated list", Colors.BOLD),
      Colors.colorize("x:y", Colors.BOLD),
    )

  def _generate_status_list(self) -> Tuple[StatusDictType, int]:
    (output_bytes, err) = bash("git status -s")
    if len(err) != 0:
      raise RuntimeError(err.decode("utf-8"))
    output = output_bytes.decode("utf-8")
    lines = output.split("\n")
    # Iterate through git status text
    status_list = []
    for line in lines:
      if line != "":
        file_path = line[3:].split(" -> ")[-1]  # handle renamed case
        status_list.append({"mod": line[0:2], "filePath": file_path})
    self._item_count = len(status_list) - 1
    return (status_list, self._item_count)

  def _check_valid_ref(self, num: Union[str, int]) -> int:
    """Wrapper for the standalone check_valid_ref function."""
    return check_valid_ref(num, self._item_count)

  def _parse_range(self, range_string: str) -> List[int]:
    """Wrapper for the standalone parse_range function."""
    try:
      return parse_range(range_string, self._item_count)
    except ValueError:
      LOGGER.info(
        Colors.colorize("ValueError in range parsing\n", Colors.RED)
        + self._ref_help_message
      )
      exit(1)

  def _check_valid_range(self, range_string: str) -> str:
    """Wrapper for the standalone check_valid_range function."""
    try:
      return check_valid_range(range_string, self._item_count)
    except ValueError:
      LOGGER.info(
        Colors.colorize("ValueError in range parsing\n", Colors.RED)
        + self._ref_help_message
      )
      exit(1)

  def _display_list(self, status_list: Optional[StatusDictType] = None) -> None:
    if status_list is None:
      status_list, _ = self._generate_status_list()
    header = Colors.colorize("#   INDEX     CUR_TREE  FILE", Colors.YELLOW)
    LOGGER.info(header)

    # Count number of files that will have the same basename. This is used
    # to determine if we should display the full path.
    if len(status_list) < 150:  # We don't do this if there are too many files
      seen = Counter([get_file_basename(item["filePath"]) for item in status_list])
    else:
      seen = Counter()

    for index, item in enumerate(status_list):
      path = item["filePath"]
      basename = get_file_basename(path)
      if (not self._args.v) and seen[basename] < 2:
        path = basename
      index_colored = Colors.colorize(str(index), Colors.PURPLE)
      index_status = Colors.colorize(
        self._git_flag_decode[item["mod"][0]], Colors.GREEN
      )
      tree_stats = Colors.colorize(self._git_flag_decode[item["mod"][1]], Colors.RED)
      LOGGER.info(
        "{:<16} {:<21}  {:<21}  {} ({})".format(
          index_colored, index_status, tree_stats, path, index_colored
        )
      )

  def _create_parser(self) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-v", action="store_true", help="show full paths of files")
    parser.add_argument("--debug", action="store_true", help="show bash commands")

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
      "REF",
      metavar="REF_INT",
      type=self._check_valid_ref,
      nargs="?",
      help="output the file path of a referenced file; can be used for input "
      "into other programs",
    )
    group1.add_argument(
      "-a",
      type=self._check_valid_range,
      metavar="REF_RANGE",
      dest="add",
      help=(
        "eq to "
        + Colors.colorize("git add ", Colors.GREEN)
        + Colors.colorize("<file>", Colors.RED)
      ),
    )
    group1.add_argument(
      "-c",
      type=self._check_valid_range,
      metavar="REF_RANGE",
      dest="checkout",
      help=(
        "eq to "
        + Colors.colorize("git checkout HEAD ", Colors.GREEN)
        + Colors.colorize("<file>", Colors.RED)
      ),
    )
    group1.add_argument(
      "-d",
      type=self._check_valid_ref,
      metavar="REF_INT",
      dest="diff",
      help=(
        "eq to "
        + Colors.colorize("git diff HEAD ", Colors.GREEN)
        + Colors.colorize("<file>", Colors.RED)
      ),
    )
    group1.add_argument(
      "-D",
      type=self._check_valid_range,
      metavar="REF_RANGE",
      dest="delete",
      help=(
        "eq to "
        + Colors.colorize("rm ", Colors.GREEN)
        + Colors.colorize("<file>", Colors.RED)
      ),
    )
    group1.add_argument(
      "-e",
      type=self._check_valid_ref,
      metavar="REF_INT",
      dest="edit",
      help=(
        "edit file with either "
        + Colors.colorize("$VISUAL", Colors.GREEN)
        + " or "
        + Colors.colorize("$EDITOR ", Colors.GREEN)
      ),
    )
    group1.add_argument(
      "-r",
      type=self._check_valid_range,
      metavar="REF_RANGE",
      dest="reset",
      help=(
        "eq to "
        + Colors.colorize("git reset HEAD ", Colors.GREEN)
        + Colors.colorize("<file>", Colors.RED)
      ),
    )
    parser.epilog = self._ref_help_message
    return parser

  def run_with_args(self, args_list=None):
    """
    Run gst with specific arguments (useful for testing).

    Args:
      args_list: List of command line arguments, or None to use sys.argv

    Returns:
      Self for method chaining or inspection
    """
    ######################
    # Generate Status List
    ######################
    try:
      self._status_list, self._item_count = self._generate_status_list()
    except RuntimeError as e:
      LOGGER.info(e)
      exit(1)

    self._args = self._parser.parse_args(args_list)
    self._execute_operation()
    return self

  def run(self) -> None:
    """Main entry point for CLI usage."""
    self.run_with_args()

  def _execute_operation(self):
    if self._args.debug:
      LOGGER.setLevel(logging.DEBUG)

    if self._args.REF is not None:  # Print path if reference given
      LOGGER.info(self._status_list[int(self._args.REF)]["filePath"])
    elif self._args.add is not None:  # git add
      cmds = ["git", "add"]
      input_range = self._parse_range(self._args.add)
      # Split for deleted items. Git does not like handling both in the git add calls.
      file_list_non_deleted = [
        self._status_list[x]["filePath"]
        for x in input_range
        if "D" not in self._status_list[x]["mod"]
      ]
      file_list_deleted = [
        self._status_list[x]["filePath"]
        for x in input_range
        if "D" in self._status_list[x]["mod"]
      ]
      bash(cmds + file_list_non_deleted) if file_list_non_deleted else []
      bash(cmds + file_list_deleted) if file_list_deleted else []
      self._display_list()
    elif self._args.checkout is not None:  # git checkout
      cmds = ["git", "checkout", "HEAD"]
      input_range = self._parse_range(self._args.checkout)
      file_list = [self._status_list[x]["filePath"] for x in input_range]
      cmds.extend(file_list)
      bash(cmds)
      self._display_list()
    elif self._args.diff is not None:  # git diff
      cmds = ["git", "diff", "HEAD"]
      cmds.append(self._status_list[int(self._args.diff)]["filePath"])
      (output, _) = bash(cmds)
      output_lines = output.decode("utf-8").split("\n")
      for index, line in enumerate(output_lines):
        try:
          if line[0] == "-":
            output_lines[index] = Colors.RED + line + Colors.OFF
          elif line[0] == "+":
            output_lines[index] = Colors.GREEN + line + Colors.OFF
          elif line[0:2] == "@@":
            k = line.rfind("@")
            output_lines[index] = (
              Colors.BLUE
              + output_lines[index][: k + 1]
              + Colors.OFF
              + output_lines[index][k + 1 :]
            )
          elif line[0:10] == "diff --git":
            output_lines[index] = Colors.WHITE + line
            if index + 2 < len(output_lines):
              output_lines[index + 2] = Colors.WHITE + output_lines[index + 2]
            if index + 3 < len(output_lines):
              output_lines[index + 3] = (
                Colors.WHITE + output_lines[index + 3] + Colors.OFF
              )
        except IndexError:
          pass
      "\n".join(output_lines) | self._less
    elif self._args.delete is not None:  # rm -r
      cmds = ["rm", "-r"]
      input_range = self._parse_range(self._args.delete)
      file_list = [self._status_list[x]["filePath"] for x in input_range]
      cmds.extend(file_list)
      bash(cmds)
      self._display_list()
    elif self._args.edit is not None:  # open in editor
      file_path = self._status_list[int(self._args.edit)]["filePath"]
      open_in_editor(file_path)
    elif self._args.reset is not None:  # git reset
      cmds = ["git", "reset", "HEAD"]
      input_range = self._parse_range(self._args.reset)
      file_list = [self._status_list[x]["filePath"] for x in input_range]
      cmds.extend(file_list)
      bash(cmds)
      self._display_list()
    else:
      self._display_list(status_list=self._status_list)


def main() -> None:
  gst = GitStatusTool()
  gst.run()


if __name__ == "__main__":
  main()
