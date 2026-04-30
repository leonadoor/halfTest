# 安装说明

## 环境要求

- Python 3.11 或更高版本
- 可访问外部 RSS/Atom 源的网络环境
- 建议使用虚拟环境隔离依赖

## 依赖概览

已知直接依赖来自现有交付：

- `APScheduler`：调度服务
- `PyYAML`：读取调度配置

根据 `TASK-3` 与 `TASK-6` 的实现，运行主流程和测试时还需要确保以下常见依赖已安装：

- `requests`
- `feedparser`

## 创建虚拟环境

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 安装依赖

由于仓库当前只在 `TASK-5` 提供了调度依赖文件，建议先安装其中内容，再补齐主流程依赖：

```bash
pip install -r outputs/proj-2-7b10c0/TASK-5/requirements.txt
pip install requests feedparser
```

如果你希望统一管理依赖，建议在项目根目录新增完整 `requirements.txt`，至少包含：

```text
APScheduler>=3.10,<4.0
PyYAML>=6.0,<7.0
requests
feedparser
```

## 安装后验证

### 验证主流程

```bash
python outputs/proj-2-7b10c0/TASK-3/main.py --help
```

### 验证调度脚本

```bash
python outputs/proj-2-7b10c0/TASK-5/scheduler_service.py --help
```

### 验证测试套件

```bash
python outputs/proj-2-7b10c0/TASK-6/run_tests.py
```

## 常见安装建议

- 在公司网络中部署时，先确认 RSS 源可访问性
- 若系统存在多个 Python 版本，统一使用 `python -m pip` 避免装到错误环境
- 首次部署前先执行一次 `--run-once`，确保目录权限和依赖都正常
