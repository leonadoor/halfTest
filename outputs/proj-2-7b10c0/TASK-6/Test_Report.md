# TASK-6 Test Plan and Coverage

## Scope

This task validates the core AI News Aggregator pipeline delivered in previous tasks:

- RSS fetching retry behavior
- RSS/Atom parsing and malformed input handling
- article normalization and date parsing
- article filtering for age, missing fields, and summary requirements
- duplicate removal by URL and title similarity
- Markdown rendering for TASK-3 and TASK-4 outputs
- end-to-end job execution using `JobRunner`

## Test Structure

- `tests/test_rss_pipeline.py`: unit tests for TASK-3 components plus one integration test for `JobRunner`
- `tests/test_task4_markdown.py`: focused tests for TASK-4 report rendering and file output
- `run_tests.py`: standard-library test runner

## Covered Boundary and Error Cases

- network request failures with retry backoff and final `None` result
- malformed or non-XML feed content
- missing title or invalid link in parsed entries
- unsupported publish-date formats
- old articles falling outside the lookback window
- missing summaries when summary is required
- duplicate URLs and near-duplicate titles from different feeds
- long Markdown summaries that require truncation
- duplicate article URLs in TASK-4 daily digest generation

## Execution

Run the test suite from the repository root:

```bash
python outputs/proj-2-7b10c0/TASK-6/run_tests.py
```

The suite uses only the Python standard library for test execution. It assumes the upstream runtime dependencies from TASK-3 and TASK-4, such as `requests` and `feedparser`, are already available.
