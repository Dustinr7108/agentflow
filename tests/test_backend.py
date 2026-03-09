"""Backend tests for AgentFlow."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create test client with mocked DB."""
    import sys
    # Mock DB before importing app
    mock_db = MagicMock()
    mock_session = MagicMock()
    mock_session_local = MagicMock(return_value=mock_session)

    with patch.dict("os.environ", {
        "DATABASE_URL": "sqlite:///./test.db",
        "REDIS_URL": "redis://localhost:6379/0",
        "SECRET_KEY": "test-secret-key-for-testing-only",
    }):
        from app.main import app
        client = TestClient(app, raise_server_exceptions=False)
        yield client


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_register(client):
    res = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
    })
    # 200 = success, 400 = already exists (re-run)
    assert res.status_code in (200, 400)


def test_login_invalid(client):
    res = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    })
    assert res.status_code == 401


def test_protected_without_token(client):
    res = client.get("/workflows/")
    assert res.status_code in (401, 403)


def test_protected_with_bad_token(client):
    res = client.get("/workflows/", headers={"Authorization": "Bearer bad-token"})
    assert res.status_code in (401, 403)


class TestWorkflowEngine:
    """Test the workflow execution engine directly."""

    def test_empty_graph(self):
        from app.workflows.engine import WorkflowEngine
        engine = WorkflowEngine(graph={"nodes": [], "edges": []}, agent_defs={})
        result = engine.run(input_data={})
        assert result["status"] == "completed"
        assert result["total_tokens"] == 0

    def test_conditional_agent_true_branch(self):
        from app.agents.conditional_agent import ConditionalAgent
        agent = ConditionalAgent(config={
            "field": "count",
            "operator": "gt",
            "value": "5",
        })
        result_obj = agent.run("check", {"count": 10})
        result = result_obj.output if hasattr(result_obj, "output") else result_obj
        assert result.get("branch") == "true"

    def test_conditional_agent_false_branch(self):
        from app.agents.conditional_agent import ConditionalAgent
        agent = ConditionalAgent(config={
            "field": "count",
            "operator": "gt",
            "value": "5",
        })
        result_obj = agent.run("check", {"count": 3})
        result = result_obj.output if hasattr(result_obj, "output") else result_obj
        assert result.get("branch") == "false"

    def test_data_transform_passthrough(self):
        from app.agents.data_transform_agent import DataTransformAgent
        agent = DataTransformAgent(config={"operation": "passthrough"})
        result_obj = agent.run("transform", {"key": "value"})
        result = result_obj.output if hasattr(result_obj, "output") else result_obj
        assert result["key"] == "value"

    def test_data_transform_extract_field(self):
        from app.agents.data_transform_agent import DataTransformAgent
        agent = DataTransformAgent(config={"operation": "extract_field", "field": "name"})
        result_obj = agent.run("extract", {"name": "Alice", "age": 30})
        result = result_obj.output if hasattr(result_obj, "output") else result_obj
        assert result["value"] == "Alice"

    def test_code_exec_basic(self):
        from app.agents.code_exec_agent import CodeExecAgent
        agent = CodeExecAgent(config={"code": "result = 2 + 2"})
        result_obj = agent.run("execute", {})
        result = result_obj.output if hasattr(result_obj, "output") else result_obj
        assert result.get("result") == 4

    def test_code_exec_with_input(self):
        from app.agents.code_exec_agent import CodeExecAgent
        agent = CodeExecAgent(config={"code": "result = input_data['x'] * 2"})
        result_obj = agent.run("execute", {"x": 5})
        result = result_obj.output if hasattr(result_obj, "output") else result_obj
        assert result.get("result") == 10


class TestAuth:
    """Test auth functions directly."""

    def test_hash_verify_password(self):
        from app.auth import hash_password, verify_password
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_create_access_token(self):
        from app.auth import create_access_token
        import os
        os.environ.setdefault("SECRET_KEY", "test-secret")
        token = create_access_token("user-id-123", "user@example.com")
        assert isinstance(token, str)
        assert len(token) > 20


class TestBillingLogic:
    """Test billing plan limits."""

    def test_usage_limit_free(self):
        from app.auth import check_usage_limit
        from fastapi import HTTPException
        import pytest

        user = MagicMock()
        user.plan = "free"
        user.runs_this_month = 10

        with pytest.raises(HTTPException) as exc_info:
            check_usage_limit(user)
        assert exc_info.value.status_code == 429

    def test_usage_limit_not_reached(self):
        from app.auth import check_usage_limit

        user = MagicMock()
        user.plan = "free"
        user.runs_this_month = 5

        # Should not raise
        check_usage_limit(user)

    def test_usage_limit_pro(self):
        from app.auth import check_usage_limit

        user = MagicMock()
        user.plan = "pro"
        user.runs_this_month = 500

        # Should not raise for pro user
        check_usage_limit(user)
