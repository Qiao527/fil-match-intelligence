"""Public synthetic-only regression contracts; never requires provider data."""

import copy
import runpy
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fil.intelligence.demo import MATCHES, load_demo  # noqa: E402
from fil.intelligence.engine import analyze  # noqa: E402

response = runpy.run_path(str(ROOT / "api/index.py"))["response"]


@pytest.mark.parametrize("mid", MATCHES)
def test_original_ids_exact_accounting_and_repeatability(mid):
    raw, meta, identity = load_demo(mid)
    before = copy.deepcopy(raw)
    r = analyze(raw, meta, identity)
    assert r == analyze(raw, meta, identity) and raw == before
    shots = [e for e in raw if e["type"]["name"] == "Shot"]
    assert Fraction(r["shot_weight"]) == sum(
        Fraction(str(e["shot"]["statsbomb_xg"])) for e in shots
    )
    assert {s["event_id"] for s in r["shots"]} == {e["id"] for e in shots}
    assert r["validated_capabilities"] == r["validated_explanations"] == []
    assert all(c["independent_relevance"] is None for c in r["review_cards"])
    for u in r["native_units"]:
        other = [e for e in shots if e["id"] not in u["event_ids"]]
        expected = sum(
            (
                Fraction(str(e["shot"]["statsbomb_xg"])) * (1 if e["team"]["id"] == 901 else -1)
                for e in other
            ),
            Fraction(0),
        )
        assert Fraction(u["complement_difference"]) == expected


@pytest.mark.parametrize(
    "query",
    [
        "match=8658",
        "match=demo-1&period=5",
        "match=demo-1&path=/etc/passwd",
        "match=demo-1&match=demo-2",
        "match=demo-1&team=999",
    ],
)
def test_api_rejects_unapproved_inputs(query):
    assert response("/api/analyze?" + query)[0] == 400


def test_filter_empty_state_and_missing_weight():
    assert response("/api/analyze?match=demo-3&period=2")[1]["report"]["shot_count"] == 0
    raw, meta, identity = load_demo("demo-1")
    shot = next(e for e in raw if e["type"]["name"] == "Shot")
    shot["shot"].pop("statsbomb_xg")
    r = analyze(raw, meta, identity)
    assert r["shot_weight"] is None and not r["review_cards"]
    assert r["missing_shot_weight_ids"] == [shot["id"]]


@pytest.mark.parametrize("defect", ["duplicate", "order", "score"])
def test_source_failures_stop_analysis(defect):
    raw, meta, identity = load_demo("demo-1")
    if defect == "duplicate":
        raw[1]["id"] = raw[0]["id"]
    elif defect == "order":
        raw[0], raw[1] = raw[1], raw[0]
    else:
        meta["home_score"] += 1
    with pytest.raises(ValueError):
        analyze(raw, meta, identity)


def test_runtime_code_has_no_private_imports_or_acquisition():
    for p in [*(ROOT / "src").rglob("*.py"), *(ROOT / "api").rglob("*.py")]:
        body = p.read_text()
        assert "fil.research" not in body and "fil.ingestion" not in body
        assert "urlopen(" not in body and "requests." not in body
    assert response("/api/health") == (200, {"status": "ok", "mode": "synthetic-only"})
    assert len(response("/api/matches")[1]) == 3


def test_public_extraction_matches_original_engine_on_all_fictional_selections():
    import hashlib
    import json

    reference = json.loads((ROOT / "tests/fixtures/engine-reference.json").read_text())
    for case in reference["cases"]:
        report = analyze(*load_demo(case["match"]), **case["selection"])
        assert (
            hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
            == case["sha256"]
        )
