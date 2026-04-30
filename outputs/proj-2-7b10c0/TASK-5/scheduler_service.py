#!/usr/bin/env python3
"""Scheduled execution service for the AI News Aggregator."""

from __future__ import annotations

import argparse
import json
import logging
import logging.handlers
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

BASE_DIR = Path(__file__).resolve().parent
TASK3_DIR = BASE_DIR.parent / "TASK-3"
TASK3_SRC_DIR = TASK3_DIR / "src"

if str(TASK3_DIR) not in sys.path:
    sys.path.insert(0, str(TASK3_DIR))
if str(TASK3_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(TASK3_SRC_DIR))

from src.schedulers.job_runner import JobRunner  # noqa: E402


@dataclass
class SchedulerConfig:
    timezone: str
    cron_hour: int
    cron_minute: int
    job_id: str
    coalesce: bool
    max_instances: int
    misfire_grace_time: int
    config_path: Path
    output_dir: Path
    log_dir: Path
    log_level: str
    retention_days: int


def load_config(config_path: Path) -> SchedulerConfig:
    """Load scheduler settings from YAML."""
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    scheduler = raw.get("scheduler", {})
    cron = scheduler.get("cron", {})
    job = scheduler.get("job", {})
    pipeline = scheduler.get("pipeline", {})

    return SchedulerConfig(
        timezone=scheduler.get("timezone", "Asia/Shanghai"),
        cron_hour=int(cron.get("hour", 8)),
        cron_minute=int(cron.get("minute", 0)),
        job_id=job.get("id", "ai_news_daily_digest"),
        coalesce=bool(job.get("coalesce", True)),
        max_instances=int(job.get("max_instances", 1)),
        misfire_grace_time=int(job.get("misfire_grace_time", 1800)),
        config_path=(config_path.parent / pipeline.get("config_path", "../TASK-3/config/feeds.yaml")).resolve(),
        output_dir=(config_path.parent / pipeline.get("output_dir", "../TASK-4/generated_reports")).resolve(),
        log_dir=(BASE_DIR / pipeline.get("log_dir", "logs")).resolve(),
        log_level=str(pipeline.get("log_level", "INFO")).upper(),
        retention_days=int(pipeline.get("retention_days", 14)),
    )


def setup_logging(log_dir: Path, log_level: str, retention_days: int) -> logging.Logger:
    """Configure console and rotating file logs."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "scheduler.log"

    logger = logging.getLogger("ai_news_scheduler")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        backupCount=retention_days,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run_pipeline(config: SchedulerConfig, logger: logging.Logger) -> dict[str, Any]:
    """Execute one aggregation run and return execution metadata."""
    logger.info("Starting scheduled pipeline run")
    started_at = time.perf_counter()

    job_runner = JobRunner(
        config_path=str(config.config_path),
        output_dir=str(config.output_dir),
    )

    stats = job_runner.run_daily_job()
    duration_seconds = round(time.perf_counter() - started_at, 2)

    result = {
        "status": "success",
        "executed_at": datetime.now(ZoneInfo(config.timezone)).isoformat(),
        "duration_seconds": duration_seconds,
        "stats": stats,
    }
    logger.info("Pipeline run finished in %.2fs", duration_seconds)
    logger.info("Run result: %s", json.dumps(result, ensure_ascii=False))
    return result


def run_job(config: SchedulerConfig, logger: logging.Logger) -> None:
    """Execute the scheduled job with guarded error handling."""
    try:
        run_pipeline(config, logger)
    except Exception:
        logger.exception("Scheduled pipeline run failed")
        raise


def write_healthcheck(config: SchedulerConfig, payload: dict[str, Any]) -> None:
    """Persist the latest run status for external monitoring."""
    config.log_dir.mkdir(parents=True, exist_ok=True)
    healthcheck_path = config.log_dir / "last_run.json"
    with healthcheck_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def scheduler_listener(event: Any, config: SchedulerConfig, logger: logging.Logger) -> None:
    """Capture APScheduler job outcomes into a healthcheck file."""
    if event.exception:
        payload = {
            "status": "failed",
            "executed_at": datetime.now(ZoneInfo(config.timezone)).isoformat(),
        }
        write_healthcheck(config, payload)
        logger.error("Job %s failed", event.job_id)
        return

    payload = {
        "status": "success",
        "executed_at": datetime.now(ZoneInfo(config.timezone)).isoformat(),
        "job_id": event.job_id,
    }
    write_healthcheck(config, payload)
    logger.info("Job %s executed successfully", event.job_id)


def build_scheduler(config: SchedulerConfig, logger: logging.Logger) -> BlockingScheduler:
    """Create the blocking scheduler instance."""
    scheduler = BlockingScheduler(timezone=ZoneInfo(config.timezone))
    trigger = CronTrigger(
        hour=config.cron_hour,
        minute=config.cron_minute,
        timezone=ZoneInfo(config.timezone),
    )
    scheduler.add_job(
        run_job,
        trigger=trigger,
        id=config.job_id,
        kwargs={"config": config, "logger": logger},
        coalesce=config.coalesce,
        max_instances=config.max_instances,
        misfire_grace_time=config.misfire_grace_time,
        replace_existing=True,
    )
    scheduler.add_listener(
        lambda event: scheduler_listener(event, config, logger),
        EVENT_JOB_EXECUTED | EVENT_JOB_ERROR,
    )
    return scheduler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI News Aggregator on a fixed APScheduler schedule.")
    parser.add_argument(
        "--config",
        default=str(BASE_DIR / "config" / "scheduler.yaml"),
        help="Path to scheduler configuration YAML.",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Execute the pipeline immediately and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config).resolve())
    logger = setup_logging(config.log_dir, config.log_level, config.retention_days)

    if args.run_once:
        try:
            payload = run_pipeline(config, logger)
            write_healthcheck(config, payload)
            return 0
        except Exception:
            return 1

    scheduler = build_scheduler(config, logger)
    logger.info(
        "Scheduler started for %02d:%02d %s, job_id=%s",
        config.cron_hour,
        config.cron_minute,
        config.timezone,
        config.job_id,
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
