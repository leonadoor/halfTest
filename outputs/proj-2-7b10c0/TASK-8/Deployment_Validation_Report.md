# TASK-8 部署配置与最终验证

## 目标

完成可部署依赖清单整理，并对 AI News Aggregator 执行最终验证，确认以下链路可用：

- `TASK-3` 主入口可直接通过 CLI 执行
- `TASK-5` 调度服务可通过 `--run-once` 执行完整流水线
- `TASK-6` 自动化测试可全部通过

## 部署配置结论

- 运行环境：Python 3.14.3
- 依赖文件：`requirements.txt`
- 补齐的运行时依赖：
  - `requests`
  - `feedparser`
- 已修复的部署阻塞问题：
  - `TASK-3/main.py` 改为使用 `src.*` 包导入，避免直接运行时报相对导入错误
  - `TASK-3/main.py` 的默认 `--config` / `--output` 路径改为相对脚本目录解析，避免从仓库根目录运行时报配置文件缺失

## 验证方法

为避免外网 RSS 在受限环境下影响结果，使用 `final_validation.py` 启动本地 HTTP RSS 伪源并执行以下验证：

1. 运行 `python outputs/proj-2-7b10c0/TASK-6/run_tests.py`
2. 运行 `python outputs/proj-2-7b10c0/TASK-3/main.py --config ... --output ... --date ...`
3. 运行 `python outputs/proj-2-7b10c0/TASK-5/scheduler_service.py --config ... --run-once`

## 结果

验证通过后，产物写入 `validation_output/`，包括：

- `validation_summary.json`
- `main_reports/ai_news_YYYY-MM-DD.md`
- `scheduler_reports/ai_news_YYYY-MM-DD.md`
- `scheduler_logs/scheduler.log`
- `scheduler_logs/last_run.json`

如需重新验证，执行：

```powershell
python outputs/proj-2-7b10c0/TASK-8/final_validation.py
```
