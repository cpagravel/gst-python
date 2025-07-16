#!/usr/bin/env python3
"""
Integration tests for gst.py that use actual git commands.

These tests create temporary git repositories to test real git interactions
without mocking. Compatible with Python 3.6+.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from typing import Dict, List

# Import the module under test
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gst


class GitStatusToolForTesting(gst.GitStatusTool):
  """
  Test-specific subclass of GitStatusTool that handles directory management.

  This makes testing much cleaner by encapsulating the directory changes
  and providing a simple interface for running gst commands in test repos.
  """

  def __init__(self, repo_path: str):
    """
    Initialize the test tool for a specific repository.

    Args:
      repo_path: Path to the git repository to operate in
    """
    self.repo_path = repo_path
    self.original_cwd = os.getcwd()
    super().__init__()

  def run_with_args(self, args_list=None):
    """
    Run gst with arguments in the test repository.

    Args:
      args_list: List of command line arguments, or None for empty args

    Returns:
      Self for method chaining or inspection
    """
    original_cwd = os.getcwd()
    try:
      os.chdir(self.repo_path)
      return super().run_with_args(args_list)
    finally:
      os.chdir(original_cwd)

  def run(self, args_string: str = ""):
    """
    Convenience method to run gst with CLI-style string arguments.

    Args:
      args_string: CLI arguments as string (e.g. "-a 0,1" or "-r 2:4")

    Returns:
      Self for method chaining or inspection
    """
    if args_string.strip():
      args_list = args_string.split()
    else:
      args_list = []

    return self.run_with_args(args_list)


class GitIntegrationTestCase(unittest.TestCase):
  """Base class for git integration tests with helper methods."""

  @contextmanager
  def temp_git_repo(self):
    """
    Context manager that creates a temporary git repository.

    Yields the path to the temporary repository directory.
    Automatically cleans up when done.
    """
    # Use tempfile.mkdtemp() for Python 3.6 compatibility
    # (TemporaryDirectory context manager is available but this is more explicit)
    temp_dir = tempfile.mkdtemp(prefix="gst_test_")

    try:
      # Initialize git repo
      self._run_git_command(["git", "init"], cwd=temp_dir)

      # Configure git user for commits (required for some operations)
      self._run_git_command(["git", "config", "user.name", "Test User"], cwd=temp_dir)
      self._run_git_command(
        ["git", "config", "user.email", "test@example.com"], cwd=temp_dir
      )

      yield temp_dir
    finally:
      # Clean up
      shutil.rmtree(temp_dir, ignore_errors=True)

  def _run_git_command(self, command: List[str], cwd: str):
    """Run a git command in the specified directory."""
    # Use subprocess.PIPE for Python 3.6 compatibility (capture_output added in 3.7)
    result = subprocess.run(
      command,
      cwd=cwd,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      universal_newlines=True,  # Use universal_newlines instead of text for 3.6
      check=False,  # Don't raise on non-zero exit
    )
    return result

  def _create_file(
    self, repo_path: str, filename: str, content: str = "test content"
  ) -> str:
    """Create a file with content in the repo directory."""
    file_path = os.path.join(repo_path, filename)

    # Ensure parent directory exists
    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
      os.makedirs(parent_dir)

    with open(file_path, "w") as f:
      f.write(content)

    return file_path

  def _delete_file(self, repo_path: str, filename: str):
    """Delete a file from the repo directory."""
    file_path = os.path.join(repo_path, filename)
    if os.path.exists(file_path):
      os.remove(file_path)

  def setup_git_state(self, repo_path: str, config: Dict[str, List[str]]):
    """
    Set up a git repository in a specific state.

    Args:
      repo_path: Path to the git repository
      config: Dictionary defining the desired state:
        - 'committed_files': Files to create and commit
        - 'modified_files': Files to modify after committing
        - 'new_files': New untracked files to create
        - 'deleted_files': Committed files to delete
        - 'staged_files': Files to stage (in addition to initial commit)
    """
    # First, create and commit any base files
    committed_files = config.get("committed_files", [])
    for filename in committed_files:
      self._create_file(repo_path, filename, f"Initial content for {filename}")

    if committed_files:
      self._run_git_command(["git", "add"] + committed_files, cwd=repo_path)
      self._run_git_command(["git", "commit", "-m", "Initial commit"], cwd=repo_path)

    # Create modified files (modify existing committed files)
    modified_files = config.get("modified_files", [])
    for filename in modified_files:
      if filename not in committed_files:
        # File wasn't committed yet, create and commit it first
        self._create_file(repo_path, filename, f"Initial content for {filename}")
        self._run_git_command(["git", "add", filename], cwd=repo_path)
        self._run_git_command(["git", "commit", "-m", f"Add {filename}"], cwd=repo_path)

      # Now modify it
      self._create_file(repo_path, filename, f"Modified content for {filename}")

    # Create new untracked files
    new_files = config.get("new_files", [])
    for filename in new_files:
      self._create_file(repo_path, filename, f"New file content for {filename}")

    # Delete committed files
    deleted_files = config.get("deleted_files", [])
    for filename in deleted_files:
      if filename not in committed_files:
        # File wasn't committed yet, create and commit it first
        self._create_file(repo_path, filename, f"Content for {filename}")
        self._run_git_command(["git", "add", filename], cwd=repo_path)
        self._run_git_command(["git", "commit", "-m", f"Add {filename}"], cwd=repo_path)

      # Now delete it
      self._delete_file(repo_path, filename)

    # Stage additional files
    staged_files = config.get("staged_files", [])
    if staged_files:
      self._run_git_command(["git", "add"] + staged_files, cwd=repo_path)

  def get_git_status_dict(self, repo_path: str) -> Dict[str, List[str]]:
    """
    Get git status as a dictionary for easy assertions.

    Returns:
      Dictionary with keys like 'staged', 'modified', 'untracked', 'deleted'
    """
    result = self._run_git_command(["git", "status", "-s"], cwd=repo_path)

    status_dict: Dict[str, List[str]] = {
      "staged": [],
      "modified": [],
      "untracked": [],
      "deleted": [],
      "staged_deleted": [],
    }

    for line in result.stdout.split("\n"):
      if not line.strip():
        continue

      # Parse git status -s format
      # Format: XY filename where X=staged, Y=working tree
      if len(line) < 3:
        continue

      staged_status = line[0]
      working_status = line[1]
      filename = line[3:]  # Skip the two status chars and the space

      # Handle staged changes
      if staged_status == "A":
        status_dict["staged"].append(filename)
      elif staged_status == "D":
        status_dict["staged_deleted"].append(filename)
      elif staged_status == "M":
        status_dict["staged"].append(filename)

      # Handle working tree changes
      if working_status == "M":
        status_dict["modified"].append(filename)
      elif working_status == "D":
        status_dict["deleted"].append(filename)
      elif working_status == "?" and staged_status == "?":
        # Both chars are '?' for untracked files
        status_dict["untracked"].append(filename)

    return status_dict

  def assert_git_status(self, repo_path: str, expected: Dict[str, List[str]]):
    """Assert that git status matches expected state."""
    actual = self.get_git_status_dict(repo_path)

    for key, expected_files in expected.items():
      actual_files = actual.get(key, [])
      self.assertEqual(
        sorted(expected_files),
        sorted(actual_files),
        f"Git status mismatch for '{key}': expected {expected_files}, "
        f"got {actual_files}",
      )


class TestGitIntegration(GitIntegrationTestCase):
  """Integration tests for gst.py git operations."""

  def test_mixed_file_operations_setup(self):
    """Test that our git repo setup helpers work correctly."""
    with self.temp_git_repo() as repo_path:
      # Set up a complex git state
      self.setup_git_state(
        repo_path,
        {
          "committed_files": ["existing.py"],
          "modified_files": ["existing.py"],
          "new_files": ["new_file.txt"],
          "deleted_files": ["old_file.txt"],
        },
      )

      # Verify the state was set up correctly
      status = self.get_git_status_dict(repo_path)

      # Should have one modified file, one new file, one deleted file
      self.assertIn("existing.py", status["modified"])
      self.assertIn("new_file.txt", status["untracked"])
      self.assertIn("old_file.txt", status["deleted"])

  def test_git_status_parsing(self):
    """Test that we can correctly parse git status output."""
    with self.temp_git_repo() as repo_path:
      # Create a simple test scenario
      self._create_file(repo_path, "test.txt", "content")
      self._run_git_command(["git", "add", "test.txt"], cwd=repo_path)

      status = self.get_git_status_dict(repo_path)
      self.assertIn("test.txt", status["staged"])

  def test_simple_gst_operations(self):
    """
    Simple examples showing how clean and readable gst testing can be now.
    """
    with self.temp_git_repo() as repo_path:
      # Set up some files
      self.setup_git_state(
        repo_path,
        {
          "committed_files": ["file1.txt", "file2.txt"],
          "modified_files": ["file1.txt"],
          "new_files": ["file3.txt"],
        },
      )

      # Create gst tool instance for this repo
      gst_tool = GitStatusToolForTesting(repo_path)

      # Test adding files: `gst -a 0,1`
      gst_tool.run("-a 0,1")
      self.assert_git_status(repo_path, {"staged": ["file1.txt", "file3.txt"]})

      # Test resetting files: `gst -r 0`
      gst_tool.run("-r 0")
      self.assert_git_status(
        repo_path, {"staged": ["file3.txt"], "modified": ["file1.txt"]}
      )

      # Test getting file reference: `gst 1`
      gst_tool.run("1")
      # The REF operation stores the result in the status list
      self.assertIn("file3.txt", gst_tool._status_list[1]["filePath"])

  def test_class_based_gst_testing(self):
    """
    Example showing the new class-based approach for even cleaner testing.
    """
    with self.temp_git_repo() as repo_path:
      # Set up some files
      self.setup_git_state(
        repo_path,
        {
          "committed_files": ["app.py", "utils.py"],
          "modified_files": ["app.py"],
          "new_files": ["test_app.py"],
        },
      )

      # Create a TestGitStatusTool instance for this repo
      gst_tool = GitStatusToolForTesting(repo_path)

      # Now we can use it very cleanly without passing repo_path every time
      gst_tool.run("-a 0")  # gst -a 0
      self.assert_git_status(
        repo_path, {"staged": ["app.py"], "untracked": ["test_app.py"]}
      )

      gst_tool.run("-a 1")  # gst -a 1
      self.assert_git_status(repo_path, {"staged": ["app.py", "test_app.py"]})

      gst_tool.run("-r 0")  # gst -r 0
      self.assert_git_status(
        repo_path, {"staged": ["test_app.py"], "modified": ["app.py"]}
      )

      # The tool instance retains state and can be inspected
      self.assertEqual(len(gst_tool._status_list), 2)
      self.assertIn("app.py", gst_tool._status_list[0]["filePath"])

  def test_add_mixed_deleted_and_new_files(self):
    """
    Integration test for adding both deleted and new files using gst.

    This tests the core functionality where gst splits deleted and non-deleted
    files into separate git add commands.
    """
    with self.temp_git_repo() as repo_path:
      # Set up a scenario with both deleted and new files
      self.setup_git_state(
        repo_path,
        {
          "committed_files": ["old_file.txt"],
          "new_files": ["new_file.txt"],
          "deleted_files": ["old_file.txt"],  # This will delete the committed file
        },
      )

      # Verify initial state
      self.assert_git_status(
        repo_path, {"deleted": ["old_file.txt"], "untracked": ["new_file.txt"]}
      )

      # Create gst tool instance for this repo
      gst_tool = GitStatusToolForTesting(repo_path)

      # First, let's see what the status list looks like to determine indices
      gst_tool.run("")  # Empty args to just generate status list
      status_list = gst_tool._status_list

      # Find indices for our files (gst sorts them so indices may vary)
      deleted_index = None
      new_index = None
      for i, item in enumerate(status_list):
        if "old_file.txt" in item["filePath"]:
          deleted_index = i
        elif "new_file.txt" in item["filePath"]:
          new_index = i

      # Verify we found both files in the status list
      self.assertIsNotNone(deleted_index, "Should find deleted file in gst status list")
      self.assertIsNotNone(new_index, "Should find new file in gst status list")

      # Now run gst with the add command using the actual indices
      gst_tool.run(f"-a {deleted_index},{new_index}")

      # Verify final state - both files should be staged
      self.assert_git_status(
        repo_path, {"staged": ["new_file.txt"], "staged_deleted": ["old_file.txt"]}
      )

      # Verify we can commit both changes
      commit_result = self._run_git_command(
        ["git", "commit", "-m", "Add new file and remove old file"], cwd=repo_path
      )
      self.assertEqual(
        commit_result.returncode, 0, f"Commit failed: {commit_result.stderr}"
      )

      # After commit, working directory should be clean
      self.assert_git_status(
        repo_path, {"staged": [], "staged_deleted": [], "untracked": [], "deleted": []}
      )

  def test_comprehensive_git_workflow(self):
    """
    Test a comprehensive git workflow using multiple gst operations.
    This shows how natural and readable the integration tests are now.
    """
    with self.temp_git_repo() as repo_path:
      # Set up a complex scenario
      self.setup_git_state(
        repo_path,
        {
          "committed_files": ["feature.py", "config.json", "docs.md"],
          "modified_files": ["feature.py", "config.json"],
          "new_files": ["test_feature.py"],
          "deleted_files": ["docs.md"],
        },
      )

      # Initial state should have mixed file types
      self.assert_git_status(
        repo_path,
        {
          "modified": ["feature.py", "config.json"],
          "untracked": ["test_feature.py"],
          "deleted": ["docs.md"],
        },
      )

      # Create gst tool instance for this repo
      gst_tool = GitStatusToolForTesting(repo_path)

      # Stage the new test file: `gst -a 3`
      gst_tool.run("-a 3")
      self.assert_git_status(
        repo_path,
        {
          "staged": ["test_feature.py"],
          "modified": ["feature.py", "config.json"],
          "deleted": ["docs.md"],
        },
      )

      # Add the modified files: `gst -a 0,2`
      gst_tool.run("-a 0,2")
      self.assert_git_status(
        repo_path,
        {
          "staged": ["config.json", "feature.py", "test_feature.py"],
          "deleted": ["docs.md"],
        },
      )

      # Reset the feature file: `gst -r 2`
      gst_tool.run("-r 2")
      self.assert_git_status(
        repo_path,
        {
          "staged": ["config.json", "test_feature.py"],
          "modified": ["feature.py"],
          "deleted": ["docs.md"],
        },
      )

      # Add the deleted file: `gst -a 1`
      gst_tool.run("-a 1")
      self.assert_git_status(
        repo_path,
        {
          "staged": ["config.json", "test_feature.py"],
          "staged_deleted": ["docs.md"],
          "modified": ["feature.py"],
        },
      )

      # Commit the staged changes
      commit_result = self._run_git_command(
        ["git", "commit", "-m", "Add test file, update config, remove docs"],
        cwd=repo_path,
      )
      self.assertEqual(commit_result.returncode, 0)

      # Final state should just have the modified file
      self.assert_git_status(repo_path, {"modified": ["feature.py"]})

  def test_gst_operations_from_subfolder(self):
    """
    Test that gst commands work correctly when run from a subfolder of the repo.

    This tests the scenario where:
    - We have files at the top level and in subfolders
    - We change CWD to a subfolder
    - We can still reference and operate on files at any level
    """
    with self.temp_git_repo() as repo_path:
      # Create the directory structure:
      # .
      # ├── subfolder/
      # │   └── subfile.txt
      # └── top_level_file.txt

      # Create subfolder and files
      subfolder_path = os.path.join(repo_path, "subfolder")
      os.makedirs(subfolder_path)

      self._create_file(repo_path, "top_level_file.txt", "content at top level")
      self._create_file(repo_path, "subfolder/subfile.txt", "content in subfolder")

      # Add files to git and commit
      self._run_git_command(["git", "add", "."], cwd=repo_path)
      self._run_git_command(["git", "commit", "-m", "Add test files"], cwd=repo_path)

      # Modify both files to create changes
      self._create_file(
        repo_path, "top_level_file.txt", "modified content at top level"
      )

      # Verify initial state from repo root
      self.assert_git_status(repo_path, {"modified": ["top_level_file.txt"]})

      # Create a GitStatusToolForTesting instance that operates from the subfolder
      gst_tool = GitStatusToolForTesting(subfolder_path)

      # Run gst from subfolder - should see both files
      gst_tool.run()
      status_list = gst_tool._status_list

      self.assertEqual(len(status_list), 1)

      # Delete the file at the top folder
      # This will only work if the tool can handle relative paths correctly
      gst_tool.run("-D 0")

      # Verify the file was deleted
      self.assertFalse(
        os.path.exists(os.path.join(repo_path, "top_level_file.txt")),
        "top_level_file.txt should be deleted",
      )

      self.assert_git_status(repo_path, {"deleted": ["top_level_file.txt"]})


if __name__ == "__main__":
  unittest.main()
