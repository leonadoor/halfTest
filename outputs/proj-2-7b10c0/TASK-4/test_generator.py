#!/usr/bin/env python3
"""
Test script for TASK-4 Markdown Generator
Demonstrates the enhanced Markdown generation functionality.
"""

import json
from datetime import datetime, timedelta
from markdown_generator import TASK4MarkdownGenerator


def create_sample_articles():
    """Create sample articles for testing."""
    articles = []

    # Create articles with different dates and categories
    base_date = datetime.now()

    # AI Research articles
    articles.append({
        "title": "OpenAI Releases GPT-4.5 with Enhanced Reasoning",
        "link": "https://openai.com/blog/gpt-4-5",
        "published_at": (base_date - timedelta(hours=2)).isoformat(),
        "summary": "OpenAI introduces GPT-4.5, featuring improved reasoning capabilities and better understanding of complex instructions. The new model shows significant improvements in mathematical reasoning and code generation tasks.",
        "source_name": "OpenAI Blog",
        "source_url": "https://openai.com/blog",
        "category": "Research",
        "priority": 10
    })

    articles.append({
        "title": "DeepMind's AlphaFold 3 Predicts Protein Interactions",
        "link": "https://deepmind.com/blog/alphafold-3",
        "published_at": (base_date - timedelta(hours=5)).isoformat(),
        "summary": "DeepMind releases AlphaFold 3, extending its protein structure prediction capabilities to model protein complexes and interactions, revolutionizing structural biology research.",
        "source_name": "DeepMind Blog",
        "source_url": "https://deepmind.com",
        "category": "Research",
        "priority": 9
    })

    # Industry News
    articles.append({
        "title": "Microsoft Announces Azure AI Copilot for Developers",
        "link": "https://azure.microsoft.com/blog/ai-copilot",
        "published_at": (base_date - timedelta(hours=1)).isoformat(),
        "summary": "Microsoft launches Azure AI Copilot, an AI-powered development assistant integrated with Visual Studio Code, offering intelligent code suggestions and debugging help.",
        "source_name": "Microsoft Azure Blog",
        "source_url": "https://azure.microsoft.com",
        "category": "Industry",
        "priority": 8
    })

    articles.append({
        "title": "Google Cloud AI Partnership with Anthropic",
        "link": "https://cloud.google.com/blog/anthropic-partnership",
        "published_at": (base_date - timedelta(hours=8)).isoformat(),
        "summary": "Google Cloud announces strategic partnership with Anthropic to bring Claude models to enterprise customers through Vertex AI platform.",
        "source_name": "Google Cloud Blog",
        "source_url": "https://cloud.google.com",
        "category": "Industry",
        "priority": 8
    })

    # Previous day articles
    articles.append({
        "title": "Meta Releases Llama 3 with Multilingual Support",
        "link": "https://ai.meta.com/blog/llama-3",
        "published_at": (base_date - timedelta(days=1, hours=3)).isoformat(),
        "summary": "Meta introduces Llama 3, supporting over 100 languages and featuring improved performance across translation and summarization tasks.",
        "source_name": "Meta AI Blog",
        "source_url": "https://ai.meta.com",
        "category": "Research",
        "priority": 9
    })

    return articles


def test_daily_report():
    """Test daily report generation."""
    print("Testing TASK-4 Markdown Generator - Daily Report\n")

    # Create sample articles
    articles_data = create_sample_articles()

    # Save to temporary JSON file
    input_file = "temp_articles.json"
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump({"articles": articles_data}, f, indent=2)

    # Generate daily report
    generator = TASK4MarkdownGenerator()
    output_file = "ai_news_daily_report.md"

    # Load articles
    from markdown_generator import Article
    articles = []
    for item in articles_data:
        article = Article(
            title=item["title"],
            link=item["link"],
            published_at=datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None,
            summary=item["summary"],
            source_name=item["source_name"],
            source_url=item["source_url"],
            category=item["category"],
            priority=item["priority"]
        )
        articles.append(article)

    # Generate report
    content = generator.generate_daily_report(articles)
    saved_path = generator.save_report(content, output_file)

    print(f"Daily report generated: {saved_path}")
    print(f"Articles processed: {len(articles)}")
    return saved_path


def test_weekly_report():
    """Test weekly report generation."""
    print("\nTesting TASK-4 Markdown Generator - Weekly Report\n")

    # Create sample articles spanning a week
    articles_data = create_sample_articles()

    # Generate weekly report
    generator = TASK4MarkdownGenerator()
    output_file = "ai_news_weekly_report.md"

    from markdown_generator import Article
    articles = []
    for item in articles_data:
        article = Article(
            title=item["title"],
            link=item["link"],
            published_at=datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None,
            summary=item["summary"],
            source_name=item["source_name"],
            source_url=item["source_url"],
            category=item["category"],
            priority=item["priority"]
        )
        articles.append(article)

    # Generate weekly report
    content = generator.generate_weekly_report(articles)
    saved_path = generator.save_report(content, output_file)

    print(f"Weekly report generated: {saved_path}")
    return saved_path


def demonstrate_features():
    """Demonstrate TASK-4 specific features."""
    print("\nTASK-4 Feature Demonstration\n")

    print("1. Enhanced Date Organization")
    print("   - Articles grouped by publication date")
    print("   - Chronological and reverse-chronological sorting")
    print("   - Date-based section headers")

    print("\n2. Rich Metadata Formatting")
    print("   - Title with clickable links")
    print("   - Publication time display")
    print("   - Category tags")
    print("   - Source attribution")

    print("\n3. Smart Summary Handling")
    print("   - Formatted block quotes")
    print("   - Line limit with truncation")
    print("   - Proper indentation")

    print("\n4. Executive Summary")
    print("   - Category breakdown")
    print("   - Article counts")
    print("   - Source statistics")

    print("\n5. Multiple Report Formats")
    print("   - Daily digest format")
    print("   - Weekly summary format")
    print("   - Customizable templates")


def main():
    """Main test function."""
    print("=" * 60)
    print("TASK-4 Markdown Generator Test Suite")
    print("=" * 60)

    try:
        # Run tests
        daily_path = test_daily_report()
        weekly_path = test_weekly_report()

        # Demonstrate features
        demonstrate_features()

        # Clean up temporary files
        import os
        temp_files = ["temp_articles.json"]
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)

        print("\n" + "=" * 60)
        print("TASK-4 Test Suite Completed Successfully")
        print("=" * 60)
        print(f"\nReports generated:")
        print(f"   - Daily: {daily_path}")
        print(f"   - Weekly: {weekly_path}")

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())