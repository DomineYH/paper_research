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
  - arXiv recent papers, target ~10 papers/day
  - 각 논문별: 500자 내외 요약 + 핵심기여 + 링크 + 핵심키워드 해시태그
- `kr_paper/YYYY-MM-DD.md`
  - 수집 소스: RISS, DBpia, Google Scholar, KCI
  - 선정 조건: KCI급 이상 논문 및 박사학위 논문 우선
  - 각 논문별: 500자 내외 요약 + 핵심기여 + 링크 + 핵심키워드 해시태그
- `research_reports/YYYY-MM-DD.md`
  - 박사과정 수준의 심층 보고서 (다각도: 이론/방법/평가/윤리/산업적 함의)
  - 엄밀 인용 포맷 + APA 참고문헌 포함

## Quality requirements (mandatory)
1. 중복 제거: 동일 논문(abs/pdf/html 버전) 1건만 유지
2. DOI 강화: DOI 확인 가능한 경우 본문 및 참고문헌에 명시
3. 엄밀 인용 포맷: 본문 인용과 참고문헌 일치
4. APA 인용: 참고문헌 섹션을 APA 형식으로 작성
5. 모든 주장에 출처 연결(검증 불가 시 명시)

## OpenClaw cron intent
Recommended cron expression (KST runtime):
- `0 9 * * *`

## Execution flow per run
1. arXiv digest collection + dedup + DOI/APA formatting
2. KR paper collection (RISS/DBpia/Google Scholar/KCI) + quality filter
3. deep research report generation (PhD-level topic)
4. write outputs into the three folders
5. append run log to `paper_research/run_logs/YYYY-MM-DD.log`