"""
Kiểm tra freshness từ manifest pipeline (SLA đơn giản theo giờ).

Sinh viên mở rộng: đọc watermark DB, so sánh với clock batch, v.v.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


def parse_iso(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        # Cho phép "2026-04-10T08:00:00" không có timezone
        if ts.endswith("Z"):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def check_manifest_freshness(
    manifest_path: Path,
    *,
    sla_hours: float = 24.0,
    now: datetime | None = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Trả về ("PASS" | "WARN" | "FAIL", detail dict).

    Distinction/Bonus (Day 10): Đo freshness ở 2 ranh giới (boundary):
    1) Source -> Ingest: latest_exported_at (nguồn) vs run_timestamp (lúc chạy).
    2) Ingest -> Publish: run_timestamp vs now (hiện tại).
    """
    now = now or datetime.now(timezone.utc)
    if not manifest_path.is_file():
        return "FAIL", {"reason": "manifest_missing", "path": str(manifest_path)}

    data: Dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    # Boundary 1: Source to Ingest
    ts_export = parse_iso(str(data.get("latest_exported_at", "")))
    ts_run = parse_iso(str(data.get("run_timestamp", "")))
    
    detail = {
        "run_id": data.get("run_id"),
        "sla_hours": sla_hours,
        "boundaries": {}
    }

    if not ts_run:
        return "FAIL", {"reason": "missing_run_timestamp"}

    # B1 Check
    if ts_export:
        b1_age = (ts_run - ts_export).total_seconds() / 3600.0
        detail["boundaries"]["source_to_ingest"] = {
            "age_hours": round(b1_age, 3),
            "status": "PASS" if b1_age <= sla_hours else "FAIL"
        }
    else:
        detail["boundaries"]["source_to_ingest"] = {"status": "UNKNOWN", "reason": "no_export_ts"}

    # Boundary 2: Ingest to Publish (Now)
    b2_age = (now - ts_run).total_seconds() / 3600.0
    detail["boundaries"]["ingest_to_publish"] = {
        "age_hours": round(b2_age, 3),
        "status": "PASS" if b2_age <= sla_hours else "FAIL"
    }

    # Final logic: PASS only if all PASS or UNKNOWN (B1 is optional if no source TS)
    statuses = [b["status"] for b in detail["boundaries"].values()]
    if "FAIL" in statuses:
        return "FAIL", detail
    if "PASS" in statuses:
        return "PASS", detail
    return "WARN", detail
