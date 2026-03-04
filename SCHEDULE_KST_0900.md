# Daily Schedule Spec (KST 09:00)

- Time: Every day 09:00 KST
- Topics (fixed):
  1. prompt
  2. reverse prompt
  3. data science
  4. ai agent
  5. context engineering

## Job outputs
- `arxiv_paper/YYYY-MM-DD.md`
  - arXiv recent papers, target ~10 papers/day (roughly 2 per topic)
  - short summary + key contribution + link
- `kr_paper/YYYY-MM-DD.md`
  - KCI 중심 국내 논문 요약 (필요 시 KISS/DBpia/RISS 보조)
  - topic mapping + link
- `research_reports/YYYY-MM-DD.md`
  - 박사과정 수준의 심층 보고서 (다각도: 이론/방법/평가/윤리/산업적 함의)

## OpenClaw cron intent
Because this sandbox cannot run host `openclaw` or `crontab`, apply scheduling from host runtime.

Recommended cron expression (KST runtime):
- `0 9 * * *`

If host timezone is UTC, use:
- `0 0 * * *` (== 09:00 KST)

## Execution flow per run
1. arXiv digest skill execution
2. KR paper collection/summarization
3. deep research report generation
4. write outputs into the three folders
5. append run log to `paper_research/run_logs/YYYY-MM-DD.log`
