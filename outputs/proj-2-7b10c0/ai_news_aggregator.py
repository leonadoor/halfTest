#!/usr/bin/env python3
"""
AI News Aggregator - 自动抓取AI新闻RSS源并生成Markdown文件
"""

import feedparser
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AI_News_Aggregator:
    """AI新闻聚合器主类"""

    def __init__(self, config_file: str = "config.json"):
        """初始化聚合器"""
        self.config_file = config_file
        self.rss_feeds = self._load_config()
        self.setup_logging()
        self.session = self._setup_session()

    def _load_config(self) -> List[str]:
        """加载RSS源配置"""
        default_feeds = [
            # AI新闻源列表
            "https://www.theverge.com/rss/ai/index.xml",
            "https://www.wired.com/feed/category/ai/latest/rss",
            "https://venturebeat.com/ai/feed/",
            "https://www.technologyreview.com/ai/feed/",
            "https://ai.googleblog.com/feeds/posts/default",
            "https://openai.com/blog/rss.xml",
            "https://deepmind.com/blog/feed/basic/",
            "https://blogs.nvidia.com/ai/feed/"
        ]

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('rss_feeds', default_feeds)
            except Exception as e:
                logging.warning(f"加载配置文件失败: {e}, 使用默认RSS源")
                return default_feeds
        else:
            logging.info("配置文件不存在，使用默认RSS源")
            return default_feeds

    def _setup_session(self) -> requests.Session:
        """设置HTTP会话，包含重试机制"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_news_aggregator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_rss_feed(self, feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """获取RSS源内容"""
        try:
            self.logger.info(f"正在获取RSS源: {feed_url}")
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            return feedparser.parse(response.content)
        except Exception as e:
            self.logger.error(f"获取RSS源失败 {feed_url}: {e}")
            return None

    def extract_articles(self, feed_data: feedparser.FeedParserDict, feed_url: str) -> List[Dict]:
        """从RSS数据中提取文章信息"""
        articles = []
        if not feed_data or not feed_data.entries:
            self.logger.warning(f"RSS源没有文章条目: {feed_url}")
            return articles

        for entry in feed_data.entries:
            try:
                # 生成文章的唯一ID
                article_id = hashlib.md5(f"{entry.title}{entry.link}".encode()).hexdigest()[:12]

                # 提取发布时间
                published_time = self._extract_published_time(entry)

                article = {
                    'id': article_id,
                    'title': getattr(entry, 'title', '无标题'),
                    'link': getattr(entry, 'link', '#'),
                    'summary': self._clean_text(getattr(entry, 'summary', getattr(entry, 'description', ''))),
                    'published': published_time,
                    'source': feed_url,
                    'source_name': getattr(feed_data.feed, 'title', feed_url)
                }
                articles.append(article)
            except Exception as e:
                self.logger.error(f"提取文章信息失败: {e}")
                continue

        return articles

    def _extract_published_time(self, entry) -> str:
        """提取并格式化发布时间"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6]).isoformat()
            else:
                return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()

    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        # 移除HTML标签
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        clean_text = ' '.join(clean_text.split())
        # 限制长度
        return clean_text[:500] + "..." if len(clean_text) > 500 else clean_text

    def load_existing_articles(self, output_file: str) -> set:
        """加载已存在的文章ID"""
        existing_ids = set()
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单的ID提取逻辑
                    import re
                    ids = re.findall(r'data-article-id="([a-f0-9]+)"', content)
                    existing_ids.update(ids)
            except Exception as e:
                self.logger.warning(f"加载已存在文章ID失败: {e}")
        return existing_ids

    def generate_markdown(self, articles: List[Dict], output_file: str):
        """生成Markdown文件"""
        # 按日期分组文章
        articles_by_date = {}
        for article in articles:
            date_key = article['published'][:10]  # YYYY-MM-DD格式
            if date_key not in articles_by_date:
                articles_by_date[date_key] = []
            articles_by_date[date_key].append(article)

        # 按日期排序（最新的在前）
        sorted_dates = sorted(articles_by_date.keys(), reverse=True)

        markdown_content = f"""# AI News Aggregator Report

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*共收集 {len(articles)} 篇文章*

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

        # 保存Markdown文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        self.logger.info(f"Markdown文件已生成: {output_file}")

    def run(self, output_file: str = None):
        """运行聚合器"""
        if output_file is None:
            output_file = f"ai_news_report_{datetime.now().strftime('%Y%m%d')}.md"

        self.logger.info("开始运行AI新闻聚合器")
        all_articles = []
        seen_articles = self.load_existing_articles(output_file)

        for feed_url in self.rss_feeds:
            feed_data = self.fetch_rss_feed(feed_url)
            if feed_data:
                articles = self.extract_articles(feed_data, feed_url)
                # 去重
                new_articles = [a for a in articles if a['id'] not in seen_articles]
                all_articles.extend(new_articles)
                seen_articles.update([a['id'] for a in new_articles])
                self.logger.info(f"从 {feed_url} 获取了 {len(new_articles)} 篇新文章")

        if all_articles:
            self.generate_markdown(all_articles, output_file)
            self.logger.info(f"总计收集 {len(all_articles)} 篇新文章")
        else:
            self.logger.info("没有获取到新的文章")

        return len(all_articles)


def main():
    """主函数"""
    aggregator = AI_News_Aggregator()
    try:
        count = aggregator.run()
        print(f"AI新闻聚合完成！共收集 {count} 篇新文章。")
    except Exception as e:
        logging.error(f"运行失败: {e}")
        return 1
    return 0


if __name__ == "__main__":
    main()