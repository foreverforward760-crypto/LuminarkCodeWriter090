"""
main.py – LUMINARK Live Bridge FastAPI Service

HTTP API layer wrapping the LuminarkLiveBridge governance orchestrator.
Adds Redis telemetry for:
  - Lyapunov V-series storage (dV/dt monitoring)
  - Stage history per context
  - Metadata-only audit trail persistence (source code and diagnostics excluded)
  - Latest governance verdict per context

Endpoints:
  POST /govern          — run full governance loop on submitted code
  POST /stage-report    — quick SAP stage check (no governance loop)
  GET  /telemetry/{id}  — retrieve stored V-series + stage history for a context
  GET  /health          — liveness check

Environment variables:
  REDIS_URL             — Redis connection string (default: redis://redis:6379)
  LUMINARK_DOCKER_IMAGE — sandbox image name (default: luminark-sandbox:latest)
  LUMINARK_MAX_ITERATIONS — max repair iterations (default: 3)
  LUMINARK_MODE         — "docker" | "local" (default: docker)
  LUMINARK_STABILITY_THRESHOLD — Lyapunov V threshold (default: 3.0)

Start:
  uvicorn main:app --host 0.0.0.0 --port 8080
"""

import json
import logging
import os
import secrets
import shutil
import subprocess
from contextlib import asynccontextmanager, suppress

import redis
from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from luminark_live_bridge import (
    ExecutionMode,
    LuminarkLiveBridge,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ── Configuration from environment ────────────────────────────────────────────

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DOCKER_IMAGE = os.getenv("LUMINARK_DOCKER_IMAGE", "luminark-sandbox:latest")
MAX_ITERATIONS = int(os.getenv("LUMINARK_MAX_ITERATIONS", "3"))
TELEMETRY_TTL_SECONDS = max(
    60, min(int(os.getenv("LUMINARK_TELEMETRY_TTL_SECONDS", "604800")), 2_592_000)
)
EXEC_MODE = os.getenv("LUMINARK_MODE", "docker").lower()
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
STABILITY_THRESHOLD = float(os.getenv("LUMINARK_STABILITY_THRESHOLD", "3.0"))
CODEWRITER_API_KEY = os.getenv("CODEWRITER_API_KEY")
CODEWRITER_DEMO_KEY = os.getenv("CODEWRITER_DEMO_KEY")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# Redis key prefixes
_KEY_V_SERIES = "luminark:v_series:{ctx}"
_KEY_STAGE_SEQ = "luminark:stage_seq:{ctx}"
_KEY_AUDIT = "luminark:audit:{ctx}"
_KEY_LATEST = "luminark:latest:{ctx}"
_KEY_VERDICT_CTR = "luminark:verdicts:{verdict}"

# ── Auth ──────────────────────────────────────────────────────────────────────

def verify_api_key(x_codewriter_api_key: str | None = Header(None)) -> str:
    if not CODEWRITER_API_KEY or len(CODEWRITER_API_KEY) < 32:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured. Set CODEWRITER_API_KEY to a random secret of at least 32 characters.",
        )
    if CODEWRITER_DEMO_KEY and len(CODEWRITER_DEMO_KEY) < 32:
        raise HTTPException(
            status_code=503,
            detail="CODEWRITER_DEMO_KEY must be at least 32 characters when configured.",
        )
    valid_keys = [CODEWRITER_API_KEY]
    if ENVIRONMENT != "production" and CODEWRITER_DEMO_KEY:
        valid_keys.append(CODEWRITER_DEMO_KEY)
    if not x_codewriter_api_key or not any(
        secrets.compare_digest(x_codewriter_api_key, key) for key in valid_keys
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing X-CODEWRITER-API-KEY")
    return x_codewriter_api_key

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Redis client ──────────────────────────────────────────────────────────────


_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis | None:
    """Return a shared Redis client, or None when telemetry storage is unavailable."""
    global _redis_client
    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            with suppress(Exception):
                _redis_client.close()
            _redis_client = None
    try:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)
        _redis_client.ping()
        return _redis_client
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — telemetry will be skipped", exc)
        if _redis_client is not None:
            with suppress(Exception):
                _redis_client.close()
        _redis_client = None
        return None


# ── Bridge singleton ──────────────────────────────────────────────────────────

_bridge: LuminarkLiveBridge | None = None


def _verify_docker_runtime(require_image: bool = True) -> bool:
    """Check that the Docker CLI, daemon, and configured sandbox image are usable."""
    if not shutil.which("docker"):
        return False
    try:
        info = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if info.returncode != 0:
            return False
        if require_image:
            image = subprocess.run(
                ["docker", "image", "inspect", DOCKER_IMAGE],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if image.returncode != 0:
                return False
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def _get_bridge() -> LuminarkLiveBridge:
    global _bridge
    if EXEC_MODE not in {"docker", "local"}:
        raise RuntimeError("LUMINARK_MODE must be 'docker' or 'local'.")
    if EXEC_MODE == "local" and ENVIRONMENT != "development":
        raise RuntimeError("LOCAL execution is permitted only in development.")
    if _bridge is None:
        mode = ExecutionMode.DOCKER if EXEC_MODE == "docker" else ExecutionMode.LOCAL
        _bridge = LuminarkLiveBridge(
            execution_mode=mode,
            max_iterations=MAX_ITERATIONS,
            docker_image=DOCKER_IMAGE,
            stability_threshold=STABILITY_THRESHOLD,
        )
        logger.info(f"LuminarkLiveBridge singleton created | mode={mode.value}")
    return _bridge


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LUMINARK Bridge starting up — warming bridge and Redis connection")
    if ENVIRONMENT == "production":
        if not CODEWRITER_API_KEY or len(CODEWRITER_API_KEY) < 32:
            raise RuntimeError("Production requires CODEWRITER_API_KEY of at least 32 characters.")
        if CODEWRITER_DEMO_KEY:
            raise RuntimeError("CODEWRITER_DEMO_KEY is disabled in production.")
        if EXEC_MODE != "docker":
            raise RuntimeError("Production requires Docker execution mode.")
        if not _verify_docker_runtime(require_image=True):
            raise RuntimeError(
                "Production requires a reachable Docker daemon and the configured sandbox image."
            )
        if not CORS_ORIGINS or any(not origin.startswith("https://") for origin in CORS_ORIGINS):
            raise RuntimeError("Production CORS_ORIGINS must contain explicit HTTPS origins.")
    _get_bridge()
    _get_redis()
    yield
    logger.info("LUMINARK Bridge shutting down")
    if _redis_client is not None:
        _redis_client.close()


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="LUMINARK Live Bridge",
    description=(
        "Experimental code-execution and heuristic-scoring prototype. A PASS "
        "means only that programmed thresholds were met; it does not certify "
        "code correctness, security, or safe behavior. Repair suggestions are "
        "heuristic and are not generated by an integrated language model."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if ENVIRONMENT == "production" else "/docs",
    redoc_url=None if ENVIRONMENT == "production" else "/redoc",
    openapi_url=None if ENVIRONMENT == "production" else "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CODEWRITER-API-KEY"],
)


# ── Request / Response models ─────────────────────────────────────────────────


class GovernRequest(BaseModel):
    code: str = Field(
        ..., min_length=1, max_length=100_000, description="Python source code to govern"
    )
    task_description: str = Field(
        "", max_length=2_000, description="Human-readable task description"
    )
    context_id: str = Field(
        "default", pattern=r"^[A-Za-z0-9_-]{1,64}$", description="ID for telemetry grouping"
    )
    prev_stage: int | None = Field(None, ge=0, le=9)


class StageReportRequest(BaseModel):
    code: str = Field(
        ..., min_length=1, max_length=100_000, description="Python source code to classify"
    )
    context_id: str = Field("default", pattern=r"^[A-Za-z0-9_-]{1,64}$")


# ── Telemetry helper ──────────────────────────────────────────────────────────


def _persist_telemetry(r: redis.Redis | None, context_id: str, result_dict: dict):
    """
    Write non-sensitive governance metadata to Redis.

    Submitted source and final code, stdout/stderr, and detailed diagnostic
    messages are deliberately excluded from persistent telemetry.
    Per-context keys expire after the configured retention period.
    """
    if r is None:
        return

    try:
        ctx = context_id

        # V-series: one entry per governance iteration
        v_key = _KEY_V_SERIES.format(ctx=ctx)
        stage_key = _KEY_STAGE_SEQ.format(ctx=ctx)
        for v in result_dict.get("v_history", []):
            r.rpush(v_key, v)
        r.expire(v_key, TELEMETRY_TTL_SECONDS)

        # Stage sequence
        for s in result_dict.get("stage_history", []):
            r.rpush(stage_key, s)
        r.expire(stage_key, TELEMETRY_TTL_SECONDS)

        # Persist metadata only; never store submitted or generated source code.
        report = result_dict.get("final_report") or {}
        audit_record = {
            "verdict": result_dict.get("verdict"),
            "iterations": result_dict.get("iterations"),
            "total_elapsed_s": result_dict.get("total_elapsed_s"),
            "v_history": result_dict.get("v_history", []),
            "stage_history": result_dict.get("stage_history", []),
            "diagnosis_count": len(result_dict.get("diagnoses", [])),
            "final_report": {
                "passed": report.get("passed"),
                "V": report.get("V"),
                "action": report.get("action"),
                "entropy": report.get("entropy"),
                "energy": report.get("energy"),
                "velocity": report.get("velocity"),
            },
        }
        audit_key = _KEY_AUDIT.format(ctx=ctx)
        latest_key = _KEY_LATEST.format(ctx=ctx)
        r.rpush(audit_key, json.dumps(audit_record))
        r.ltrim(audit_key, -100, -1)
        r.expire(audit_key, TELEMETRY_TTL_SECONDS)

        # Latest metadata only (quick dashboard lookup)
        r.set(latest_key, json.dumps(audit_record), ex=TELEMETRY_TTL_SECONDS)

        # Global verdict counters
        r.incr(_KEY_VERDICT_CTR.format(verdict=result_dict.get("verdict", "UNKNOWN")))

    except Exception as exc:
        logger.warning(f"Telemetry write failed for context '{context_id}': {exc}")


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.post("/govern")
@limiter.limit("20/minute")
def govern(request: Request, body: GovernRequest, api_key: str = Depends(verify_api_key)):
    """
    Run the full LUMINARK governance loop on submitted code.
    Requires X-CODEWRITER-API-KEY header. Rate limited: 20/minute.
    """
    bridge = _get_bridge()
    r = _get_redis()

    try:
        result = bridge.govern(
            code=body.code,
            task_description=body.task_description,
            prev_stage=body.prev_stage,
        )
    except Exception as exc:
        logger.error(f"Bridge govern() raised: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Governance operation failed. See server logs."
        ) from exc

    result_dict = result.to_dict()
    _persist_telemetry(r, body.context_id, result_dict)

    v_hist = result.v_history
    dv_dt = None
    if len(v_hist) >= 2:
        dv_dt = round(v_hist[-1] - v_hist[0], 4)

    return {
        **result_dict,
        "context_id": body.context_id,
        "dv_dt_overall": dv_dt,
        "telemetry_stored": r is not None,
    }


@app.post("/stage-report")
@limiter.limit("60/minute")
def stage_report(
    request: Request, body: StageReportRequest, api_key: str = Depends(verify_api_key)
):
    """Quick SAP stage classification — no full governance loop."""
    bridge = _get_bridge()
    try:
        report = bridge.get_stage_report(body.code)
    except Exception as exc:
        logger.error(f"stage_report error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Stage report failed. See server logs."
        ) from exc

    return {
        "context_id": body.context_id,
        **report,
    }


@app.get("/telemetry/{context_id}")
@limiter.limit("60/minute")
def get_telemetry(
    request: Request,
    context_id: str = Path(..., pattern=r"^[A-Za-z0-9_-]{1,64}$"),
    limit: int = Query(50, ge=1, le=100),
    api_key: str = Depends(verify_api_key),
):
    """
    Retrieve stored Lyapunov V-series and stage history for a context ID.

    Returns:
      v_series      — last `limit` V values (for dV/dt plotting)
      stage_sequence — last `limit` SAP stage values
      latest        — most recent full governance result
      run_count     — total runs stored for this context
    """
    r = _get_redis()
    if r is None:
        raise HTTPException(status_code=503, detail="Redis unavailable")

    try:
        ctx = context_id
        v_raw = r.lrange(_KEY_V_SERIES.format(ctx=ctx), -limit, -1)
        s_raw = r.lrange(_KEY_STAGE_SEQ.format(ctx=ctx), -limit, -1)
        latest_s = r.get(_KEY_LATEST.format(ctx=ctx))
        run_count = r.llen(_KEY_AUDIT.format(ctx=ctx))

        v_series = [float(v) for v in v_raw]
        stage_sequence = [int(s) for s in s_raw]

        # dV/dt: slope across the stored V-series
        dv_dt = None
        if len(v_series) >= 2:
            dv_dt = round(v_series[-1] - v_series[0], 4)

        # Flag any dV > 0 windows (instability events)
        instability_events = [
            {"index": i + 1, "dV": round(v_series[i + 1] - v_series[i], 4)}
            for i in range(len(v_series) - 1)
            if v_series[i + 1] > v_series[i]
        ]

        return {
            "context_id": context_id,
            "v_series": v_series,
            "stage_sequence": stage_sequence,
            "dv_dt_overall": dv_dt,
            "instability_events": instability_events,
            "run_count": run_count,
            "latest": json.loads(latest_s) if latest_s else None,
        }
    except Exception as exc:
        logger.error(f"Telemetry read failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Telemetry read failed. See server logs."
        ) from exc


@app.get("/health")
def health():
    """Liveness check — confirms bridge and Redis status."""
    r = _get_redis()
    _get_bridge()
    docker_status = (
        ("available" if _verify_docker_runtime(require_image=True) else "unavailable")
        if EXEC_MODE == "docker"
        else "local-development-only"
    )
    return {
        "status": "ok" if docker_status == "available" or EXEC_MODE == "local" else "degraded",
        "service": "LUMINARK Live Bridge",
        "version": "1.0.0",
        "exec_mode": EXEC_MODE,
        "max_iterations": MAX_ITERATIONS,
        "stability_threshold": STABILITY_THRESHOLD,
        "redis": "connected" if r is not None else "unavailable",
        "bridge": "ready",
        "docker_runtime": docker_status,
    }
