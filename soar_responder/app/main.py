from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


def _data_dir() -> Path:
    return Path(os.getenv("SOAR_DATA_DIR", "/data"))


def _ensure_files() -> tuple[Path, Path]:
    data_dir = _data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    actions_log = data_dir / "actions.log"
    blocked_ips = data_dir / "blocked_ips.json"
    if not blocked_ips.exists():
        blocked_ips.write_text("[]", encoding="utf-8")
    return actions_log, blocked_ips


def _append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line.rstrip("\n") + "\n")


def _load_json_array(path: Path) -> list[Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        val = json.loads(raw or "[]")
        if isinstance(val, list):
            return val
    except Exception:
        pass
    return []


def _atomic_write_json(path: Path, obj: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


class RespondRequest(BaseModel):
    src_ip: str = Field(..., min_length=3)
    anomaly_score: Optional[str] = None
    description: Optional[str] = None
    wazuh_rule_id: Optional[str] = None
    raw_alert: Optional[Dict[str, Any]] = None


app = FastAPI(title="Next-Gen SIEM SOAR Responder", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/respond")
def respond(req: RespondRequest) -> dict[str, Any]:
    actions_log, blocked_ips_path = _ensure_files()

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    action_id = f"mitigation_{int(time.time() * 1000)}"

    blocked = _load_json_array(blocked_ips_path)
    if req.src_ip not in blocked:
        blocked.append(req.src_ip)
        _atomic_write_json(blocked_ips_path, blocked)

    _append_line(
        actions_log,
        json.dumps(
            {
                "timestamp": now,
                "action_id": action_id,
                "action": "block_ip_simulated",
                "src_ip": req.src_ip,
                "anomaly_score": req.anomaly_score,
                "description": req.description,
                "wazuh_rule_id": req.wazuh_rule_id,
            },
            ensure_ascii=False,
        ),
    )

    return {
        "status": "mitigated",
        "action_id": action_id,
        "blocked_ip": req.src_ip,
        "blocked_ip_count": len(blocked),
    }


@app.post("/reset")
def reset() -> dict[str, str]:
    _, blocked_ips_path = _ensure_files()
    _atomic_write_json(blocked_ips_path, [])
    return {"status": "reset"}

