#!/usr/bin/env python3
"""
AI News Aggregator Scheduler - 定时执行新闻聚合任务
"""

import logging
import schedule
import time
from ai_news_aggregator import AI_News_Aggregator
from datetime import datetime
import os


def setup_scheduler_logging():
    """设置定时任务的日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [Scheduler] - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scheduler.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def job():
    """定时执行的聚合任务"""
    logger = logging.getLogger(__name__)
    logger.info("开始执行定时任务")

    try:
        # 创建输出目录
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)

        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"ai_news_report_{timestamp}.md")

        # 运行聚合器
        aggregator = AI_News_Aggregator()
        article_count = aggregator.run(output_file=output_file)

        logger.info(f"定时任务完成！共收集 {article_count} 篇文章")
        return True

    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")
        return False


def main():
    """主函数 - 设置并运行定时任务"""
    logger = setup_scheduler_logging()

    # 设置定时任务（每天上午9点和下午6点执行）
    schedule.every().day.at("09:00").do(job)
    schedule.every().day.at("18:00").do(job)

    logger.info("AI新闻聚合定时任务已启动")
    logger.info("计划执行时间: 每天 09:00 和 18:00")

    # 立即执行一次（测试用）
    logger.info("立即执行第一次测试任务")
    job()

    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    main()