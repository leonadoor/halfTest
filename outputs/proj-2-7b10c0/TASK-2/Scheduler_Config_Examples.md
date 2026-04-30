# Scheduler Configuration Examples

## 1. Feed Configuration Example

```yaml
feeds:
  - name: OpenAI Blog
    url: https://openai.com/blog/rss.xml
    category: frontline_research
    priority: 100
    enabled: true
    update_hours: 24

  - name: arXiv cs.AI
    url: https://arxiv.org/rss/cs.AI
    category: research_papers
    priority: 95
    enabled: true
    update_hours: 4

  - name: TechCrunch AI
    url: https://techcrunch.com/tag/artificial-intelligence/feed/
    category: industry_news
    priority: 85
    enabled: true
    update_hours: 6
```

## 2. Runtime Scheduler Example

```yaml
scheduler:
  timezone: Asia/Shanghai
  run_time: "08:00"
  lookback_hours: 24
  output_dir: output/reports
  log_dir: logs
  request_timeout: 15
  retry_count: 3
  keyword_filter:
    - ai
    - artificial intelligence
    - machine learning
    - deep learning
```

## 3. Linux Cron Example

Run every day at 08:00:

```cron
0 8 * * * /usr/bin/python3 /opt/ai_news_aggregator/main.py >> /opt/ai_news_aggregator/logs/cron.log 2>&1
```

## 4. Windows Task Scheduler Example

Recommended task settings:

- Trigger: daily at `08:00`
- Program: `python`
- Arguments: `main.py`
- Start in: project root directory

PowerShell registration example:

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "main.py" -WorkingDirectory "C:\AI-News-Aggregator"
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI-News-Daily-Digest" -Action $action -Trigger $trigger -Description "Generate daily AI news markdown digest"
```

## 5. In-Process Scheduler Alternative

If the project runs continuously as a service, use a lightweight in-process scheduler:

```python
import schedule
import time

from src.schedulers.job_runner import run_daily_job

schedule.every().day.at("08:00").do(run_daily_job)

while True:
    schedule.run_pending()
    time.sleep(30)
```

Use this only for long-running processes. For production reliability, prefer OS-level schedulers.
