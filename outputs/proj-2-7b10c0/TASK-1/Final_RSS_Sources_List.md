# AI新闻RSS源最终清单

## 精选RSS源列表（已验证有效）

### 一、高质量AI新闻源（推荐优先级排序）

#### 1. 前沿研究类
- **OpenAI Blog** ⭐⭐⭐⭐⭐
  - URL: https://openai.com/blog/rss.xml
  - 内容：928篇文章，前沿AI研究成果
  - 更新频率：活跃
  - 特点：权威、及时、深度

- **arXiv AI (cs.AI)** ⭐⭐⭐⭐⭐
  - URL: https://arxiv.org/rss/cs.AI
  - 内容：229篇文章，最新AI研究论文
  - 更新频率：每日
  - 特点：学术性、前沿性

- **arXiv Machine Learning (stat.ML)** ⭐⭐⭐⭐⭐
  - URL: https://arxiv.org/rss/stat.ML
  - 内容：34篇文章，机器学习论文
  - 更新频率：每日
  - 特点：专业性强

#### 2. 主流媒体AI报道
- **TechCrunch AI** ⭐⭐⭐⭐
  - URL: https://techcrunch.com/tag/artificial-intelligence/feed/
  - 内容：20篇文章，AI行业新闻
  - 更新频率：高
  - 特点：覆盖面广、时效性强

- **MIT Technology Review AI** ⭐⭐⭐⭐
  - URL: https://www.technologyreview.com/topic/artificial-intelligence/feed/
  - 内容：10篇文章，深度AI报道
  - 更新频率：中
  - 特点：权威、深度

- **The Verge AI** ⭐⭐⭐
  - URL: https://www.theverge.com/rss/artificial-intelligence/index.xml
  - 内容：0篇文章（暂无内容）
  - 状态：需要监控

#### 3. 技术教程与实践
- **Towards Data Science** ⭐⭐⭐⭐
  - URL: https://towardsdatascience.com/feed
  - 内容：20篇文章，数据科学和AI教程
  - 更新频率：高
  - 特点：实用性强、易理解

- **KDnuggets** ⭐⭐⭐⭐
  - URL: https://www.kdnuggets.com/feed
  - 内容：10篇文章，数据科学和机器学习
  - 更新频率：中
  - 特点：专业性强

#### 4. 企业AI应用
- **Microsoft AI Blog** ⭐⭐⭐
  - URL: https://blogs.microsoft.com/ai/feed/
  - 内容：10篇文章，微软AI技术和产品
  - 更新频率：较低
  - 特点：工业应用导向

- **MIT CSAIL** ⭐⭐⭐
  - URL: https://www.csail.mit.edu/rss.xml
  - 内容：9篇文章，MIT计算机科学和AI研究
  - 更新频率：低
  - 特点：学术性强

## 替代源建议（原无效源的替代方案）

### 替换建议

1. **替代 VentureBeat AI**
   - 推荐：**Synced AI**
   - URL: https://syncedreview.com/feed/
   - 理由：专注AI行业，更新频繁

2. **替代 Google DeepMind Blog**
   - 推荐：**Google AI Blog**
   - URL: https://ai.googleblog.com/feeds/posts/default
   - 理由：Google官方AI博客

3. **替代 Meta AI Blog**
   - 推荐：**Meta Research**
   - URL: https://research.fb.com/feed/
   - 理由：Meta官方研究博客

4. **替代 Wired AI**
   - 推荐：**VentureBeat Transform**
   - URL: https://venturebeat.com/category/transform/feed/
   - 理由：AI和数字化转型专业报道

## 核心推荐源（Top 10）

基于验证结果，推荐以下10个RSS源作为AI新闻聚合器的核心数据源：

1. **https://openai.com/blog/rss.xml** - OpenAI官方博客
2. **https://arxiv.org/rss/cs.AI** - arXiv AI论文
3. **https://arxiv.org/rss/stat.ML** - arXiv机器学习论文
4. **https://techcrunch.com/tag/artificial-intelligence/feed/** - TechCrunch AI
5. **https://www.technologyreview.com/topic/artificial-intelligence/feed/** - MIT TR AI
6. **https://towardsdatascience.com/feed** - Towards Data Science
7. **https://www.kdnuggets.com/feed** - KDnuggets
8. **https://blogs.microsoft.com/ai/feed/** - Microsoft AI Blog
9. **https://ai.googleblog.com/feeds/posts/default** - Google AI Blog（新增）
10. **https://syncedreview.com/feed/** - Synced AI（新增）

## 实施注意事项

### 数据源管理策略
- **主源**：前6个高质量源
- **备用源**：后4个补充源
- **监控策略**：定期检查所有源的可用性

### 更新频率配置
- arXiv源：每4小时检查一次（每日更新）
- 主流媒体：每6小时检查一次
- 企业博客：每天检查一次
- 教程博客：每天检查一次

### 错误处理
- 单源失败不影响整体运行
- 记录失败日志，便于维护
- 设置自动重试机制（最多3次）
- 备用源自动切换

### 内容过滤建议
- 按发布时间筛选（仅获取24小时内内容）
- 关键词过滤（AI、machine learning、deep learning等）
- 去重处理（相同标题或相似内容）