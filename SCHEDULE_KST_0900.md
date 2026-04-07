# Daily Schedule Spec (KST 09:00)

- Time: Every day 09:00 KST
- Topics (dynamic):
  - 기본 앵커: prompt, reverse prompt, data science, ai agent, context engineering
  - 매일 실행 시 최신 동향 기반 확장 주제 2~5개를 추가 제안 후 반영
  - 예시 확장 주제: AI safety/evals, agent memory, tool-use reliability, multimodal agents, RAG evaluation, synthetic data quality, LLM observability

## Job outputs
- `arxiv_paper/YYYY-MM-DD.md`
  - arXiv recent papers, target ~10 papers/day
  - 각 논문별: 500자 내외 요약 + 핵심기여 + 링크 + 핵심키워드 해시태그
- `kr_paper/YYYY-MM-DD.md`
  - 수집 소스: RISS, DBpia, Google Scholar, KCI
  - 선정 조건: KCI급 이상 논문 및 박사학위 논문 우선
  - 각 논문별: 500자 내외 요약 + 핵심기여 + 링크 + 핵심키워드 해시태그
- `research_reports/YYYY-MM-DD.md`
  - 당일 수집한 논문(arXiv + KR)을 근거로 박사학위급 연구 주제를 1개 이상 도출
  - 해당 주제로 심층 보고서 작성(다각도: 이론/방법/평가/윤리/산업적 함의)
  - 본문에서 당일 논문을 근거로 직접 인용하고, 엄밀 인용 포맷 + APA 참고문헌 포함

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