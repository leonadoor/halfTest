# AI新闻RSS源需求分析和清单整理

## 需求分析

### 核心需求
- 自动拉取AI相关新闻的RSS源
- 提取标题和链接信息
- 生成格式化的Markdown文件
- 每日自动执行

### RSS源分类标准
1. **主流AI新闻媒体** - 专注AI领域的大型媒体平台
2. **技术博客** - 科技公司官方博客和技术博主
3. **研究机构** - 知名AI研究机构的官方发布渠道

## AI新闻RSS源清单

### 主流AI新闻媒体

#### 1. AI垂直媒体
- **MIT Technology Review AI**
  - RSS: https://www.technologyreview.com/topic/artificial-intelligence/feed/
  - 特点：权威技术媒体，AI报道深入

- **VentureBeat AI**
  - RSS: https://venturebeat.com/tag/ai/feed/
  - 特点：关注AI商业应用和创业

- **TechCrunch AI**
  - RSS: https://techcrunch.com/tag/artificial-intelligence/feed/
  - 特点：科技新闻，AI领域覆盖全面

- **The Verge AI**
  - RSS: https://www.theverge.com/rss/artificial-intelligence/index.xml
  - 特点：科技文化，AI产品和技术报道

#### 2. 综合科技媒体AI板块
- **Wired AI**
  - RSS: https://www.wired.com/tag/ai/feed/
  - 特点：深度报道，技术文化结合

### 技术博客

#### 1. 科技巨头官方博客
- **OpenAI Blog**
  - RSS: https://openai.com/blog/rss.xml
  - 特点：前沿AI研究成果和产品开发

- **Google DeepMind Blog**
  - RSS: https://deepmind.google/blog/feed/
  - 特点：Google AI研究成果

- **Microsoft AI Blog**
  - RSS: https://blogs.microsoft.com/ai/feed/
  - 特点：微软AI技术和产品

- **Meta AI Blog**
  - RSS: https://ai.meta.com/blog/feed/
  - 特点：Meta AI研究和应用

#### 2. 专业AI技术博客
- **Towards Data Science**
  - RSS: https://towardsdatascience.com/feed
  - 特点：数据科学和AI技术教程

- **KDnuggets**
  - RSS: https://www.kdnuggets.com/feed
  - 特点：数据科学、机器学习和AI

### 研究机构

#### 1. 顶级研究机构
- **Stanford AI Lab**
  - RSS: https://ai.stanford.edu/rss.xml
  - 特点：学术研究，前沿探索

- **MIT CSAIL**
  - RSS: https://www.csail.mit.edu/rss.xml
  - 特点：计算机科学和AI研究

- **CMU AI**
  - RSS: https://www.ml.cmu.edu/rss.xml
  - 特点：机器学习和AI研究

#### 2. 预印本平台
- **arXiv AI**
  - RSS: https://arxiv.org/rss/cs.AI
  - 特点：最新AI研究论文

- **arXiv Machine Learning**
  - RSS: https://arxiv.org/rss/stat.ML
  - 特点：机器学习研究论文

## RSS源质量评估标准

### 优先级排序
1. **更新频率** - 每日/每周更新
2. **内容质量** - 原创性、深度、准确性
3. **权威性** - 机构背景、作者资质
4. **稳定性** - RSS feed的可用性
5. **覆盖范围** - AI相关内容的比例

### 推荐核心源列表（Top 10）
1. OpenAI Blog - 前沿研究
2. MIT Technology Review AI - 深度报道
3. Google DeepMind Blog - 大公司研发
4. arXiv AI - 最新论文
5. VentureBeat AI - 商业应用
6. Towards Data Science - 技术教程
7. Microsoft AI Blog - 工业应用
8. TechCrunch AI - 行业新闻
9. Stanford AI Lab - 学术研究
10. KDnuggets - 数据科学

## 实施建议

### 技术选型
- 使用 `feedparser` 库解析RSS
- 使用 `requests` 库获取feed内容
- 定时任务使用 `schedule` 或系统cron
- Markdown模板化生成

### 数据结构设计
```python
class NewsItem:
    title: str
    link: str
    source: str
    published_date: datetime
    summary: str = ""
```

### 错误处理
- RSS feed不可用时的重试机制
- 网络请求超时处理
- 内容解析异常捕获
- 重复内容过滤