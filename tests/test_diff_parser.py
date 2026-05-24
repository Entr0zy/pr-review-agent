from pr_review_agent.diff_parser import parse_unified_diff

SAMPLE = """diff --git a/foo.py b/foo.py
index e69de29..a1b2c3d 100644
--- a/foo.py
+++ b/foo.py
@@ -1,3 +1,4 @@
 import os
+import sys
 def f():
-    return 1
+    return 2
"""


def test_parses_single_file():
    files = parse_unified_diff(SAMPLE)
    assert len(files) == 1
    assert files[0].path == "foo.py"


def test_added_line_numbers():
    fd = parse_unified_diff(SAMPLE)[0]
    added = [(ln.new_lineno, ln.content) for ln in fd.added_lines]
    assert added == [(2, "import sys"), (4, "    return 2")]


def test_deletions_have_no_new_lineno():
    fd = parse_unified_diff(SAMPLE)[0]
    dels = [ln for ln in fd.lines if ln.kind == "del"]
    assert len(dels) == 1
    assert dels[0].new_lineno is None
    assert dels[0].content == "    return 1"


def test_multiple_files():
    diff = SAMPLE + (
        "diff --git a/bar.py b/bar.py\n"
        "--- a/bar.py\n"
        "+++ b/bar.py\n"
        "@@ -0,0 +1,1 @@\n"
        "+x = 1\n"
    )
    files = parse_unified_diff(diff)
    assert [f.path for f in files] == ["foo.py", "bar.py"]
    assert files[1].added_lines[0].new_lineno == 1
