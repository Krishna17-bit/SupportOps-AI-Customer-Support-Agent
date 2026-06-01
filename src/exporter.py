from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


def ensure_outputs(base_dir: Path) -> Path:
    out = base_dir / "outputs"
    out.mkdir(exist_ok=True)
    return out


def write_exports(base_dir: Path, results_df: pd.DataFrame, audit: List[Dict]) -> Dict[str, Path]:
    out = ensure_outputs(base_dir)
    csv_path = out / "supportops_triaged_tickets.csv"
    json_path = out / "supportops_audit_package.json"
    results_df.drop(columns=["evidence"], errors="ignore").to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"csv": csv_path, "json": json_path}
