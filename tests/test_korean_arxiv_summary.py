import re

from daily_research_pipeline import summarize_abstract


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
