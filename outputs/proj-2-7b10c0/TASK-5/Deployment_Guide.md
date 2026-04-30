# TASK-5 Deployment Guide

## Overview

This delivery adds a production-oriented scheduling layer for the AI News Aggregator. It supports:

- APScheduler-based in-process scheduling for long-running service mode
- one-shot execution for Linux cron and Windows Task Scheduler
- rotating logs and `last_run.json` healthcheck output
- guarded error handling so feed or job failures are visible in logs and scheduler state

## Files

- `scheduler_service.py`: APScheduler service and one-shot runner
- `run_scheduled_job.py`: wrapper intended for cron or Task Scheduler
- `config/scheduler.yaml`: schedule, pipeline path, and logging settings
- `install_cron.sh`: helper to register a Linux cron job
- `register_windows_task.ps1`: helper to register a Windows scheduled task
- `requirements.txt`: minimal scheduler dependencies

## How It Works

`scheduler_service.py` loads `config/scheduler.yaml`, resolves the upstream pipeline from `../TASK-3`, and runs `JobRunner.run_daily_job()`. Every execution writes:

- `logs/scheduler.log`: rotated daily, retained for the configured number of days
- `logs/last_run.json`: latest success or failure marker for health checks

If `--run-once` is passed, the service executes immediately and exits. This is the mode used by cron and Windows Task Scheduler.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Review and adjust `config/scheduler.yaml`:

- `timezone`: scheduler timezone
- `cron.hour` and `cron.minute`: daily execution time
- `pipeline.config_path`: RSS feed config from TASK-3
- `pipeline.output_dir`: report output directory
- `pipeline.log_level`: runtime verbosity

3. Test one execution locally:

```bash
python scheduler_service.py --run-once
```

## Linux Cron

Register the daily job:

```bash
bash install_cron.sh
```

The installed entry runs at `08:00` every day and appends stdout/stderr to `logs/cron.log`.

## Windows Task Scheduler

Register the task from PowerShell:

```powershell
.\register_windows_task.ps1
```

The script creates a daily `08:00` task with `IgnoreNew` instance policy so overlapping runs are skipped.

## Service Mode

If you want to keep the scheduler alive as a process instead of relying on OS scheduling:

```bash
python scheduler_service.py
```

This starts an APScheduler blocking service and runs the pipeline every day according to `config/scheduler.yaml`.

## Error Handling

- uncaught pipeline exceptions are logged with stack traces
- APScheduler success and failure events update `logs/last_run.json`
- `max_instances=1` prevents concurrent overlapping runs
- `coalesce=true` merges missed runs into a single execution after downtime
- `misfire_grace_time=1800` allows a delayed start within 30 minutes
