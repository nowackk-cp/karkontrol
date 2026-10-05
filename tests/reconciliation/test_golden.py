"""Her CSV satırı bağımsız insan kanıtı gerektirir; boş beklenti başarısızlıktır."""

import csv
import json
from pathlib import Path

import pytest

from qa.acceptance import read_review, reconcile
from scripts.check_golden import calculate

pytestmark = pytest.mark.reconciliation
ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data/draft/inputs.json"
REVIEW_PATH = ROOT / "data/golden/altin_set.csv"
if not REVIEW_PATH.exists():
    REVIEW_PATH = ROOT / "data/draft/manual_review.csv"
SCENARIOS = json.loads(INPUT_PATH.read_text(encoding="utf-8"))["scenarios"]
with REVIEW_PATH.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream, delimiter=";")
    HEADERS = reader.fieldnames
    REVIEW_ROWS = list(reader)


@pytest.mark.parametrize(
    "row", REVIEW_ROWS or [{}], ids=lambda row: row.get("id", "missing-review")
)
def test_human_reviewed_golden_row(row, tmp_path):
    identifier = row.get("id", "")
    scenario_ids = [scenario["id"] for scenario in SCENARIOS]
    review_ids = [review.get("id", "") for review in REVIEW_ROWS]
    assert len(scenario_ids) == len(set(scenario_ids)) == 40, "40 benzersiz girdi gerekli"
    assert len(review_ids) == len(set(review_ids)) == 40, "40 benzersiz insan incelemesi gerekli"
    assert set(review_ids) == set(scenario_ids), "CSV ve girdi kimlikleri aynı olmalı"

    # Mevcut provenance/doğrulama kapısını her gerçek CSV satırında ayrı uygula.
    single_review = tmp_path / "review.csv"
    with single_review.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=HEADERS, delimiter=";")
        writer.writeheader()
        writer.writerow(row)
    try:
        reviewed = read_review(single_review, {identifier})
    except ValueError as error:
        pytest.fail(str(error), pytrace=False)

    scenario = next(scenario for scenario in SCENARIOS if scenario["id"] == identifier)
    differences = reconcile([scenario], reviewed, calculate)
    assert not differences, f"{identifier}: {differences}"
