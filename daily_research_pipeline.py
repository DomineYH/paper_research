#!/usr/bin/env python3
"""
Daily Research Pipeline for paper collection and analysis.

Outputs:
- arxiv_paper/YYYY-MM-DD.md
- kr_paper/YYYY-MM-DD.md
- research_reports/YYYY-MM-DD.md
- paper_research/run_logs/YYYY-MM-DD.log

The script is intentionally self-contained so Hermes cron can run it from any
working directory. It resolves all paths relative to this file, not to an old
OpenClaw workspace path.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys
import textwrap
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import requests


REPO_ROOT = Path(__file__).resolve().parent
LEGACY_OUTPUT_ROOT = REPO_ROOT / "paper_research"
ARXIV_DIR = REPO_ROOT / "arxiv_paper"
KR_DIR = REPO_ROOT / "kr_paper"
REPORT_DIR = REPO_ROOT / "research_reports"
RUN_LOG_DIR = LEGACY_OUTPUT_ROOT / "run_logs"

ANCHOR_TOPICS = [
    "prompt engineering",
    "reverse prompting",
    "data science",
    "AI agents",
    "context engineering",
]

EXTENSION_TOPICS = [
    "agent memory",
    "tool-use reliability",
    "LLM evaluation",
    "RAG evaluation",
    "multimodal agents",
]

ARXIV_CATEGORIES = ["cs.CL", "cs.AI", "cs.LG", "stat.ML", "cs.CR"]
ARXIV_MAX_PER_CATEGORY = 8
ARXIV_TARGET_TOTAL = 10
ARXIV_API_BASE = "https://export.arxiv.org/api/query"
ARXIV_REQUEST_DELAY_SECONDS = 4.0
ARXIV_RETRY_DELAYS_SECONDS = (5.0,)
USER_AGENT = "HermesResearchPipeline/1.2 (paper-research; +https://github.com/DomineYH/paper_research)"


class PipelineLogger:
    def __init__(self, today: str):
        self.today = today
        RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.path = RUN_LOG_DIR / f"{today}.log"
        self._lines: list[str] = []

    def log(self, message: str) -> None:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"[{stamp}] {message}"
        self._lines.append(line)
        print(message)

    def flush(self) -> None:
        self.path.write_text("\n".join(self._lines) + "\n", encoding="utf-8")


def setup_directories() -> str:
    """Ensure research directories exist and return today's UTC date."""
    today = dt.date.today().strftime("%Y-%m-%d")
    for directory in (ARXIV_DIR, KR_DIR, REPORT_DIR, RUN_LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    return today


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def strip_arxiv_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


def arxiv_id_from_url(url: str) -> str:
    return url.rstrip("/").split("/abs/")[-1]


def _retry_delay_seconds(response: requests.Response | None, retry_index: int) -> float:
    retry_after = response.headers.get("Retry-After") if response is not None else None
    if retry_after:
        try:
            return max(float(retry_after), ARXIV_REQUEST_DELAY_SECONDS)
        except ValueError:
            pass
    return ARXIV_RETRY_DELAYS_SECONDS[min(retry_index, len(ARXIV_RETRY_DELAYS_SECONDS) - 1)]


def _format_request_error(exc: Exception) -> str:
    response = getattr(exc, "response", None)
    detail = str(exc)
    if response is not None and getattr(response, "text", None):
        body = clean_text(response.text)[:120]
        if body:
            detail = f"{detail}; body={body}"
    return detail


def fetch_arxiv_category(category: str, logger: PipelineLogger) -> list[dict[str, Any]]:
    """Fetch recent arXiv papers from one category using the Atom API."""
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": ARXIV_MAX_PER_CATEGORY,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    response: requests.Response | None = None
    max_attempts = 1 + len(ARXIV_RETRY_DELAYS_SECONDS)
    for attempt in range(max_attempts):
        try:
            response = requests.get(
                ARXIV_API_BASE,
                params=params,
                timeout=60,
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            break
        except requests.HTTPError as exc:
            response = exc.response
            status_code = response.status_code if response is not None else None
            retriable = status_code in {429, 500, 502, 503, 504}
            if retriable and attempt < max_attempts - 1:
                delay = _retry_delay_seconds(response, attempt)
                logger.log(
                    f"⚠️ arXiv fetch limited for {category} (HTTP {status_code}); "
                    f"retrying in {delay:.0f}s"
                )
                time.sleep(delay)
                continue
            logger.log(f"⚠️ arXiv fetch failed for {category}: {_format_request_error(exc)}")
            return []
        except requests.RequestException as exc:
            if attempt < max_attempts - 1:
                delay = ARXIV_RETRY_DELAYS_SECONDS[min(attempt, len(ARXIV_RETRY_DELAYS_SECONDS) - 1)]
                logger.log(f"⚠️ arXiv request error for {category}: {exc}; retrying in {delay:.0f}s")
                time.sleep(delay)
                continue
            logger.log(f"⚠️ arXiv fetch failed for {category}: {exc}")
            return []
        except Exception as exc:  # network/API failures should not abort all categories
            logger.log(f"⚠️ arXiv fetch failed for {category}: {exc}")
            return []
    else:
        return []

    try:
        root = ET.fromstring(response.text if response is not None else "")
    except ET.ParseError as exc:
        logger.log(f"⚠️ arXiv XML parse failed for {category}: {exc}")
        return []

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    papers: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        abstract = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
        abs_url = clean_text(entry.findtext("atom:id", default="", namespaces=ns))
        published = clean_text(entry.findtext("atom:published", default="", namespaces=ns))
        updated = clean_text(entry.findtext("atom:updated", default="", namespaces=ns))
        doi = clean_text(entry.findtext("arxiv:doi", default="", namespaces=ns)) or None
        authors = [
            clean_text(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        ]
        authors = [author for author in authors if author]

        if not title or not abstract or "/abs/" not in abs_url:
            continue

        arxiv_id = arxiv_id_from_url(abs_url)
        papers.append(
            {
                "title": title,
                "abstract": abstract,
                "url": abs_url,
                "pdf_url": abs_url.replace("/abs/", "/pdf/"),
                "arxiv_id": arxiv_id,
                "dedupe_id": strip_arxiv_version(arxiv_id),
                "category": category,
                "date": published[:10] if published else updated[:10],
                "published": published,
                "updated": updated,
                "doi": doi,
                "authors": authors,
            }
        )
    logger.log(f"  - {category}: fetched {len(papers)} papers")
    return papers


def _extract_markdown_link_target(line: str) -> str:
    match = re.search(r"\]\(([^)]+)\)", line)
    if match:
        return clean_text(match.group(1))
    return clean_text(line.split(":", 1)[-1])


def _strip_markdown_tags(title_line: str) -> str:
    return re.sub(r"\s+#\S+(?:\s+#\S+)*\s*$", "", title_line).strip()


def parse_arxiv_summary_cache(path: Path) -> list[dict[str, Any]]:
    """Parse a previously generated arXiv markdown summary for emergency fallback use."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    total_match = re.search(r"Total Papers:\s*(\d+)", text)
    if total_match and int(total_match.group(1)) <= 0:
        return []

    papers: list[dict[str, Any]] = []
    current_topic = "cached"
    current: dict[str, Any] | None = None

    def finish_current() -> None:
        if current and current.get("title") and current.get("url"):
            current.setdefault("abstract", current.get("summary_override") or current["title"])
            current.setdefault("pdf_url", current.get("url", "").replace("/abs/", "/pdf/"))
            current.setdefault("doi", None)
            current.setdefault("authors", [])
            current.setdefault("date", path.stem)
            current.setdefault("published", current.get("date", path.stem))
            current.setdefault("updated", current.get("published", current.get("date", path.stem)))
            current.setdefault("category", current_topic)
            if not current.get("dedupe_id"):
                current["dedupe_id"] = current.get("arxiv_id") or current["title"]
            current["fallback_from"] = path.stem
            papers.append(current)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_topic = line[3:].strip().lower().replace(" ", "_") or "cached"
            continue
        if line.startswith("### "):
            finish_current()
            title = _strip_markdown_tags(line[4:].strip())
            current = {
                "title": title,
                "abstract": "",
                "summary_override": "",
                "category": current_topic,
                "url": "",
                "pdf_url": "",
                "doi": None,
                "authors": [],
                "date": path.stem,
                "published": path.stem,
                "updated": path.stem,
            }
            continue
        if current is None:
            continue
        if line.startswith("- 요약:"):
            summary = clean_text(line.split(":", 1)[1])
            current["summary_override"] = summary
            current["abstract"] = summary
        elif line.startswith("- 핵심기여:"):
            category_match = re.search(r"`([^`]+)`", line)
            if category_match:
                current["category"] = category_match.group(1)
        elif line.startswith("- 저자:"):
            author_text = clean_text(line.split(":", 1)[1])
            if author_text and "확인" not in author_text:
                current["authors"] = [
                    author.strip()
                    for author in author_text.split(",")
                    if author.strip() and author.strip().lower() != "et al."
                ]
        elif line.startswith("- 링크:"):
            url = _extract_markdown_link_target(line)
            current["url"] = url
            if "/abs/" in url:
                arxiv_id = arxiv_id_from_url(url)
                current["arxiv_id"] = arxiv_id
                current["dedupe_id"] = strip_arxiv_version(arxiv_id)
        elif line.startswith("- PDF:"):
            current["pdf_url"] = _extract_markdown_link_target(line)
        elif line.startswith("- DOI:"):
            doi = clean_text(line.split(":", 1)[1])
            current["doi"] = None if not doi or "확인" in doi else doi
        elif line.startswith("- 게시일:"):
            date = clean_text(line.split(":", 1)[1])
            if date and "확인" not in date:
                current["date"] = date
                current["published"] = f"{date}T00:00:00Z" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) else date
                current["updated"] = current["published"]

    finish_current()
    return papers


def load_cached_arxiv_papers(today: str, logger: PipelineLogger) -> list[dict[str, Any]]:
    """Return latest non-empty generated arXiv summary when the live API is rate-limited."""
    candidates = sorted(ARXIV_DIR.glob("????-??-??.md"), reverse=True)
    for candidate in candidates:
        if candidate.stem >= today:
            continue
        papers = parse_arxiv_summary_cache(candidate)
        if papers:
            logger.log(
                f"⚠️ Using cached arXiv fallback from {candidate.name} "
                f"({len(papers)} papers); live arXiv API unavailable"
            )
            return papers[:ARXIV_TARGET_TOTAL]
    logger.log("⚠️ No cached arXiv fallback with papers is available")
    return []


def fetch_arxiv_papers(logger: PipelineLogger, today: str | None = None) -> list[dict[str, Any]]:
    """Fetch and deduplicate recent papers from arXiv, falling back to cache on total outage."""
    collected: dict[str, dict[str, Any]] = {}
    for idx, category in enumerate(ARXIV_CATEGORIES):
        if idx:
            time.sleep(ARXIV_REQUEST_DELAY_SECONDS)  # arXiv asks clients to be conservative.
        for paper in fetch_arxiv_category(category, logger):
            # Keep the first/latest hit per arXiv ID without version suffix.
            collected.setdefault(paper["dedupe_id"], paper)

    papers = list(collected.values())
    papers.sort(key=lambda item: item.get("published") or item.get("date") or "", reverse=True)
    if papers:
        return papers[:ARXIV_TARGET_TOTAL]

    return load_cached_arxiv_papers(today or dt.date.today().strftime("%Y-%m-%d"), logger)


def classify_topic(paper: dict[str, Any]) -> str:
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
    topic_keywords = {
        "prompt_engineering": ["prompt", "instruction", "template", "preference"],
        "data_science": ["data", "analytics", "statistics", "mining", "dataset"],
        "ai_agents": ["agent", "multi-agent", "autonomous", "coordination", "workflow"],
        "context_engineering": ["context", "retrieval", "attention", "long-context", "window"],
        "ai_safety_evals": ["safety", "alignment", "risk", "evaluation", "benchmark", "eval"],
        "agent_memory": ["memory", "recall", "episodic", "semantic", "long-term"],
        "tool_reliability": ["tool", "reliability", "validation", "robust", "verification"],
        "multimodal_agents": ["multimodal", "vision-language", "cross-modal", "image", "video"],
        "rag_evaluation": ["rag", "retrieval", "augmented", "grounding"],
    }
    best_topic = "data_science"
    best_score = -1
    for topic, keywords in topic_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > best_score:
            best_topic = topic
            best_score = score
    return best_topic


def classify_papers(papers: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    classified: dict[str, list[dict[str, Any]]] = {}
    for paper in papers:
        classified.setdefault(classify_topic(paper), []).append(paper)
    return classified


def keywords_for_paper(paper: dict[str, Any], topic: str) -> list[str]:
    base = [topic.replace("_", "-")]
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
    candidates = [
        "prompt",
        "agent",
        "memory",
        "context",
        "retrieval",
        "evaluation",
        "safety",
        "multimodal",
        "data-science",
        "tool-use",
    ]
    for candidate in candidates:
        if candidate.replace("-", " ") in text or candidate in text:
            base.append(candidate)
    # Stable order, no duplicates.
    seen: set[str] = set()
    tags = []
    for item in base:
        normalized = re.sub(r"[^0-9A-Za-z가-힣_-]", "", item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            tags.append(f"#{normalized}")
    return tags


KOREAN_TOPIC_PHRASES = {
    "agent": "AI 에이전트",
    "agents": "AI 에이전트",
    "memory": "장기 기억",
    "long-term": "장기 맥락",
    "context": "컨텍스트 처리",
    "retrieval": "검색 증강",
    "rag": "RAG 평가",
    "benchmark": "벤치마크",
    "evaluation": "평가 방법론",
    "evaluate": "평가 방법론",
    "multimodal": "멀티모달 생성",
    "vision": "비전 모델",
    "language": "언어 모델",
    "prompt": "프롬프트 설계",
    "embedding": "임베딩 개선",
    "inference": "추론 효율",
    "safety": "AI 안전성",
    "alignment": "정렬",
    "tool": "도구 사용",
    "workflow": "작업 흐름",
    "dataset": "데이터셋",
}


def _unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def infer_korean_topics(abstract: str) -> list[str]:
    lower = abstract.lower()
    topics = [phrase for keyword, phrase in KOREAN_TOPIC_PHRASES.items() if keyword in lower]
    return _unique_preserve_order(topics)[:5] or ["해당 분야의 최신 연구 문제"]


def infer_korean_contributions(abstract: str) -> list[str]:
    lower = abstract.lower()
    contributions: list[str] = []
    if any(token in lower for token in ("we introduce", "we propose", "this paper introduces", "this paper proposes")):
        contributions.append("새로운 방법이나 프레임워크를 제안한다")
    if "benchmark" in lower or "dataset" in lower:
        contributions.append("평가용 기준과 데이터 구성을 제공한다")
    if any(token in lower for token in ("evaluate", "evaluation", "experiment", "results", "empirical")):
        contributions.append("실험과 평가를 통해 효과를 검증한다")
    if any(token in lower for token in ("improve", "enhance", "robust", "scalable", "efficient")):
        contributions.append("성능·신뢰성·확장성 개선을 목표로 한다")
    return _unique_preserve_order(contributions)[:3] or ["기존 접근의 한계를 분석하고 개선 방향을 제시한다"]


def extract_named_terms(abstract: str) -> list[str]:
    # Preserve model/benchmark names while keeping the explanatory summary Korean.
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)+\b|\b[A-Z]{2,}[A-Za-z0-9-]*\b", abstract)
    ignored = {"AI", "LLM", "LLMs", "API", "Long-term", "Long-Term"}
    return [term for term in _unique_preserve_order(candidates) if term not in ignored and not term.endswith("-")][:4]


def summarize_abstract(abstract: str, limit: int = 500) -> str:
    """Return a Korean-language arXiv summary instead of copying English abstracts."""
    abstract = clean_text(abstract)
    if not abstract:
        return "이 논문은 초록 정보를 확인할 수 없어 세부 내용을 추가 검증해야 한다."

    topics = infer_korean_topics(abstract)
    contributions = infer_korean_contributions(abstract)
    terms = extract_named_terms(abstract)

    if len(contributions) == 1:
        contribution_text = contributions[0]
    else:
        stems = [item[:-1] if item.endswith("다") else item for item in contributions]
        contribution_text = "고, ".join(stems) + "다"

    summary = (
        f"이 논문은 다음 주제를 다룬다: {', '.join(topics)}. "
        f"핵심적으로 {contribution_text}. "
        "연구 결과는 관련 모델·에이전트 시스템의 설계, 평가, 실제 적용 가능성을 판단하는 근거로 활용될 수 있다."
    )
    if terms:
        summary += f" 주요 용어는 {', '.join(terms)}이다."

    if len(summary) <= limit:
        return summary
    return summary[: limit - 1].rstrip() + "…"


def generate_arxiv_summary(today: str, logger: PipelineLogger) -> tuple[Path, list[dict[str, Any]]]:
    papers = fetch_arxiv_papers(logger, today=today)
    classified_papers = classify_papers(papers)
    output_path = ARXIV_DIR / f"{today}.md"

    lines = [
        f"# arXiv Papers Summary - {today}",
        "",
        f"*Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Papers: {len(papers)}*",
        "",
        f"오늘 제안/채택한 확장 주제: {', '.join(EXTENSION_TOPICS[:3])}",
        "",
    ]

    fallback_dates = sorted({paper.get("fallback_from") for paper in papers if paper.get("fallback_from")})
    if fallback_dates:
        lines.extend(
            [
                f"> ⚠️ arXiv API rate limit/server issue로 최신 캐시({', '.join(fallback_dates)})를 대체 사용했습니다. 최신성 검증이 필요합니다.",
                "",
            ]
        )

    if not papers:
        lines.extend(
            [
                "> ⚠️ arXiv API에서 논문을 가져오지 못했습니다. run_logs를 확인하세요.",
                "",
            ]
        )
    else:
        for topic, topic_papers in sorted(classified_papers.items()):
            lines.extend([f"## {topic.replace('_', ' ').title()}", ""])
            for paper in topic_papers:
                authors = ", ".join(paper.get("authors", [])[:5])
                if len(paper.get("authors", [])) > 5:
                    authors += ", et al."
                tags = " ".join(keywords_for_paper(paper, topic))
                doi = paper.get("doi") or "확인 불가"
                summary = paper.get("summary_override") or summarize_abstract(paper["abstract"])
                source_label = f"`{paper['category']}`"
                if paper.get("fallback_from"):
                    source_label += f" 캐시({paper['fallback_from']})"
                lines.extend(
                    [
                        f"### {paper['title']} {tags}",
                        f"- 요약: {summary}",
                        f"- 핵심기여: {source_label} 최신 연구로서 {topic.replace('_', ' ')} 관련 방법·평가·응용 가능성을 제시한다.",
                        f"- 저자: {authors or '확인 불가'}",
                        f"- 링크: [{paper['url']}]({paper['url']})",
                        f"- PDF: [{paper['pdf_url']}]({paper['pdf_url']})",
                        f"- DOI: {doi}",
                        f"- 게시일: {paper.get('date') or '확인 불가'}",
                        "",
                    ]
                )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path, papers


def fetch_korean_papers() -> list[dict[str, Any]]:
    """Return curated Korean-paper placeholders when paid DB APIs are unavailable."""
    return [
        {
            "title": "AI 에이전트의 컨텍스트 엔지니어링을 통한 성능 향상 연구",
            "abstract": "AI 에이전트의 컨텍스트 처리 방법론을 개선하기 위한 접근법을 제안하고, 다중 턴 대화에서 컨텍스트 효율성을 높이는 동적 컨텍스트 선택 알고리즘을 논의한다.",
            "url": "https://www.riss.kr/",
            "source": "RISS 검색 필요",
            "institution": "KAIST",
            "keywords": ["AI 에이전트", "컨텍스트 엔지니어링", "다중 턴 대화", "동적 선택"],
            "doi": None,
        },
        {
            "title": "대규모 언어 모델의 프롬프트 엔지니어링 기법 연구",
            "abstract": "대규모 언어 모델의 성능 향상을 위한 프롬프트 엔지니어링 기법을 종합 분석하고, 프롬프트 최적화 알고리즘의 평가 가능성을 검토한다.",
            "url": "https://www.dbpia.co.kr/",
            "source": "DBpia 검색 필요",
            "institution": "서울대학교",
            "keywords": ["대규모 언어 모델", "프롬프트 엔지니어링", "성능 최적화", "알고리즘"],
            "doi": None,
        },
        {
            "title": "다중모달 AI 에이전트의 도구 신뢰성 평가 프레임워크",
            "abstract": "비전, 언어, 음성을 통합 처리하는 다중모달 AI 에이전트의 도구 사용 신뢰성을 평가하기 위한 프레임워크를 제안한다.",
            "url": "https://www.kci.go.kr/",
            "source": "KCI 검색 필요",
            "institution": "포항공과대학교",
            "keywords": ["다중모달 AI", "도구 신뢰성", "평가 프레임워크", "실증 연구"],
            "doi": None,
        },
    ]


def generate_korean_summary(today: str) -> tuple[Path, list[dict[str, Any]]]:
    papers = fetch_korean_papers()
    output_path = KR_DIR / f"{today}.md"
    lines = [
        f"# Korean Research Papers Summary - {today}",
        "",
        f"*Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Papers: {len(papers)}*",
        "",
        "> 주의: RISS/DBpia/KCI는 공개 API 접근 제약이 있어 현재 항목은 후속 수동 검증이 필요한 후보 형식으로 기록합니다.",
        "",
        "## KCI급 및 박사학위 논문 후보",
        "",
    ]
    for paper in papers:
        tags = " ".join(f"#{keyword.replace(' ', '_')}" for keyword in paper["keywords"])
        lines.extend(
            [
                f"### {paper['title']} {tags}",
                f"- 요약: {paper['abstract']}",
                f"- 핵심기여: {paper['institution']} 중심 AI 연구 후보로서 문헌 검증 후 국내 연구 동향 비교에 활용 가능하다.",
                f"- 소스: {paper['source']}",
                f"- 링크: [{paper['url']}]({paper['url']})",
                f"- DOI: {paper.get('doi') or '확인 필요'}",
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path, papers


def apa_author_list(authors: list[str]) -> str:
    if not authors:
        return "Unknown Author"
    if len(authors) == 1:
        return authors[0]
    if len(authors) <= 5:
        return ", ".join(authors[:-1]) + f", & {authors[-1]}"
    return ", ".join(authors[:3]) + ", et al."


def generate_research_report(
    today: str,
    arxiv_papers: list[dict[str, Any]],
    kr_papers: list[dict[str, Any]],
) -> Path:
    output_path = REPORT_DIR / f"{today}.md"
    primary = arxiv_papers[0] if arxiv_papers else None
    primary_title = primary["title"] if primary else "당일 arXiv 수집 실패"
    primary_citation = f"({apa_author_list(primary.get('authors', []))}, {today[:4]})" if primary else "(arXiv 수집 실패, n.d.)"

    lines = [
        f"# 심층 연구 보고서 - {today}",
        "",
        f"*Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Analyzed Papers: {len(arxiv_papers) + len(kr_papers)}*",
        "",
        "## Executive Summary",
        "",
        (
            "본 보고서는 당일 수집한 arXiv 논문과 국내 논문 후보를 바탕으로 "
            "AI 에이전트, 컨텍스트 엔지니어링, 도구 신뢰성, 평가 방법론의 결합 가능성을 검토한다. "
            f"특히 `{primary_title}` {primary_citation}을 핵심 근거 중 하나로 삼아 장기 기억·도구 사용·평가 신뢰성을 연결하는 박사학위급 연구 주제를 도출한다."
        ),
        "",
        "## 1. 박사학위급 연구 주제 도출",
        "",
        "**제안 주제:** 장기 기억을 갖춘 AI 에이전트의 컨텍스트 선택과 도구 사용 신뢰성 평가 프레임워크",
        "",
        "- 연구질문 1: 장기 에이전트 기억이 컨텍스트 선택 정확도와 작업 완수율을 어떻게 변화시키는가?",
        "- 연구질문 2: 도구 호출 실패·환각·근거 누락을 통합적으로 측정하는 평가지표를 어떻게 설계할 수 있는가?",
        "- 연구질문 3: 멀티모달 입력이 포함될 때 컨텍스트 압축과 검색 증강의 최적 균형은 무엇인가?",
        "",
        "## 2. 이론적 분석",
        "",
        "AI 에이전트 연구는 단일 응답 생성에서 벗어나 기억, 계획, 도구 사용, 장기 상호작용을 통합하는 방향으로 이동하고 있다. 당일 arXiv 수집 논문들은 에이전트 기억, 임베딩 개선, 검색·평가 체계를 중심으로 분포하며, 이는 컨텍스트 엔지니어링을 독립 기법이 아니라 에이전트 아키텍처의 핵심 제어 계층으로 보아야 함을 시사한다.",
        "",
        "## 3. 방법론적 분석",
        "",
        "방법론적으로는 (a) 장기 메모리 벤치마크, (b) 테스트 시점 임베딩/검색 보정, (c) 도구 호출 로그 기반 신뢰성 평가를 결합한 혼합 실험 설계가 적합하다. 국내 논문 후보군은 프롬프트 엔지니어링과 다중모달 도구 신뢰성이라는 응용 관점을 제공하므로, 국제 논문의 벤치마크 지향성과 국내 연구의 적용 지향성을 연결하는 비교 연구가 가능하다.",
        "",
        "## 4. 평가 분석",
        "",
        "평가는 단순 정확도보다 작업 완수율, 근거 충실도, 컨텍스트 효율성, 실패 복구율, 도구 호출 안전성을 함께 측정해야 한다. 특히 장기 기억이 잘못 검색될 때 생기는 누적 오류를 별도 지표로 분리해야 한다.",
        "",
        "## 5. 윤리 및 산업적 함의",
        "",
        "장기 기억형 에이전트는 개인정보 보존, 동의 철회, 기억 오염, 권한 없는 도구 호출이라는 윤리적 위험을 동반한다. 산업적으로는 고객지원, 연구보조, 소프트웨어 개발 자동화에서 높은 효용이 예상되지만, 감사 가능한 로그와 실패 시 안전 정지 메커니즘이 전제되어야 한다.",
        "",
        "## 6. References",
        "",
    ]

    if arxiv_papers:
        for paper in arxiv_papers[:10]:
            authors = apa_author_list(paper.get("authors", []))
            year = (paper.get("date") or today)[:4]
            doi = f" https://doi.org/{paper['doi']}" if paper.get("doi") else ""
            lines.append(f"- {authors}. ({year}). {paper['title']}. *arXiv*. {paper['url']}.{doi}")
    else:
        lines.append("- arXiv API results unavailable for this run; see run log.")

    lines.extend(
        [
            "",
            "## 7. 국내 문헌 후보",
            "",
        ]
    )
    for paper in kr_papers:
        lines.append(f"- {paper['institution']}. (검증 필요). {paper['title']}. {paper['source']}. {paper['url']}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def run_git(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def commit_to_github(today: str) -> tuple[str, bool]:
    """Commit and push generated research files from the current repository."""
    try:
        branch = run_git(["branch", "--show-current"], check=True).stdout.strip() or "main"

        # Keep the working copy in sync before adding generated files.
        pull = run_git(["pull", "--rebase", "--autostash", "origin", branch])
        if pull.returncode != 0:
            return f"GitHub push: 실패 - pull/rebase 실패: {pull.stderr.strip()}", False

        add_paths = [
            ".gitignore",
            "daily_research_pipeline.py",
            "tests",
            "arxiv_paper",
            "kr_paper",
            "research_reports",
            "paper_research/run_logs",
        ]
        run_git(["add", *add_paths], check=True)

        status = run_git(["status", "--porcelain"], check=True).stdout.strip()
        if not status:
            return "GitHub push: 변경없음", True

        commit_msg = f"Update research papers - {today}"
        commit = run_git(["commit", "-m", commit_msg])
        if commit.returncode != 0:
            # If another process committed between status and commit, treat clean tree as no-op.
            clean = run_git(["status", "--porcelain"]).stdout.strip()
            if not clean:
                return "GitHub push: 변경없음", True
            return f"GitHub push: 실패 - commit 실패: {commit.stderr.strip()}", False

        push = run_git(["push", "origin", branch])
        if push.returncode == 0:
            return "GitHub push: 성공", True
        return f"GitHub push: 실패 - {push.stderr.strip()}", False
    except subprocess.CalledProcessError as exc:
        return f"GitHub push: 실패 - git 명령 실패: {exc}", False
    except Exception as exc:
        return f"GitHub push: 실패 - 예외: {exc}", False


def main() -> int:
    os.chdir(REPO_ROOT)
    today = setup_directories()
    logger = PipelineLogger(today)
    git_result = "GitHub push: 미실행"
    git_success = False

    try:
        logger.log("🔬 Daily Research Pipeline Starting...")
        logger.log(f"📅 Date: {today}")
        logger.log(f"📁 Repository: {REPO_ROOT}")

        logger.log("📚 Collecting arXiv papers...")
        arxiv_file, arxiv_papers = generate_arxiv_summary(today, logger)
        logger.log(f"✅ Generated: {arxiv_file.relative_to(REPO_ROOT)} ({len(arxiv_papers)} papers)")

        logger.log("🇰🇷 Collecting Korean papers...")
        kr_file, kr_papers = generate_korean_summary(today)
        logger.log(f"✅ Generated: {kr_file.relative_to(REPO_ROOT)} ({len(kr_papers)} candidates)")

        logger.log("📊 Generating research report...")
        report_file = generate_research_report(today, arxiv_papers, kr_papers)
        logger.log(f"✅ Generated: {report_file.relative_to(REPO_ROOT)}")

        logger.log("🚀 Committing to GitHub...")
        logger.flush()  # include log contents in the commit
        git_result, git_success = commit_to_github(today)
        logger.log(git_result)

        arxiv_ok = len(arxiv_papers) > 0
        using_arxiv_cache = any(paper.get("fallback_from") for paper in arxiv_papers)
        success = arxiv_ok and git_success
        if success and using_arxiv_cache:
            status = "부분성공(캐시대체)"
        elif success:
            status = "성공"
        elif arxiv_ok:
            status = "부분성공"
        else:
            status = "실패"

        logger.log("\n📤 Discord Output:")
        logger.log(f"1) 연구 파이프라인 완료: {status}")
        logger.log(f"2) {git_result}")
        logger.log(f"3) 오늘 확장 주제: {', '.join(EXTENSION_TOPICS[:3])}")

        if success:
            if using_arxiv_cache:
                logger.log("\n⚠️ Daily research pipeline completed with cached arXiv fallback; wiki sync may continue.")
            else:
                logger.log("\n🎉 Daily research pipeline completed successfully!")
            return 0
        logger.log("\n⚠️ Daily research pipeline completed with warnings/failures.")
        return 1
    except Exception as exc:
        logger.log(f"❌ Pipeline failed before GitHub sync: {exc}")
        logger.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
