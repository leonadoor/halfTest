# AI News Aggregator

自动抓取AI新闻RSS源并生成本地Markdown文件的Python工具。

## 功能特点

- 🚀 自动抓取多个AI新闻源的RSS订阅
- 📝 智能提取文章标题、链接、摘要和发布时间
- 🔍 自动去重，避免重复收录
- 📊 按日期组织内容，生成结构化的Markdown报告
- ⚡ 支持定时任务，实现自动化运行
- 🛡️ 完善的错误处理和日志记录

## 支持的新闻源

默认包含以下高质量的AI新闻源：

- The Verge AI
- Wired AI
- VentureBeat AI
- MIT Technology Review AI
- Google AI Blog
- OpenAI Blog
- DeepMind Blog
- NVIDIA AI Blog

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/leonadoor/halfTest.git
cd halfTest/outputs/proj-2-7b10c0
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置（可选）

编辑 `config.json` 文件可以：

- 添加或删除RSS源
- 修改输出目录
- 调整超时和重试设置

## 使用方法

### 立即运行一次

```bash
python ai_news_aggregator.py
```

运行后会生成 `ai_news_report_YYYYMMDD.md` 文件。

### 启动定时任务

```bash
python scheduler.py
```

定时任务会：
- 每天上午9:00执行一次
- 每天晚上6:00执行一次
- 立即执行一次测试运行

生成的Markdown文件保存在 `./output/` 目录中。

## 输出示例

生成的Markdown文件格式如下：

```markdown
# AI News Aggregator Report

*生成时间: 2024-01-15 14:30:00*
*共收集 12 篇文章*

---

## 2024-01-15

### 1. OpenAI发布新模型

**来源:** [OpenAI Blog](https://openai.com/blog)
**发布时间:** 2024-01-15T10:00:00
**摘要:** OpenAI今天宣布发布了...

[阅读原文](https://openai.com/blog/new-model)

---
```

## 配置文件说明

`config.json` 结构：

```json
{
  "rss_feeds": [
    "https://example.com/feed.xml"
  ],
  "settings": {
    "output_directory": "./output",
    "log_level": "INFO",
    "fetch_timeout": 30,
    "max_retries": 3
  }
}
```

## 运行测试

```bash
python test_aggregator.py
```

## 日志文件

- `ai_news_aggregator.log` - 聚合器运行日志
- `scheduler.log` - 定时任务日志

## 技术栈

- Python 3.7+
- feedparser - RSS解析
- requests - HTTP请求
- schedule - 定时任务
- urllib3 - 连接池和重试

## 故障排除

### RSS源无法访问

1. 检查网络连接
2. 验证RSS源URL是否有效
3. 查看日志文件中的详细错误信息

### 安装依赖失败

1. 确保使用Python 3.7+
2. 尝试更新pip: `pip install --upgrade pip`
3. 使用虚拟环境: `python -m venv venv`

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License