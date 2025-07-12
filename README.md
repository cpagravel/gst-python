# gst [![MIT License][license-badge]](LICENSE.md)

## Synposis
gst is short for **G**it **St**atus - it's a commandline app with some neat features for improving your workflow with git
Note that gst is meant for in dark themed terminals

## Usage
Note that the output is colorized in the terminal and intended for a dark themed terminal. It doesn't show here - waiting for colorized text in Github markdown (re: https://github.com/github/markup/issues/369).
```
$ gst # Show status of repository
#   INDEX     CUR_TREE  FILE
0   Untrackd  Untrackd  LICENSE.md (0)
1             Modified  colors.py (1)
2   Untrackd  Untrackd  dist/ (2)

$ gst -a 0,1 # Add a file[s]/stage changes
#   INDEX     CUR_TREE  FILE
0   Added               LICENSE.md (0)
1   Modified            colors.py (1)
2   Untrackd  Untrackd  dist/ (2)

$ gst -r 1 # reset staged changes
#   INDEX     CUR_TREE  FILE
0   Added               LICENSE.md (0)
1             Modified  colors.py (1)
2   Untrackd  Untrackd  dist/ (2)

$ gst -d 1 # view changes of a file
diff --git a/colors.py b/colors.py
index e697793..295fbeb 100644
--- a/colors.py
+++ b/colors.py
@@ -1,3 +1,4 @@
 class Colors(object):
+    BLUE        = '\033[1;34m'
     BOLD        = '\033[;1m'

$ gst -c 1 # checkout file to revert changes
#   INDEX     CUR_TREE  FILE
0   Added               LICENSE.md (0)
1   Untrackd  Untrackd  dist/ (1)

$ gst -D 1 # delete a file
#   INDEX     CUR_TREE  FILE
0   Added               LICENSE.md (0)

$ gst -e 1 # open file in default editor
```

## Installation
Install from pip.
```
pip install gst
```

## Compatability
- Linux, Mac, Windows
- Git version >2
- Python3 (re: https://pythonclock.org/)

## TODO
- Use a class and get rid of globals (parser, item_count)
- Upload pictures to show colored text (or wish harder for github to support it)

## License MIT
[View project License](LICENSE.md).

[license-badge]: https://img.shields.io/badge/license-MIT-007EC7.svg
