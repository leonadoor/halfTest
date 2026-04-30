# AI News Aggregator

## 项目简介

AI News Aggregator 是一个基于 Python 的 AI 新闻聚合脚本。项目每天从预设 RSS/Atom 源拉取新闻，提取标题、链接、发布时间与摘要，经过过滤和去重后生成 Markdown 日报，并可通过 APScheduler、Linux cron 或 Windows Task Scheduler 自动执行。

当前交付内容来自以下前序任务：

- `TASK-3`：RSS 获取、解析、过滤、去重与主执行入口
- `TASK-4`：增强版 Markdown 日报/周报生成
- `TASK-5`：定时调度、日志与健康检查
- `TASK-6`：单元测试与集成测试

## 目录结构

```text
outputs/proj-2-7b10c0/
├── TASK-3/
│   ├── main.py
│   ├── config/feeds.yaml
│   └── src/
├── TASK-4/
│   ├── markdown_generator.py
│   └── generated_reports/        # 由调度任务输出
├── TASK-5/
│   ├── scheduler_service.py
│   ├── run_scheduled_job.py
│   ├── config/scheduler.yaml
│   └── logs/                     # 运行后生成
├── TASK-6/
│   └── run_tests.py
└── TASK-7/
    ├── README.md
    ├── INSTALLATION.md
    ├── CONFIGURATION.md
    ├── TROUBLESHOOTING.md
    └── result.json
```

## 快速开始

1. 安装 Python 3.11 或更高版本。
2. 安装项目依赖。
3. 检查 RSS 源配置 `outputs/proj-2-7b10c0/TASK-3/config/feeds.yaml`。
4. 手动运行一次主流程，确认能够生成日报。
5. 视需要启用 `TASK-5` 的调度服务或系统计划任务。

常用命令：

```bash
python outputs/proj-2-7b10c0/TASK-3/main.py --output outputs/proj-2-7b10c0/TASK-4/generated_reports
python outputs/proj-2-7b10c0/TASK-5/scheduler_service.py --run-once
python outputs/proj-2-7b10c0/TASK-6/run_tests.py
```

## 运行方式

### 1. 手动生成日报

```bash
python outputs/proj-2-7b10c0/TASK-3/main.py \
  --config outputs/proj-2-7b10c0/TASK-3/config/feeds.yaml \
  --output outputs/proj-2-7b10c0/TASK-4/generated_reports \
  --log-level INFO
```

可选参数：

- `--date YYYY-MM-DD`：为指定日期生成报告
- `--log-file PATH`：将运行日志输出到文件

### 2. 单次调度执行

```bash
python outputs/proj-2-7b10c0/TASK-5/scheduler_service.py --run-once
```

该命令会读取 `TASK-5/config/scheduler.yaml`，并将最新状态写入 `TASK-5/logs/last_run.json`。

### 3. 常驻调度服务

```bash
python outputs/proj-2-7b10c0/TASK-5/scheduler_service.py
```

默认配置会在 `Asia/Shanghai` 时区的每天 `08:00` 执行一次。

## 输出说明

- `TASK-4/generated_reports/`：生成的 Markdown 日报文件
- `TASK-5/logs/scheduler.log`：调度运行日志
- `TASK-5/logs/last_run.json`：最近一次运行状态

Markdown 日报通常包含：

- 报告标题和日期
- 分类统计摘要
- 按发布日期与新闻源分组的文章列表
- 每篇文章的标题、链接、时间、分类与摘要

## 测试

```bash
python outputs/proj-2-7b10c0/TASK-6/run_tests.py
```

测试覆盖 RSS 获取、解析、文章处理、Markdown 生成和 `JobRunner` 端到端执行路径。

## 文档索引

- 安装步骤：`INSTALLATION.md`
- 配置说明：`CONFIGURATION.md`
- 故障排查：`TROUBLESHOOTING.md`
