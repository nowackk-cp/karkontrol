import json

from scripts.build_profit_lab import DATA_PATH, SVG_PATH, build_data, build_svg


def test_committed_lab_data_matches_engine():
    assert json.loads(DATA_PATH.read_text(encoding="utf-8")) == build_data()


def test_committed_cliff_chart_matches_engine():
    assert SVG_PATH.read_text(encoding="utf-8") == build_svg(build_data())


def test_lab_data_shows_the_documented_cliff():
    # Elle: 300,00 brüt → 250,00 net − 60,00 komisyon − 30,00 kargo − 10,00 hizmet
    # − 120,00 maliyet = 30,00. 300,01 brüt → 250,01 − 60,00 − 60,00 − 10,00 − 120,00 = 0,01.
    data = build_data()
    prices = data["prices"]
    profit = data["scenarios"]["20|120.00"]["profit"]
    assert profit[prices.index(30000)] == 3000
    assert profit[prices.index(30001)] == 1
