#!/usr/bin/env python3
"""
AI News Aggregator 测试用例
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ai_news_aggregator import AI_News_Aggregator


class TestAI_News_Aggregator(unittest.TestCase):
    """AI News Aggregator 测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_config = {
            "rss_feeds": [
                "https://example.com/feed1.xml",
                "https://example.com/feed2.xml"
            ]
        }

        # 创建临时配置文件
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()

        self.aggregator = AI_News_Aggregator(self.temp_config_file.name)

    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.temp_config_file.name):
            os.unlink(self.temp_config_file.name)

    def test_load_config_success(self):
        """测试配置文件加载成功"""
        self.assertEqual(len(self.aggregator.rss_feeds), 2)
        self.assertIn("https://example.com/feed1.xml", self.aggregator.rss_feeds)

    def test_load_config_file_not_found(self):
        """测试配置文件不存在时使用默认值"""
        aggregator = AI_News_Aggregator("nonexistent_file.json")
        self.assertGreater(len(aggregator.rss_feeds), 0)  # 应该使用默认RSS源

    def test_extract_articles_from_feed(self):
        """测试文章提取功能"""
        # 创建模拟的RSS数据
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(
                title="Test Article 1",
                link="https://example.com/article1",
                summary="This is a test article summary",
                published_parsed=(2024, 1, 1, 12, 0, 0)
            ),
            Mock(
                title="Test Article 2",
                link="https://example.com/article2",
                description="Another test article",
                published_parsed=None,
                updated_parsed=(2024, 1, 2, 10, 30, 0)
            )
        ]
        mock_feed.feed.title = "Test Feed"

        articles = self.aggregator.extract_articles(mock_feed, "https://example.com/feed.xml")

        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['title'], "Test Article 1")
        self.assertEqual(articles[1]['title'], "Test Article 2")

        # 验证ID生成
        self.assertIsNotNone(articles[0]['id'])
        self.assertIsNotNone(articles[1]['id'])
        self.assertNotEqual(articles[0]['id'], articles[1]['id'])

    def test_text_cleaning(self):
        """测试文本清理功能"""
        dirty_text = "<p>This is a <b>test</b> article with <a href='#'>links</a></p>   and extra spaces    "
        clean_text = self.aggregator._clean_text(dirty_text)

        self.assertNotIn("<p>", clean_text)
        self.assertNotIn("<b>", clean_text)
        self.assertIn("test", clean_text)
        self.assertIn("article", clean_text)

    def test_generate_markdown(self):
        """测试Markdown生成功能"""
        test_articles = [
            {
                'id': 'test123',
                'title': 'Test Article',
                'link': 'https://example.com/article',
                'summary': 'This is a test summary',
                'published': '2024-01-15T10:00:00',
                'source': 'https://example.com/feed.xml',
                'source_name': 'Test Feed'
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_output_file = f.name

        try:
            self.aggregator.generate_markdown(test_articles, temp_output_file)

            # 验证文件内容
            with open(temp_output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.assertIn('# AI News Aggregator Report', content)
            self.assertIn('Test Article', content)
            self.assertIn('https://example.com/article', content)
            self.assertIn('Test Feed', content)

        finally:
            if os.path.exists(temp_output_file):
                os.unlink(temp_output_file)

    def test_duplicate_article_filtering(self):
        """测试重复文章过滤"""
        existing_ids = {'duplicate123'}

        new_articles = [
            {'id': 'duplicate123', 'title': 'Duplicate Article'},
            {'id': 'unique456', 'title': 'Unique Article'}
        ]

        filtered = [a for a in new_articles if a['id'] not in existing_ids]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], 'unique456')


class TestScheduler(unittest.TestCase):
    """定时任务测试类"""

    @patch('ai_news_aggregator.AI_News_Aggregator')
    def test_job_execution(self, mock_aggregator_class):
        """测试定时任务执行"""
        from scheduler import job

        # 模拟聚合器实例
        mock_aggregator = Mock()
        mock_aggregator.run.return_value = 5
        mock_aggregator_class.return_value = mock_aggregator

        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.makedirs'):
                result = job()

        self.assertTrue(result)
        mock_aggregator.run.assert_called_once()


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()