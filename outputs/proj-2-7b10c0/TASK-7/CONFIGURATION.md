# 配置说明

## 1. RSS 源配置

RSS 源配置文件位于：

```text
outputs/proj-2-7b10c0/TASK-3/config/feeds.yaml
```

当前格式示例：

```yaml
feeds:
  - name: "OpenAI Blog"
    url: "https://openai.com/blog/rss.xml"
    category: "Research"
    priority: 10
    enabled: true
    update_hours: 12
```

字段说明：

- `name`：新闻源名称
- `url`：RSS 或 Atom 地址
- `category`：文章分类标签
- `priority`：优先级，数值越高越重要
- `enabled`：是否启用该源
- `update_hours`：允许的更新间隔，用于控制抓取频率策略

配置建议：

- 新增 RSS 源时，优先选择稳定、公开、无需登录的订阅地址
- 将研究类与产业类新闻拆分到不同 `category`
- 临时禁用某个源时，直接将 `enabled` 改为 `false`

## 2. 主程序参数

主入口：

```text
outputs/proj-2-7b10c0/TASK-3/main.py
```

支持的核心参数：

- `--date`：目标日期，格式 `YYYY-MM-DD`
- `--config`：RSS 配置文件路径，默认 `config/feeds.yaml`
- `--output`：报告输出目录，默认 `output/reports`
- `--log-level`：`DEBUG`、`INFO`、`WARNING`、`ERROR`
- `--log-file`：可选日志文件路径

示例：

```bash
python outputs/proj-2-7b10c0/TASK-3/main.py \
  --date 2026-04-30 \
  --config outputs/proj-2-7b10c0/TASK-3/config/feeds.yaml \
  --output outputs/proj-2-7b10c0/TASK-4/generated_reports \
  --log-level INFO
```

## 3. 调度配置

调度配置文件位于：

```text
outputs/proj-2-7b10c0/TASK-5/config/scheduler.yaml
```

当前配置项：

```yaml
scheduler:
  timezone: Asia/Shanghai
  cron:
    hour: 8
    minute: 0
  job:
    id: ai_news_daily_digest
    coalesce: true
    max_instances: 1
    misfire_grace_time: 1800
  pipeline:
    config_path: ../TASK-3/config/feeds.yaml
    output_dir: ../TASK-4/generated_reports
    log_dir: logs
    log_level: INFO
    retention_days: 14
```

字段说明：

- `timezone`：调度时区
- `cron.hour` / `cron.minute`：每日执行时间
- `job.id`：调度任务唯一标识
- `coalesce`：宕机恢复后是否合并错过的多次执行
- `max_instances`：同一任务允许的最大并发实例数
- `misfire_grace_time`：错过计划时间后的补执行宽限秒数
- `pipeline.config_path`：RSS 配置文件路径
- `pipeline.output_dir`：Markdown 报告输出目录
- `pipeline.log_dir`：日志目录
- `pipeline.log_level`：调度日志级别
- `pipeline.retention_days`：日志保留天数

## 4. 输出目录配置

推荐输出路径保持与当前任务一致：

- 报告输出：`outputs/proj-2-7b10c0/TASK-4/generated_reports`
- 调度日志：`outputs/proj-2-7b10c0/TASK-5/logs`

修改输出目录时，请同步检查：

- 目录是否存在或是否允许自动创建
- 部署用户是否具备写权限
- 定时任务执行用户是否与手工执行用户一致

## 5. 测试配置

测试入口：

```text
outputs/proj-2-7b10c0/TASK-6/run_tests.py
```

该脚本通过 `unittest discover` 自动加载 `tests/test_*.py`。正常情况下无需额外配置，但应确保：

- Python 环境中已安装主流程依赖
- `TASK-3`、`TASK-4`、`TASK-6` 目录结构未被破坏
