#!/usr/bin/env python3
"""Run reproducible final validation for TASK-8 using a local RSS fixture."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


TASK8_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TASK8_DIR.parents[2]
TASK3_DIR = PROJECT_ROOT / "outputs" / "proj-2-7b10c0" / "TASK-3"
TASK5_DIR = PROJECT_ROOT / "outputs" / "proj-2-7b10c0" / "TASK-5"
TASK6_DIR = PROJECT_ROOT / "outputs" / "proj-2-7b10c0" / "TASK-6"
VALIDATION_DIR = TASK8_DIR / "validation_output"
FIXTURE_DIR = TASK8_DIR / "fixtures"


RSS_FIXTURE = textwrap.dedent(
    """\
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Local AI News Fixture</title>
        <link>http://localhost/</link>
        <description>Fixture feed for TASK-8 validation</description>
        <item>
          <title>Local Model Release Reaches Production</title>
          <link>https://example.com/local-model-release</link>
          <pubDate>Thu, 30 Apr 2026 09:15:00 +0800</pubDate>
          <description>Deployment fixture article used to validate markdown generation.</description>
        </item>
        <item>
          <title>Agent Workflow Passes Final Validation</title>
          <link>https://example.com/agent-validation</link>
          <pubDate>Thu, 30 Apr 2026 10:30:00 +0800</pubDate>
          <description>Scheduler run-once fixture article used to validate report output.</description>
        </item>
      </channel>
    </rss>
    """
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def run_command(command: list[str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    if VALIDATION_DIR.exists():
        shutil.rmtree(VALIDATION_DIR)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    feed_file = FIXTURE_DIR / "local_feed.xml"
    write_text(feed_file, RSS_FIXTURE)

    os.chdir(FIXTURE_DIR)
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    today = datetime.now().strftime("%Y-%m-%d")
    feed_url = f"http://127.0.0.1:{port}/{feed_file.name}"
    main_config = VALIDATION_DIR / "feeds.yaml"
    scheduler_config = VALIDATION_DIR / "scheduler.yaml"
    main_output = VALIDATION_DIR / "main_reports"
    scheduler_output = VALIDATION_DIR / "scheduler_reports"
    scheduler_logs = VALIDATION_DIR / "scheduler_logs"

    write_text(
        main_config,
        textwrap.dedent(
            f"""\
            feeds:
              - name: "Local Validation Feed"
                url: "{feed_url}"
                category: "Validation"
                priority: 10
                enabled: true
                update_hours: 24
            """
        ),
    )
    write_text(
        scheduler_config,
        textwrap.dedent(
            f"""\
            scheduler:
              timezone: Asia/Shanghai
              cron:
                hour: 8
                minute: 0
              job:
                id: ai_news_validation
                coalesce: true
                max_instances: 1
                misfire_grace_time: 1800
              pipeline:
                config_path: {main_config.as_posix()}
                output_dir: {scheduler_output.as_posix()}
                log_dir: {scheduler_logs.as_posix()}
                log_level: INFO
                retention_days: 7
            """
        ),
    )

    try:
        tests_result = run_command([sys.executable, str(TASK6_DIR / "run_tests.py")], PROJECT_ROOT)
        main_result = run_command(
            [
                sys.executable,
                str(TASK3_DIR / "main.py"),
                "--config",
                str(main_config),
                "--output",
                str(main_output),
                "--date",
                today,
            ],
            PROJECT_ROOT,
        )
        scheduler_result = run_command(
            [
                sys.executable,
                str(TASK5_DIR / "scheduler_service.py"),
                "--config",
                str(scheduler_config),
                "--run-once",
            ],
            PROJECT_ROOT,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    artifacts = {
        "tests": tests_result,
        "main_cli": main_result,
        "scheduler_run_once": scheduler_result,
        "generated_reports": sorted(str(path.relative_to(TASK8_DIR)) for path in VALIDATION_DIR.rglob("*.md")),
        "healthcheck_files": sorted(str(path.relative_to(TASK8_DIR)) for path in VALIDATION_DIR.rglob("*.json")),
        "log_files": sorted(str(path.relative_to(TASK8_DIR)) for path in VALIDATION_DIR.rglob("*.log")),
    }

    summary = {
        "validated_at": datetime.now().isoformat(),
        "python": sys.version,
        "all_commands_succeeded": all(item["returncode"] == 0 for item in (tests_result, main_result, scheduler_result)),
        "artifacts": artifacts,
    }
    write_text(VALIDATION_DIR / "validation_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))

    return 0 if summary["all_commands_succeeded"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
