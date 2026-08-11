from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_base_url: str = os.getenv("CLINIC_OPS_API_BASE_URL", "http://127.0.0.1:8765")
    lake_backend: str = os.getenv("LAKE_BACKEND", "local")
    local_lake_root: Path = Path(os.getenv("LOCAL_LAKE_ROOT", "data_lake"))
    warehouse_path: Path = Path(os.getenv("WAREHOUSE_PATH", "warehouse/clinic_ops.duckdb"))
    s3_bucket: str = os.getenv("S3_BUCKET", "")
    s3_prefix: str = os.getenv("S3_PREFIX", "clinic-ops").strip("/")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
