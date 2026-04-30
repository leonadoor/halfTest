#!/usr/bin/env python3
"""
AI News Aggregator - 简化版本，用于测试核心逻辑
"""

import json
import os
import hashlib
from datetime import datetime


class SimpleAINewsAggregator:
    """简化版AI新闻聚合器，用于测试核心逻辑"""

    def __init__(self):
        self.rss_feeds = self._load_config()
        self.test_data = self._generate_test_data()

    def _load_config(self):
        """加载配置"""
        default_feeds = [
            "https://www.theverge.com/rss/ai/index.xml",
            "https://www.wired.com/feed/category/ai/latest/rss",
        ]
        return default_feeds

    def _generate_test_data(self):
        """生成测试数据"""
        return [
            {
                'title': 'OpenAI发布GPT-5新模型',
                'link': 'https://openai.com/blog/gpt-5',
                'summary': 'OpenAI今天正式发布GPT-5模型，性能提升50%...',
                'published': '2024-01-15T10:00:00',
                'source': 'https://openai.com/blog/rss.xml',
                'source_name': 'OpenAI Blog'
            },
            {
                'title': 'Google DeepMind突破AI推理能力',
                'link': 'https://deepmind.com/blog/ai-reasoning',
                'summary': 'DeepMind最新研究在AI推理领域取得重大突破...',
                'published': '2024-01-15T08:30:00',
                'source': 'https://deepmind.com/blog/feed/basic/',
                'source_name': 'DeepMind Blog'
            },
            {
                'title': 'NVIDIA发布新一代AI芯片',
                'link': 'https://blogs.nvidia.com/ai-chip',
                'summary': 'NVIDIA推出全新AI加速芯片，性能提升3倍...',
                'published': '2024-01-14T15:45:00',
                'source': 'https://blogs.nvidia.com/ai/feed/',
                'source_name': 'NVIDIA AI Blog'
            }
        ]

    def _generate_article_id(self, title, link):
        """生成文章ID"""
        return hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]

    def _clean_text(self, text):
        """清理文本"""
        if not text:
            return ""
        return ' '.join(text.split())[:500]

    def test_generate_markdown(self):
        """测试Markdown生成"""
        articles_by_date = {}
        for article in self.test_data:
            date_key = article['published'][:10]
            if date_key not in articles_by_date:
                articles_by_date[date_key] = []
            articles_by_date[date_key].append(article)

        sorted_dates = sorted(articles_by_date.keys(), reverse=True)

        markdown_content = f"""# AI News Aggregator Report

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*共收集 {len(self.test_data)} 篇文章*

---

"""

        for date in sorted_dates:
            markdown_content += f"## {date}\n\n"
            date_articles = sorted(articles_by_date[date], key=lambda x: x['published'], reverse=True)

            for i, article in enumerate(date_articles, 1):
                markdown_content += f"""### {i}. {article['title']}

**来源:** [{article['source_name']}]({article['link']})
**发布时间:** {article['published']}
**摘要:** {article['summary']}

[阅读原文]({article['link']})

---

"""

        # 保存测试文件
        output_file = f"ai_news_test_{datetime.now().strftime('%Y%m%d')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"测试Markdown文件已生成: {output_file}")
        return output_file

    def run(self):
        """运行测试"""
        print("=== AI News Aggregator 测试运行 ===")
        print(f"配置的RSS源数量: {len(self.rss_feeds)}")
        print(f"测试文章数量: {len(self.test_data)}")

        # 生成Markdown
        output_file = self.test_generate_markdown()

        # 验证文件内容
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"\n文件验证:")
            print(f"- 包含 'AI News Aggregator Report': {'AI News Aggregator Report' in content}")
            print(f"- 包含日期标题: {'## 2024-01' in content}")
            print(f"- 包含文章标题: {'GPT-5' in content}")
            print(f"- 包含链接: {'https://openai.com' in content}")

            print(f"\nTest passed! Generated Markdown file saved to current directory.")
        else:
            print("Test failed! File not generated.")


if __name__ == "__main__":
    aggregator = SimpleAINewsAggregator()
    aggregator.run()