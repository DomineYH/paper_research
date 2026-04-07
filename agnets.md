# agnets.md

## Daily Research Pipeline Rules (KST 09:00)

### 1) Topic Operation (Dynamic)
- 기본 앵커 주제:
  - prompt
  - reverse prompt
  - data science
  - ai agent
  - context engineering
- 고정 주제만 사용하지 않는다.
- 매일 실행 시 최신 동향 기반 확장 주제 2~5개를 먼저 제안하고 연구 범위에 포함한다.
- 확장 주제 예시:
  - AI safety / evals
  - agent memory
  - tool-use reliability
  - multimodal agents
  - RAG evaluation
  - synthetic data quality
  - LLM observability

### 2) arXiv Output Rule
- 파일: `paper_research/arxiv_paper/{YYYY-MM-DD}.md`
- 목표: 당일 주제군 기준 약 10편
- 각 논문별 필수 항목:
  - 500자 내외 요약
  - 핵심기여
  - 링크
  - 핵심키워드 해시태그
  - DOI(확인 가능 시)
- abs/pdf/html 중복은 1건만 유지

### 3) KR Paper Output Rule
- 파일: `paper_research/kr_paper/{YYYY-MM-DD}.md`
- 수집 소스:
  - RISS
  - DBpia
  - Google Scholar
  - KCI
- 선정 기준:
  - KCI급 이상 논문 우선
  - 박사학위논문 우선
- 각 논문별 필수 항목:
  - 500자 내외 요약
  - 핵심기여
  - 링크
  - 핵심키워드 해시태그
  - DOI(확인 가능 시)

### 4) Research Report Rule (핵심)
- 파일: `paper_research/research_reports/{YYYY-MM-DD}.md`
- 반드시 당일 수집한 논문(arXiv + KR)을 근거로 작성한다.
- 박사학위급 연구 주제를 1개 이상 도출한다.
- 보고서는 다각도 분석을 포함한다:
  - 이론
  - 방법
  - 평가
  - 윤리
  - 산업적 함의
- 본문 인용은 엄밀 포맷으로 작성한다.
- 참고문헌은 APA 형식으로 작성한다.

### 5) Global Quality Rules
- 모든 주장에 출처를 연결한다.
- 검증 불가 항목은 불확실성으로 명시한다.
- 중복 제거를 항상 수행한다.
- DOI를 가능한 범위에서 강화한다.
- 인용 형식 일치(본문 인용 ↔ 참고문헌)를 점검한다.

### 6) Skill Usage Priority
- 관련 스킬을 우선 활용한다.
  - deep-research-pro
  - agentic-paper-digest-skill

### 7) Result Reporting Rule
- 실행 결과는 채널에 간결하게 보고한다.
- 보고 시 `오늘 제안/채택한 확장 주제`를 1줄 포함한다.
