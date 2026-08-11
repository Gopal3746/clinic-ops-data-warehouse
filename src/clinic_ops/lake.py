from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from clinic_ops.config import Settings


class LakeStorage(ABC):
    @abstractmethod
    def write_text(self, key: str, text: str) -> None: ...

    @abstractmethod
    def read_text(self, key: str) -> str: ...

    @abstractmethod
    def list_keys(self, prefix: str) -> list[str]: ...


class LocalLakeStorage(LakeStorage):
    def __init__(self, root: Path):
        self.root = root

    def write_text(self, key: str, text: str) -> None:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def read_text(self, key: str) -> str:
        return (self.root / key).read_text(encoding="utf-8")

    def list_keys(self, prefix: str) -> list[str]:
        base = self.root / prefix
        if not base.exists():
            return []
        return sorted(
            str(path.relative_to(self.root))
            for path in base.rglob("*")
            if path.is_file()
        )


class S3LakeStorage(LakeStorage):
    def __init__(self, bucket: str, prefix: str, region: str):
        if not bucket:
            raise ValueError("S3_BUCKET is required when LAKE_BACKEND=s3")
        import boto3

        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.client = boto3.client("s3", region_name=region)

    def _full_key(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def write_text(self, key: str, text: str) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=self._full_key(key),
            Body=text.encode("utf-8"),
            ContentType="application/x-ndjson",
        )

    def read_text(self, key: str) -> str:
        obj = self.client.get_object(Bucket=self.bucket, Key=self._full_key(key))
        return obj["Body"].read().decode("utf-8")

    def list_keys(self, prefix: str) -> list[str]:
        full_prefix = self._full_key(prefix)
        paginator = self.client.get_paginator("list_objects_v2")
        keys: list[str] = []
        prefix_cut = f"{self.prefix}/" if self.prefix else ""
        for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
            for item in page.get("Contents", []):
                key = item["Key"]
                if prefix_cut and key.startswith(prefix_cut):
                    key = key[len(prefix_cut):]
                keys.append(key)
        return sorted(keys)


def get_lake(settings: Settings | None = None) -> LakeStorage:
    settings = settings or Settings()
    if settings.lake_backend.lower() == "s3":
        return S3LakeStorage(
            settings.s3_bucket,
            settings.s3_prefix,
            settings.aws_region,
        )
    return LocalLakeStorage(settings.local_lake_root)
