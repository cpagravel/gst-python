#!/usr/bin/env python3
"""Unit tests for gst module."""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
import argparse

# Import the module we're testing
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gst


class TestColors:
  """Test the Colors class and colorize method."""

  def test_colorize_basic(self):
    """Test basic colorization functionality."""
    result = gst.Colors.colorize("test", gst.Colors.RED)
    expected = gst.Colors.RED + "test" + gst.Colors.OFF
    assert result == expected

  def test_colorize_with_number(self):
    """Test colorization with non-string input."""
    result = gst.Colors.colorize(42, gst.Colors.BLUE)
    expected = gst.Colors.BLUE + "42" + gst.Colors.OFF
    assert result == expected


class TestBashFunction:
  """Test the bash command execution function."""

  @patch("subprocess.Popen")
  def test_bash_command_string(self, mock_popen):
    """Test bash function with string command."""
    # Setup mock
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b"output", b"error")
    mock_popen.return_value = mock_process

    # Test
    output, error = gst.bash("git status")

    # Assertions
    assert output == b"output"
    assert error == b"error"
    mock_popen.assert_called_once_with(
      ["git", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
    )

  @patch("subprocess.Popen")
  def test_bash_command_with_list(self, mock_popen):
    """Test bash function with list command."""
    # Setup mock
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b"list_output", b"list_error")
    mock_popen.return_value = mock_process

    # Test
    output, error = gst.bash(["git", "status", "--porcelain"])

    # Assertions
    assert output == b"list_output"
    assert error == b"list_error"
    mock_popen.assert_called_once_with(
      ["git", "status", "--porcelain"],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      shell=False,
    )

  @patch("subprocess.Popen")
  def test_bash_removes_quotes_from_list(self, mock_popen):
    """Test that bash function removes quotes from list commands."""
    # Setup mock
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b"", b"")
    mock_popen.return_value = mock_process

    # Test with quoted strings in list
    gst.bash(["git", '"status"', '"--porcelain"'])

    # Verify quotes were removed
    mock_popen.assert_called_once_with(
      ["git", "status", "--porcelain"],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      shell=False,
    )


class TestValidationFunctions:
  """Test the validation and parsing functions."""

  def test_check_valid_ref_valid_input(self):
    """Test check_valid_ref with valid inputs."""
    # Test with string input
    assert gst.check_valid_ref("5", 10) == 5
    # Test with int input
    assert gst.check_valid_ref(3, 10) == 3
    # Test boundary values
    assert gst.check_valid_ref(0, 10) == 0
    assert gst.check_valid_ref(10, 10) == 10

  def test_check_valid_ref_negative_input(self):
    """Test check_valid_ref with negative input."""
    with pytest.raises(
      argparse.ArgumentTypeError, match="is an invalid positive int value"
    ):
      gst.check_valid_ref(-1, 10)

  def test_check_valid_ref_out_of_range(self):
    """Test check_valid_ref with out of range input."""
    with pytest.raises(argparse.ArgumentTypeError, match="is an out of range"):
      gst.check_valid_ref(15, 10)

  def test_parse_range_single_numbers(self):
    """Test parse_range with single numbers."""
    assert gst.parse_range("5", 10) == [5]
    assert gst.parse_range("0", 10) == [0]
    assert gst.parse_range("10", 10) == [10]

  def test_parse_range_comma_separated(self):
    """Test parse_range with comma separated values."""
    assert gst.parse_range("1,3,5", 10) == [1, 3, 5]
    assert gst.parse_range("0,10", 10) == [0, 10]

  def test_parse_range_bounded_ranges(self):
    """Test parse_range with bounded ranges (x:y)."""
    assert gst.parse_range("2:5", 10) == [2, 3, 4, 5]
    assert gst.parse_range("0:3", 10) == [0, 1, 2, 3]
    assert gst.parse_range("8:10", 10) == [8, 9, 10]

  def test_parse_range_unbounded_ranges(self):
    """Test parse_range with unbounded ranges (x:)."""
    assert gst.parse_range("5:", 10) == [5, 6, 7, 8, 9, 10]
    assert gst.parse_range("8:", 10) == [8, 9, 10]
    assert gst.parse_range("0:", 3) == [0, 1, 2, 3]

  def test_parse_range_mixed_formats(self):
    """Test parse_range with mixed formats."""
    assert gst.parse_range("1,3:5,8", 10) == [1, 3, 4, 5, 8]

  def test_parse_range_output_sorted(self):
    assert gst.parse_range("0,5:,2", 10) == [0, 2, 5, 6, 7, 8, 9, 10]

  def test_parse_range_invalid_format(self):
    """Test parse_range with invalid format."""
    with pytest.raises(ValueError):
      gst.parse_range("random_letters", 10)

  def test_check_valid_range_invalid_format(self):
    """Test check_valid_range with invalid format."""
    with pytest.raises(ValueError):
      gst.check_valid_range("random_letters", 10)

  def test_check_valid_range_valid_inputs(self):
    """Test check_valid_range with valid inputs."""
    # Should return the input string if all values are valid
    assert gst.check_valid_range("1,3,5", 10) == "1,3,5"
    assert gst.check_valid_range("2:5", 10) == "2:5"
    assert gst.check_valid_range("0:", 10) == "0:"

  def test_check_valid_range_invalid_refs(self):
    """Test check_valid_range with invalid references."""
    # Should raise exception for out of range values
    with pytest.raises(argparse.ArgumentTypeError):
      gst.check_valid_range("15", 10)

    with pytest.raises(argparse.ArgumentTypeError):
      gst.check_valid_range("1,15", 10)

  def test_check_valid_range_negative_refs(self):
    """Test check_valid_range with negative references."""
    with pytest.raises(argparse.ArgumentTypeError):
      gst.check_valid_range("-1", 10)

    with pytest.raises(argparse.ArgumentTypeError):
      gst.check_valid_range("1,-1", 10)


class TestGenerateStatusList:
  """Test the _generate_status_list method."""

  @patch("gst.bash")
  def test_generate_status_list_empty(self, mock_bash):
    """Test _generate_status_list with empty git status."""
    mock_bash.return_value = (b"", b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    assert status_list == []
    assert item_count == -1
    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_single_file(self, mock_bash):
    """Test _generate_status_list with single modified file."""
    mock_bash.return_value = (b"M  example.py\n", b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [{"mod": "M ", "filePath": "example.py"}]
    assert status_list == expected
    assert item_count == 0
    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_multiple_files(self, mock_bash):
    """Test _generate_status_list with multiple files."""
    git_output = b"M  modified.py\nA  added.py\nD  deleted.py\n?? untracked.py\n"
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "M ", "filePath": "modified.py"},
      {"mod": "A ", "filePath": "added.py"},
      {"mod": "D ", "filePath": "deleted.py"},
      {"mod": "??", "filePath": "untracked.py"},
    ]
    assert status_list == expected
    assert item_count == 3
    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_renamed_file(self, mock_bash):
    """Test _generate_status_list with renamed file."""
    git_output = b"R  old_name.py -> new_name.py\n"
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [{"mod": "R ", "filePath": "new_name.py"}]
    assert status_list == expected
    assert item_count == 0
    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_complex_paths(self, mock_bash):
    """Test _generate_status_list with complex file paths."""
    git_output = (
      b"M  src/utils/helper.py\nA  tests/test_new.py\n?? config/settings.json\n"
    )
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "M ", "filePath": "src/utils/helper.py"},
      {"mod": "A ", "filePath": "tests/test_new.py"},
      {"mod": "??", "filePath": "config/settings.json"},
    ]
    assert status_list == expected
    assert item_count == 2
    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_mixed_modifications(self, mock_bash):
    """Test _generate_status_list with mixed index/working tree modifications."""
    git_output = (
      b"MM both_modified.py\nAM added_then_modified.py\n M working_tree_only.py\n"
    )
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "MM", "filePath": "both_modified.py"},
      {"mod": "AM", "filePath": "added_then_modified.py"},
      {"mod": " M", "filePath": "working_tree_only.py"},
    ]
    assert status_list == expected
    assert item_count == 2
    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_trailing_newline(self, mock_bash):
    """Test _generate_status_list handles trailing newline correctly."""
    git_output = b"M  file1.py\nA  file2.py\n"
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "M ", "filePath": "file1.py"},
      {"mod": "A ", "filePath": "file2.py"},
    ]
    assert status_list == expected
    assert item_count == 1

  @patch("gst.bash")
  def test_generate_status_list_spaces_in_filename(self, mock_bash):
    """Test _generate_status_list with spaces in filenames."""
    git_output = b"M  file with spaces.py\nA  another file.txt\n"
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "M ", "filePath": "file with spaces.py"},
      {"mod": "A ", "filePath": "another file.txt"},
    ]
    assert status_list == expected
    assert item_count == 1

  @patch("gst.bash")
  def test_generate_status_list_git_error(self, mock_bash):
    """Test _generate_status_list with git error."""
    mock_bash.return_value = (b"", b"fatal: not a git repository")

    tool = gst.GitStatusTool()

    with pytest.raises(RuntimeError, match="fatal: not a git repository"):
      tool._generate_status_list()

    mock_bash.assert_called_once_with("git status -s")

  @patch("gst.bash")
  def test_generate_status_list_unicode_filenames(self, mock_bash):
    """Test _generate_status_list with unicode filenames."""
    git_output = "M  файл.py\nA  测试.txt\n".encode("utf-8")
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "M ", "filePath": "файл.py"},
      {"mod": "A ", "filePath": "测试.txt"},
    ]
    assert status_list == expected
    assert item_count == 1

  @patch("gst.bash")
  def test_generate_status_list_all_git_flags(self, mock_bash):
    """Test _generate_status_list with all possible git status flags."""
    git_output = b"""M  modified.py
A  added.py
D  deleted.py
R  renamed.py -> new_renamed.py
C  copied.py -> new_copied.py
U  unmerged.py
T  typechange.py
?? untracked.py
!! ignored.py
"""
    mock_bash.return_value = (git_output, b"")

    tool = gst.GitStatusTool()
    status_list, item_count = tool._generate_status_list()

    expected = [
      {"mod": "M ", "filePath": "modified.py"},
      {"mod": "A ", "filePath": "added.py"},
      {"mod": "D ", "filePath": "deleted.py"},
      {"mod": "R ", "filePath": "new_renamed.py"},
      {"mod": "C ", "filePath": "new_copied.py"},
      {"mod": "U ", "filePath": "unmerged.py"},
      {"mod": "T ", "filePath": "typechange.py"},
      {"mod": "??", "filePath": "untracked.py"},
      {"mod": "!!", "filePath": "ignored.py"},
    ]
    assert status_list == expected
    assert item_count == 8


class TestGitAddFunctionality:
  """Test the 'gst -a' (git add) functionality."""

  def create_mock_tool_with_status(self, git_status_output):
    """Helper to create a GitStatusTool with mocked status."""
    tool = gst.GitStatusTool()
    # Mock the status list based on git output
    status_list = []
    for line in git_status_output.split("\n"):
      if line.strip():
        file_path = line[3:].split(" -> ")[-1]  # handle renamed case
        status_list.append({"mod": line[0:2], "filePath": file_path})
    tool._status_list = status_list
    tool._item_count = len(status_list) - 1
    return tool

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0"])
  def test_add_single_modified_file(self, mock_bash):
    """Test adding a single modified file."""
    # Mock git status output
    mock_bash.side_effect = [
      (b"M  modified.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git add call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called with the modified file
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "add", "modified.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0"])
  def test_add_single_deleted_file(self, mock_bash):
    """Test adding a single deleted file."""
    # Mock git status output
    mock_bash.side_effect = [
      (b"D  deleted.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git add call for deleted file
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called with the deleted file
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "add", "deleted.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0,1"])
  def test_add_mixed_files_no_deleted(self, mock_bash):
    """Test adding mixed files with no deleted files."""
    # Mock git status output
    mock_bash.side_effect = [
      (b"M  modified.py\nA  added.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git add call for non-deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called with both files in one call
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "add", "modified.py", "added.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0,1"])
  def test_add_mixed_files_with_deleted(self, mock_bash):
    """Test adding mixed files including deleted files."""
    # Mock git status output
    mock_bash.side_effect = [
      (b"M  modified.py\nD  deleted.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git add call for non-deleted files
      (b"", b""),  # git add call for deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called separately for non-deleted and deleted files
    assert mock_bash.call_count == 4
    mock_bash.assert_any_call(["git", "add", "modified.py"])
    mock_bash.assert_any_call(["git", "add", "deleted.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0,1,2"])
  def test_add_multiple_deleted_files(self, mock_bash):
    """Test adding multiple deleted files."""
    # Mock git status output
    mock_bash.side_effect = [
      (
        b"D  deleted1.py\nD  deleted2.py\nD  deleted3.py\n",
        b"",
      ),  # _generate_status_list call
      (b"", b""),  # git add call for deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called with all deleted files
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(
      ["git", "add", "deleted1.py", "deleted2.py", "deleted3.py"]
    )

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0:2"])
  def test_add_range_with_mixed_deleted_status(self, mock_bash):
    """Test adding a range that includes both deleted and non-deleted files."""
    # Mock git status output
    mock_bash.side_effect = [
      (
        b"M  modified.py\nD  deleted.py\nA  added.py\n",
        b"",
      ),  # _generate_status_list call
      (b"", b""),  # git add call for non-deleted files
      (b"", b""),  # git add call for deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called separately for non-deleted and deleted files
    assert mock_bash.call_count == 4
    mock_bash.assert_any_call(["git", "add", "modified.py", "added.py"])
    mock_bash.assert_any_call(["git", "add", "deleted.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0,1,2"])
  def test_add_various_deletion_types(self, mock_bash):
    """Test adding files with various deletion indicators."""
    # Mock git status output with different deletion patterns
    mock_bash.side_effect = [
      (
        b"D  deleted_staged.py\n D deleted_working.py\nDD deleted_both.py\n",
        b"",
      ),  # _generate_status_list call
      (b"", b""),  # git add call for deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called with all files containing 'D'
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(
      ["git", "add", "deleted_staged.py", "deleted_working.py", "deleted_both.py"]
    )

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0,1,2,3"])
  def test_add_complex_mixed_scenario(self, mock_bash):
    """Test adding a complex mix of file statuses."""
    # Mock git status output
    mock_bash.side_effect = [
      (
        b"M  modified.py\nD  deleted.py\nA  added.py\n?? untracked.py\n",
        b"",
      ),  # _generate_status_list call
      (b"", b""),  # git add call for non-deleted files
      (b"", b""),  # git add call for deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git add was called separately for non-deleted and deleted files
    assert mock_bash.call_count == 4
    mock_bash.assert_any_call(["git", "add", "modified.py", "added.py", "untracked.py"])
    mock_bash.assert_any_call(["git", "add", "deleted.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0"])
  def test_add_only_deleted_files_no_non_deleted(self, mock_bash):
    """Test adding when only deleted files are selected."""
    # Mock git status output
    mock_bash.side_effect = [
      (b"D  deleted.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git add call for deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify only one git add call was made (for deleted files)
    assert mock_bash.call_count == 3
    # Should not call git add with empty non-deleted list
    git_add_calls = [
      call
      for call in mock_bash.call_args_list
      if len(call[0]) > 0
      and call[0][0][0] == "git"
      and len(call[0][0]) > 1
      and call[0][0][1] == "add"
    ]
    assert len(git_add_calls) == 1
    mock_bash.assert_any_call(["git", "add", "deleted.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-a", "0"])
  def test_add_only_non_deleted_files(self, mock_bash):
    """Test adding when only non-deleted files are selected."""
    # Mock git status output
    mock_bash.side_effect = [
      (b"M  modified.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git add call for non-deleted files
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify only one git add call was made (for non-deleted files)
    assert mock_bash.call_count == 3
    # Should not call git add with empty deleted list
    git_add_calls = [
      call
      for call in mock_bash.call_args_list
      if len(call[0]) > 0
      and call[0][0][0] == "git"
      and len(call[0][0]) > 1
      and call[0][0][1] == "add"
    ]
    assert len(git_add_calls) == 1
    mock_bash.assert_any_call(["git", "add", "modified.py"])


class TestGitDiffFunctionality:
  """Test the 'gst -d' (git diff) functionality."""

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-d", "0"])
  def test_diff_single_file(self, mock_bash):
    """Test viewing diff for a single file."""
    diff_output = b"""diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 def hello():
+    print("world")
     return "hello"
"""
    mock_bash.side_effect = [
      (b"M  test.py\n", b""),  # _generate_status_list call
      (diff_output, b""),  # git diff call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git diff was called with the correct file
    assert mock_bash.call_count == 2
    mock_bash.assert_any_call(["git", "diff", "HEAD", "test.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-d", "1"])
  def test_diff_with_complex_path(self, mock_bash):
    """Test viewing diff for a file with complex path."""
    mock_bash.side_effect = [
      (b"M  src/utils/helper.py\nA  test.py\n", b""),  # _generate_status_list call
      (b"diff output here", b""),  # git diff call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git diff was called with the correct file (index 1)
    assert mock_bash.call_count == 2
    mock_bash.assert_any_call(["git", "diff", "HEAD", "test.py"])


class TestGitResetFunctionality:
  """Test the 'gst -r' (git reset) functionality."""

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-r", "0"])
  def test_reset_single_file(self, mock_bash):
    """Test resetting a single staged file."""
    mock_bash.side_effect = [
      (b"M  staged.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git reset call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git reset was called with the staged file
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "reset", "HEAD", "staged.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-r", "0,2"])
  def test_reset_multiple_files(self, mock_bash):
    """Test resetting multiple staged files."""
    mock_bash.side_effect = [
      (b"M  file1.py\nA  file2.py\nM  file3.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git reset call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git reset was called with multiple files
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "reset", "HEAD", "file1.py", "file3.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-r", "1:3"])
  def test_reset_range_of_files(self, mock_bash):
    """Test resetting a range of files."""
    mock_bash.side_effect = [
      (
        b"M  file0.py\nA  file1.py\nM  file2.py\nD  file3.py\n",
        b"",
      ),  # _generate_status_list call
      (b"", b""),  # git reset call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git reset was called with range of files (index 1, 2, 3)
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(
      ["git", "reset", "HEAD", "file1.py", "file2.py", "file3.py"]
    )


class TestGitDeleteFunctionality:
  """Test the 'gst -D' (rm) functionality."""

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-D", "0"])
  def test_delete_single_file(self, mock_bash):
    """Test deleting a single file."""
    mock_bash.side_effect = [
      (b"?? unwanted.py\n", b""),  # _generate_status_list call
      (b"", b""),  # rm call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify rm was called with the file
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["rm", "-r", "unwanted.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-D", "0,1"])
  def test_delete_multiple_files(self, mock_bash):
    """Test deleting multiple files."""
    mock_bash.side_effect = [
      (b"?? file1.tmp\n?? file2.tmp\n", b""),  # _generate_status_list call
      (b"", b""),  # rm call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify rm was called with both files
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["rm", "-r", "file1.tmp", "file2.tmp"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-D", "0"])
  def test_delete_directory(self, mock_bash):
    """Test deleting a directory."""
    mock_bash.side_effect = [
      (b"?? build/\n", b""),  # _generate_status_list call
      (b"", b""),  # rm call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify rm -r was called (which handles directories)
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["rm", "-r", "build/"])


class TestGitCheckoutFunctionality:
  """Test the 'gst -c' (git checkout) functionality."""

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-c", "0"])
  def test_checkout_single_file(self, mock_bash):
    """Test checking out a single modified file."""
    mock_bash.side_effect = [
      (b" M modified.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git checkout call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git checkout was called with the modified file
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "checkout", "HEAD", "modified.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-c", "0,1"])
  def test_checkout_multiple_files(self, mock_bash):
    """Test checking out multiple modified files."""
    mock_bash.side_effect = [
      (b" M file1.py\n M file2.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git checkout call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git checkout was called with both files
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "checkout", "HEAD", "file1.py", "file2.py"])

  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-c", "1:"])
  def test_checkout_unbounded_range(self, mock_bash):
    """Test checking out files using unbounded range."""
    mock_bash.side_effect = [
      (b" M file0.py\n M file1.py\n M file2.py\n", b""),  # _generate_status_list call
      (b"", b""),  # git checkout call
      (b"", b""),  # _display_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify git checkout was called with files 1 and 2 (unbounded from 1)
    assert mock_bash.call_count == 3
    mock_bash.assert_any_call(["git", "checkout", "HEAD", "file1.py", "file2.py"])


class TestGitEditFunctionality:
  """Test the 'gst -e' (editor) functionality."""

  @patch("gst.open_in_editor")
  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-e", "0"])
  def test_edit_single_file(self, mock_bash, mock_open_editor):
    """Test opening a single file in editor."""
    mock_bash.side_effect = [
      (b"M  script.py\n", b""),  # _generate_status_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify open_in_editor was called with the correct file
    assert mock_bash.call_count == 1
    mock_open_editor.assert_called_once_with("script.py")

  @patch("gst.open_in_editor")
  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-e", "2"])
  def test_edit_file_with_complex_path(self, mock_bash, mock_open_editor):
    """Test opening a file with complex path in editor."""
    mock_bash.side_effect = [
      (
        b"M  file1.py\nA  file2.py\n?? src/utils/helper.py\n",
        b"",
      ),  # _generate_status_list call
    ]

    tool = gst.GitStatusTool()
    tool.run()

    # Verify open_in_editor was called with the correct file (index 2)
    assert mock_bash.call_count == 1
    mock_open_editor.assert_called_once_with("src/utils/helper.py")

  @patch("os.environ.get")
  @patch("subprocess.run")
  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-e", "0"])
  def test_edit_with_visual_editor(self, mock_bash, mock_subprocess, mock_env):
    """Test opening file with VISUAL environment variable set."""
    mock_bash.side_effect = [
      (b"M  test.py\n", b""),  # _generate_status_list call
    ]
    mock_env.side_effect = lambda var: "code" if var == "VISUAL" else None

    tool = gst.GitStatusTool()
    tool.run()

    # Verify subprocess.run was called with the VISUAL editor
    assert mock_bash.call_count == 1
    mock_subprocess.assert_called_once_with(["code", "test.py"])

  @patch("os.environ.get")
  @patch("subprocess.run")
  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-e", "0"])
  def test_edit_with_editor_fallback(self, mock_bash, mock_subprocess, mock_env):
    """Test opening file with EDITOR environment variable as fallback."""
    mock_bash.side_effect = [
      (b"M  test.py\n", b""),  # _generate_status_list call
    ]
    # VISUAL returns None, EDITOR returns vim
    mock_env.side_effect = lambda var: "vim" if var == "EDITOR" else None

    tool = gst.GitStatusTool()
    tool.run()

    # Verify subprocess.run was called with the EDITOR fallback
    assert mock_bash.call_count == 1
    mock_subprocess.assert_called_once_with(["vim", "test.py"])

  @patch("gst.LOGGER")
  @patch("os.environ.get")
  @patch("gst.bash")
  @patch("sys.argv", ["gst", "-e", "0"])
  def test_edit_no_editor_found(self, mock_bash, mock_env, mock_logger):
    """Test behavior when no editor is found."""
    mock_bash.side_effect = [
      (b"M  test.py\n", b""),  # _generate_status_list call
    ]
    mock_env.return_value = None  # No VISUAL or EDITOR set

    tool = gst.GitStatusTool()
    tool.run()

    # Verify warning message was logged
    assert mock_bash.call_count == 1
    mock_logger.info.assert_called_once()
    # Check that the logged message contains the "No default editor found" text
    call_args = mock_logger.info.call_args[0][0]
    assert "No default editor found" in call_args


if __name__ == "__main__":
  pytest.main([__file__])
