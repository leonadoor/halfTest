#!/usr/bin/env python3
"""
RSS源验证脚本
用于验证RSS源的有效性和可用性
"""

import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import time

class RSSValidator:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.results = []

    def validate_feed(self, name: str, url: str) -> Dict:
        """验证单个RSS源"""
        print(f"正在验证: {name} - {url}")

        result = {
            "name": name,
            "url": url,
            "valid": False,
            "status_code": None,
            "error": None,
            "title": None,
            "entries_count": 0,
            "last_updated": None,
            "response_time": None
        }

        try:
            # 记录响应时间
            start_time = time.time()

            # 使用feedparser解析RSS
            feed = feedparser.parse(url)

            response_time = time.time() - start_time
            result["response_time"] = round(response_time, 2)

            # 检查HTTP状态
            if hasattr(feed, 'status'):
                result["status_code"] = feed.status

            # 检查是否解析成功
            if feed.bozo:
                result["error"] = f"RSS解析错误: {feed.bozo_exception}"
                return result

            # 填充成功信息
            result["valid"] = True
            result["title"] = getattr(feed.feed, 'title', 'Unknown')
            result["entries_count"] = len(feed.entries)

            # 获取最后更新时间
            if hasattr(feed.feed, 'updated'):
                result["last_updated"] = feed.feed.updated
            elif feed.entries:
                # 使用最新条目的发布时间
                latest_entry = max(feed.entries,
                                 key=lambda e: getattr(e, 'published_parsed', (1970, 1, 1, 0, 0, 0, 0, 0, 0)))
                if hasattr(latest_entry, 'published_parsed') and latest_entry.published_parsed:
                    result["last_updated"] = time.strftime('%Y-%m-%d %H:%M:%S', latest_entry.published_parsed)

            print(f"[OK] 验证通过: {result['title']} ({result['entries_count']}篇文章)")

        except requests.exceptions.Timeout:
            result["error"] = "请求超时"
            print(f"[TIMEOUT] 请求超时: {url}")
        except requests.exceptions.ConnectionError:
            result["error"] = "连接错误"
            print(f"[CONN ERROR] 连接错误: {url}")
        except Exception as e:
            result["error"] = str(e)
            print(f"[ERROR] 验证失败: {str(e)}")

        return result

    def validate_list(self, rss_list: List[Dict[str, str]]) -> List[Dict]:
        """验证RSS源列表"""
        print(f"\n开始验证 {len(rss_list)} 个RSS源...\n")

        for rss_item in rss_list:
            result = self.validate_feed(rss_item["name"], rss_item["url"])
            self.results.append(result)
            time.sleep(1)  # 避免请求过于频繁

        return self.results

    def generate_report(self) -> str:
        """生成验证报告"""
        if not self.results:
            return "没有验证结果"

        total = len(self.results)
        valid = sum(1 for r in self.results if r["valid"])
        invalid = total - valid

        report = f"""# RSS源验证报告

## 统计信息
- 总计验证: {total} 个RSS源
- 有效源: {valid} 个 ({valid/total*100:.1f}%)
- 无效源: {invalid} 个 ({invalid/total*100:.1f}%)

## 有效RSS源推荐

### 高质量源 (响应快、更新频繁)
"""

        # 筛选高质量源
        high_quality = [
            r for r in self.results
            if r["valid"] and r["response_time"] and r["response_time"] < 3 and r["entries_count"] > 0
        ]

        high_quality.sort(key=lambda x: (x["entries_count"], -x["response_time"]), reverse=True)

        for i, result in enumerate(high_quality[:10], 1):
            report += f"{i}. **{result['name']}**\n"
            report += f"   - URL: {result['url']}\n"
            report += f"   - 标题: {result['title']}\n"
            report += f"   - 文章数量: {result['entries_count']}\n"
            report += f"   - 响应时间: {result['response_time']}s\n"
            if result['last_updated']:
                report += f"   - 最后更新: {result['last_updated']}\n"
            report += "\n"

        if invalid > 0:
            report += f"""## 无效RSS源 ({invalid}个)

需要检查或替换的源：

"""
            for result in self.results:
                if not result["valid"]:
                    report += f"- **{result['name']}**\n"
                    report += f"  - URL: {result['url']}\n"
                    report += f"  - 错误: {result['error']}\n\n"

        return report


# 测试用的RSS源列表
test_rss_list = [
    # 主流AI新闻媒体
    {"name": "MIT Technology Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/tag/ai/feed/"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/tag/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/artificial-intelligence/index.xml"},
    {"name": "Wired AI", "url": "https://www.wired.com/tag/ai/feed/"},

    # 技术博客
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Google DeepMind Blog", "url": "https://deepmind.google/blog/feed/"},
    {"name": "Microsoft AI Blog", "url": "https://blogs.microsoft.com/ai/feed/"},
    {"name": "Meta AI Blog", "url": "https://ai.meta.com/blog/feed/"},
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed"},
    {"name": "KDnuggets", "url": "https://www.kdnuggets.com/feed"},

    # 研究机构
    {"name": "Stanford AI Lab", "url": "https://ai.stanford.edu/rss.xml"},
    {"name": "MIT CSAIL", "url": "https://www.csail.mit.edu/rss.xml"},
    {"name": "CMU AI", "url": "https://www.ml.cmu.edu/rss.xml"},
    {"name": "arXiv AI", "url": "https://arxiv.org/rss/cs.AI"},
    {"name": "arXiv Machine Learning", "url": "https://arxiv.org/rss/stat.ML"},
]

if __name__ == "__main__":
    validator = RSSValidator(timeout=30)
    validator.validate_list(test_rss_list)

    # 生成报告
    report = validator.generate_report()

    # 保存报告
    with open("rss_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n验证完成！报告已保存到: rss_validation_report.md")
    print(f"有效源: {sum(1 for r in validator.results if r['valid'])}/{len(validator.results)}")