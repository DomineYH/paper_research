# 연구 파이프라인 작업 템플릿

## 작업 1: arXiv 수집/요약
- 저장 위치: `paper_research/arxiv_paper/{YYYY-MM-DD}.md`
- 주제군: prompt/reverse prompt/data science/ai agent/context engineering (확장 가능)
- 선편 수: 약 10편
- 포맷:
  - 제목: [논문 제목] (#해시태그)
  - 요약: 500자 내외
  - 핵심 기여
  - 링크: [arXiv 링크]
  - DOI: (확인 가능 시)
  - 키워드: #해시태그

## 작업 2: 국내 논문 수집/요약
- 저장 위치: `paper_research/kr_paper/{YYYY-MM-DD}.md`
- 소스: RISS, DBpia, Google Scholar, KCI
- 선정 기준: KCI급 이상 논문 및 박사학위 논문 우선
- 포맷: 동일

## 작업 3: 심층 연구 보고서
- 저장 위치: `paper_research/research_reports/{YYYY-MM-DD}.md`
- 근거: 당일 수집 논문(arXiv + KR)
- 분석 각도: 이론/방법/평가/윤리/산업
- 형식: 엄밀 인용 + APA 참고문헌

## 작업 4: GitHub 반영
- 작업 디렉토리: `paper_research/`
- 명령어 순서:
  1. cd paper_research
  2. git add .
  3. git commit -m "Update research papers - {YYYY-MM-DD}"
  4. git push
- 주의: 변경 없으면 push 생략

## 출력 포맷 (Discord)
1) `연구 파이프라인 완료: 성공 | 부분성공 | 실패`
2) `GitHub push: 성공 | 변경없음 | 실패`
3) `오늘 확장 주제: ...`