from pr_review_agent.adapters import gitlab_mcp


class FakeHTTPParams:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeToolset:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def _fake_adk():
    return FakeAgent, FakeToolset, FakeHTTPParams


def test_build_agent_uses_gitlab_mcp_and_gemini_3(monkeypatch):
    monkeypatch.setattr(gitlab_mcp, "_import_adk", _fake_adk)

    agent = gitlab_mcp.build_agent()
    toolset = agent.kwargs["tools"][0]
    params = toolset.kwargs["connection_params"]

    assert agent.kwargs["model"] == "gemini-3-pro-preview"
    assert params.kwargs["url"] == "https://gitlab.com/api/v4/mcp"
    assert params.kwargs["headers"] == {
        "X-Gitlab-Mcp-Server-Tool-Name-Prefix": "gitlab_"
    }
    assert "explicit user approval" in agent.kwargs["instruction"]


def test_build_agent_reads_deployment_environment(monkeypatch):
    monkeypatch.setattr(gitlab_mcp, "_import_adk", _fake_adk)
    monkeypatch.setenv("PR_REVIEW_MODEL", "gemini-3-flash-preview")
    monkeypatch.setenv("GITLAB_MCP_URL", "https://gitlab.example/api/v4/mcp")
    monkeypatch.setenv("GITLAB_MCP_TOOL_PREFIX", "company_")
    monkeypatch.setenv("GITLAB_MCP_AUTH_TOKEN", "oauth-token")

    agent = gitlab_mcp.build_agent()
    params = agent.kwargs["tools"][0].kwargs["connection_params"]

    assert agent.kwargs["model"] == "gemini-3-flash-preview"
    assert params.kwargs["url"] == "https://gitlab.example/api/v4/mcp"
    assert params.kwargs["headers"][
        "X-Gitlab-Mcp-Server-Tool-Name-Prefix"
    ] == "company_"
    assert params.kwargs["headers"]["Authorization"] == "Bearer oauth-token"
