import sys
import subprocess
from pathlib import Path

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main as api
import luminark_live_bridge as bridge_module
from luminark_live_bridge import ExecutionMode, LuminarkLiveBridge


def test_api_auth_fails_closed_without_configured_key(monkeypatch):
    monkeypatch.setattr(api, "CODEWRITER_API_KEY", None)
    monkeypatch.setattr(api, "CODEWRITER_DEMO_KEY", None)
    with pytest.raises(HTTPException) as exc:
        api.verify_api_key("x" * 40)
    assert exc.value.status_code == 503


def test_api_auth_rejects_short_key(monkeypatch):
    monkeypatch.setattr(api, "CODEWRITER_API_KEY", "short")
    monkeypatch.setattr(api, "CODEWRITER_DEMO_KEY", None)
    with pytest.raises(HTTPException) as exc:
        api.verify_api_key("short")
    assert exc.value.status_code == 503


def test_api_auth_accepts_explicit_strong_key(monkeypatch):
    key = "a" * 40
    monkeypatch.setattr(api, "CODEWRITER_API_KEY", key)
    monkeypatch.setattr(api, "CODEWRITER_DEMO_KEY", None)
    monkeypatch.setattr(api, "ENVIRONMENT", "development")
    assert api.verify_api_key(key) == key


def test_demo_key_is_not_accepted_in_production(monkeypatch):
    monkeypatch.setattr(api, "CODEWRITER_API_KEY", "a" * 40)
    monkeypatch.setattr(api, "CODEWRITER_DEMO_KEY", "b" * 40)
    monkeypatch.setattr(api, "ENVIRONMENT", "production")
    with pytest.raises(HTTPException) as exc:
        api.verify_api_key("b" * 40)
    assert exc.value.status_code == 401


def test_local_execution_mode_is_rejected_in_production(monkeypatch):
    monkeypatch.setattr(api, "EXEC_MODE", "local")
    monkeypatch.setattr(api, "ENVIRONMENT", "production")
    monkeypatch.setattr(api, "_bridge", None)
    with pytest.raises(RuntimeError, match="only in development"):
        api._get_bridge()


def test_docker_mode_fails_closed_when_docker_executable_is_missing(monkeypatch):
    bridge = LuminarkLiveBridge(execution_mode=ExecutionMode.DOCKER)

    def docker_missing(*args, **kwargs):
        raise FileNotFoundError("docker executable missing")

    def should_not_run_locally(*args, **kwargs):
        raise AssertionError("Docker mode must never fall back to host execution")

    monkeypatch.setattr(bridge_module.subprocess, "run", docker_missing)
    monkeypatch.setattr(bridge, "_execute_local", should_not_run_locally)

    result = bridge._execute_docker("print('untrusted')")
    assert result.exit_code == 127
    assert "Refusing to execute" in result.stderr


def test_docker_execution_includes_hardening_flags(monkeypatch):
    bridge = LuminarkLiveBridge(execution_mode=ExecutionMode.DOCKER)
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(bridge_module.subprocess, "run", fake_run)
    result = bridge._execute_docker("print('sandboxed')")
    assert result.success
    command = captured["command"]
    for flag in (
        "--network", "none", "--read-only", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges:true", "--user", "1001:1001",
        "--pids-limit", "64",
    ):
        assert flag in command


def test_govern_request_limits_code_size_and_context_id():
    with pytest.raises(ValidationError):
        api.GovernRequest(code="x", context_id="invalid:context")
    with pytest.raises(ValidationError):
        api.GovernRequest(code="x" * 100_001)
