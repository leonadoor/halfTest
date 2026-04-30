# 故障排除指南

## 1. 启动时报缺少模块

典型现象：

- `ModuleNotFoundError: No module named 'apscheduler'`
- `ModuleNotFoundError: No module named 'yaml'`
- `ModuleNotFoundError: No module named 'requests'`
- `ModuleNotFoundError: No module named 'feedparser'`

处理方法：

```bash
pip install -r outputs/proj-2-7b10c0/TASK-5/requirements.txt
pip install requests feedparser
```

如果使用虚拟环境，先确认已经激活对应环境。

## 2. 运行主流程时日期格式错误

典型现象：

- 命令传入 `--date 2026/04/30`
- 程序报错提示必须使用 `YYYY-MM-DD`

处理方法：

```bash
python outputs/proj-2-7b10c0/TASK-3/main.py --date 2026-04-30
```

## 3. 无法抓取 RSS 内容

可能原因：

- 目标 RSS 地址失效
- 网络出口被限制
- 远端站点临时不可用
- HTTPS 访问被代理或证书策略拦截

处理方法：

1. 先检查 `TASK-3/config/feeds.yaml` 中的 URL 是否仍然有效。
2. 在部署机器上直接访问 RSS 源，确认网络连通。
3. 暂时将异常源的 `enabled` 设置为 `false`，避免影响整体日报生成。
4. 查看运行日志，定位是全部源失败还是单个源失败。

## 4. 没有生成 Markdown 报告

排查顺序：

1. 检查 `main.py` 或调度脚本是否实际返回成功。
2. 检查输出目录参数是否指向预期位置。
3. 检查抓取结果是否在过滤和去重后为空。
4. 检查部署账号是否有目录写权限。

建议命令：

```bash
python outputs/proj-2-7b10c0/TASK-5/scheduler_service.py --run-once
```

然后查看：

- `outputs/proj-2-7b10c0/TASK-5/logs/scheduler.log`
- `outputs/proj-2-7b10c0/TASK-5/logs/last_run.json`

## 5. 定时任务未按预期触发

### APScheduler 常驻模式

检查项：

- `scheduler.yaml` 中 `timezone`、`hour`、`minute` 是否正确
- 进程是否持续存活
- 是否存在系统重启后未自动拉起的问题

### Linux cron

检查项：

- `install_cron.sh` 是否成功安装
- `crontab -l` 中是否存在对应任务
- 执行路径是否使用了正确的 Python 解释器

### Windows Task Scheduler

检查项：

- 任务是否已成功注册
- 运行账户是否有访问项目目录与 Python 的权限
- 历史记录中是否存在启动失败或权限错误

## 6. `last_run.json` 显示失败

`last_run.json` 只记录最近一次执行状态。若状态为 `failed`：

1. 先查看同时间段的 `scheduler.log`
2. 确认失败发生在配置加载、依赖导入、RSS 拉取还是文件写入阶段
3. 修复问题后执行一次 `--run-once`，确认状态恢复为 `success`

## 7. 测试执行失败

处理方法：

1. 确认当前代码和前序任务目录完整存在。
2. 确认依赖已经安装。
3. 从仓库根目录执行测试：

```bash
python outputs/proj-2-7b10c0/TASK-6/run_tests.py
```

如果某条测试只在特定机器失败，优先检查：

- Python 版本差异
- 本地路径分隔符与编码环境
- 依赖版本不一致
