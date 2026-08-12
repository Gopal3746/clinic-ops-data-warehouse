from pathlib import Path


def test_ai_context_protects_grain_and_synthetic_data():
    text = Path("AGENTS.md").read_text(encoding="utf-8")
    assert "synthetic data only" in text.lower()
    assert "one row per encounter/session" in text
    assert "SCD Type 2" in text
