import contextlib
import io
import json

from pr_review_agent.cli import main

DIFF = (
    'diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n'
    '@@ -0,0 +1,1 @@\n+password = "x"\n'
)


def _write(tmp_path):
    p = tmp_path / "d.diff"
    p.write_text(DIFF, encoding="utf-8")
    return str(p)


def test_cli_text_blocks_on_high(tmp_path, capsys):
    code = main([_write(tmp_path), "--mock"])
    out = capsys.readouterr().out
    assert "CRITICAL" in out
    assert code == 1  # critical >= default fail-on=high


def test_cli_json_output(tmp_path):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main([_write(tmp_path), "--mock", "--format", "json", "--fail-on", "none"])
    data = json.loads(buf.getvalue())
    assert data["has_blocking"] is True


def test_cli_fail_on_none_exits_zero(tmp_path):
    assert main([_write(tmp_path), "--mock", "--fail-on", "none"]) == 0


def test_cli_markdown(tmp_path, capsys):
    main([_write(tmp_path), "--mock", "--format", "markdown", "--fail-on", "none"])
    assert "## PR Review" in capsys.readouterr().out
