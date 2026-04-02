from __future__ import annotations

import gzip
import logging
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone as dt_timezone
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _cleanup_old_backups(storage_dir: Path, keep_days: int) -> int:
    removed = 0
    if keep_days <= 0:
        return removed

    threshold = timezone.now() - timedelta(days=keep_days)
    for backup_file in storage_dir.glob("*.sql.gz"):
        modified_at = datetime.fromtimestamp(backup_file.stat().st_mtime, tz=dt_timezone.utc)
        if modified_at >= threshold:
            continue
        try:
            backup_file.unlink()
            removed += 1
        except OSError:
            logger.exception("Failed to remove old backup file path=%s", backup_file)
    return removed


@shared_task(bind=True, autoretry_for=(RuntimeError,), retry_kwargs={"max_retries": 3, "countdown": 60})
def create_postgres_backup(self):
    if not settings.BACKUP_ENABLED:
        logger.info("PostgreSQL backup skipped: BACKUP_ENABLED is false")
        return {"status": "skipped", "reason": "BACKUP_ENABLED_FALSE"}

    db_cfg = settings.DATABASES["default"]
    storage_dir = Path(settings.BACKUP_STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    timestamp = timezone.localtime().strftime("%Y%m%d_%H%M%S")
    db_name = db_cfg.get("NAME") or "postgres"
    output_path = storage_dir / f"{db_name}_{timestamp}.sql.gz"

    command = [
        settings.BACKUP_PG_DUMP_PATH,
        "--host",
        str(db_cfg.get("HOST") or "db"),
        "--port",
        str(db_cfg.get("PORT") or 5432),
        "--username",
        str(db_cfg.get("USER") or "postgres"),
        "--dbname",
        str(db_name),
        "--no-owner",
        "--no-privileges",
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = str(db_cfg.get("PASSWORD") or "")

    try:
        with output_path.open("wb") as target_file:
            with gzip.GzipFile(fileobj=target_file, mode="wb") as gz_stream:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                )
                assert process.stdout is not None
                shutil.copyfileobj(process.stdout, gz_stream)
                _, stderr = process.communicate()
    except FileNotFoundError as exc:
        logger.exception("pg_dump binary not found path=%s", settings.BACKUP_PG_DUMP_PATH)
        raise RuntimeError("pg_dump is not available in container image") from exc
    except OSError as exc:
        logger.exception("PostgreSQL backup failed with OS error")
        raise RuntimeError("backup os error") from exc

    if process.returncode != 0:
        try:
            output_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Failed to remove broken backup file path=%s", output_path)
        error_text = (stderr or b"").decode("utf-8", errors="ignore")
        logger.error("PostgreSQL backup failed rc=%s stderr=%s", process.returncode, error_text)
        raise RuntimeError(f"pg_dump failed with code {process.returncode}")

    removed = _cleanup_old_backups(storage_dir, keep_days=settings.BACKUP_KEEP_DAYS)
    logger.info("PostgreSQL backup created path=%s removed_old=%s", output_path, removed)
    return {
        "status": "ok",
        "path": str(output_path),
        "removed_old": removed,
    }
