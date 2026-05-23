import re

import requests

from daily_research_pipeline import (
    fetch_arxiv_category,
    load_cached_arxiv_papers,
    summarize_abstract,
)


class DummyLogger:
    def __init__(self):
        self.messages = []

    def log(self, message: str) -> None:
        self.messages.append(message)


def test_arxiv_abstract_summary_is_written_in_korean():
    abstract = (
        "Long-term memory is crucial for agents in specialized web environments, "
        "where success depends on recalling interface affordances, state dynamics, "
        "workflows, and recurring failure modes. To address this gap, we introduce "
        "LongMemEval-V2, a benchmark for evaluating whether memory systems internalize "
        "environment-specific experience."
    )

    summary = summarize_abstract(abstract)

    assert re.search(r"[가-힣]", summary)
    assert summary.startswith("이 논문은")
    assert "Long-term memory is crucial" not in summary
    assert "To address this gap" not in summary
    assert len(summary) <= 500


def test_arxiv_fetch_retries_rate_limit_before_giving_up(monkeypatch):
    atom_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
      <entry>
        <id>http://arxiv.org/abs/2605.21384v1</id>
        <updated>2026-05-20T00:00:00Z</updated>
        <published>2026-05-20T00:00:00Z</published>
        <title>SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents</title>
        <summary>We introduce a benchmark for evaluating long-horizon coding agents.</summary>
        <author><name>Bingchen Zhao</name></author>
      </entry>
    </feed>
    """

    class FakeResponse:
        def __init__(self, status_code: int, text: str):
            self.status_code = status_code
            self.text = text
            self.headers = {}
            self.url = "https://export.arxiv.org/api/query?search_query=cat%3Acs.CL"

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"{self.status_code} Client Error", response=self)

    responses = [FakeResponse(429, "Rate exceeded."), FakeResponse(200, atom_xml)]
    sleeps = []

    def fake_get(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr("daily_research_pipeline.requests.get", fake_get)
    monkeypatch.setattr("daily_research_pipeline.time.sleep", lambda seconds: sleeps.append(seconds))

    papers = fetch_arxiv_category("cs.CL", DummyLogger())

    assert len(papers) == 1
    assert papers[0]["arxiv_id"] == "2605.21384v1"
    assert sleeps and sleeps[0] >= 3


def test_arxiv_cache_fallback_uses_latest_non_empty_summary(tmp_path, monkeypatch):
    cache_dir = tmp_path / "arxiv_paper"
    cache_dir.mkdir()
    (cache_dir / "2026-05-21.md").write_text(
        "# arXiv Papers Summary - 2026-05-21\n\n"
        "*Generated: 2026-05-21 09:00:00 | Total Papers: 0*\n\n"
        "> ⚠️ arXiv API에서 논문을 가져오지 못했습니다.\n",
        encoding="utf-8",
    )
    (cache_dir / "2026-05-22.md").write_text(
        "# arXiv Papers Summary - 2026-05-22\n\n"
        "*Generated: 2026-05-22 09:00:00 | Total Papers: 1*\n\n"
        "## Ai Agents\n\n"
        "### SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents #ai-agents #agent\n"
        "- 요약: 이 논문은 다음 주제를 다룬다: AI 에이전트, 벤치마크.\n"
        "- 핵심기여: `cs.CL` 최신 연구로서 ai agents 관련 방법·평가·응용 가능성을 제시한다.\n"
        "- 저자: Bingchen Zhao, Dhruv Srikanth\n"
        "- 링크: [http://arxiv.org/abs/2605.21384v1](http://arxiv.org/abs/2605.21384v1)\n"
        "- PDF: [http://arxiv.org/pdf/2605.21384v1](http://arxiv.org/pdf/2605.21384v1)\n"
        "- DOI: 확인 불가\n"
        "- 게시일: 2026-05-20\n",
        encoding="utf-8",
    )
    logger = DummyLogger()
    monkeypatch.setattr("daily_research_pipeline.ARXIV_DIR", cache_dir)

    papers = load_cached_arxiv_papers("2026-05-23", logger)

    assert len(papers) == 1
    assert papers[0]["title"] == "SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents"
    assert papers[0]["category"] == "cs.CL"
    assert papers[0]["url"] == "http://arxiv.org/abs/2605.21384v1"
    assert papers[0]["fallback_from"] == "2026-05-22"
    assert papers[0]["summary_override"].startswith("이 논문은")
    assert any("cached arXiv fallback" in message for message in logger.messages)
