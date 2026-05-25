import hashlib
import hmac

from pr_review_agent.adapters.github_app import (
    extract_pr,
    should_review,
    verify_signature,
)


def _sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_verify_signature_accepts_valid():
    body, secret = b'{"a":1}', "topsecret"
    assert verify_signature(body, secret, _sign(body, secret))


def test_verify_signature_rejects_bad_and_missing():
    assert not verify_signature(b"{}", "s", "sha256=deadbeef")
    assert not verify_signature(b"{}", "s", None)
    assert not verify_signature(b"{}", "s", "md5=whatever")
    # wrong secret
    assert not verify_signature(b"{}", "s", _sign(b"{}", "other"))


def test_extract_pr_fields():
    payload = {
        "action": "opened",
        "pull_request": {"number": 7, "diff_url": "u", "html_url": "h"},
        "repository": {"full_name": "octo/repo"},
    }
    info = extract_pr(payload)
    assert info == {
        "action": "opened",
        "owner": "octo",
        "repo": "repo",
        "number": 7,
        "diff_url": "u",
        "html_url": "h",
    }


def test_extract_pr_none_for_non_pr_event():
    assert extract_pr({"action": "push"}) is None


def test_should_review_gates_actions():
    assert should_review({"action": "opened"})
    assert should_review({"action": "synchronize"})
    assert not should_review({"action": "labeled"})
