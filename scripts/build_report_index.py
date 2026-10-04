"""Build the Pages landing page from the successful run's actual artifacts."""

import argparse
import html
import json
from pathlib import Path
from xml.etree import ElementTree

LAYERS = (
    ("unit", "Birim"),
    ("integration", "Entegrasyon"),
    ("eval", "Çevrimdışı eval"),
    ("other", "Diğer testler"),
    ("e2e", "Chromium E2E"),
)


def junit_counts(path):
    root = ElementTree.parse(path).getroot()
    # Nested suite parents already contain their children's totals; count leaves.
    suites = [suite for suite in root.iter("testsuite") if not suite.findall("testsuite")]
    if not suites:
        raise ValueError(f"JUnit test suite bulunamadı: {path}")
    counts = {
        field: sum(int(suite.get(field, "0")) for suite in suites)
        for field in ("tests", "failures", "errors", "skipped")
    }
    counts["passed"] = counts["tests"] - sum(
        counts[field] for field in ("failures", "errors", "skipped")
    )
    if any(value < 0 for value in counts.values()):
        raise ValueError(f"JUnit sayıları tutarsız: {path}")
    return counts


def build_index(root, run_url, commit):
    report = json.loads((root / "reports" / "coverage.json").read_text(encoding="utf-8"))
    coverage = str(report["totals"]["percent_covered_display"])
    rows = []
    total = dict.fromkeys(("tests", "passed", "failures", "errors", "skipped"), 0)
    for name, label in LAYERS:
        counts = junit_counts(root / "reports" / f"{name}.xml")
        total = {field: total[field] + counts[field] for field in total}
        rows.append(
            f"<tr><th>{label}</th><td>{counts['tests']}</td><td>{counts['passed']}</td>"
            f"<td>{counts['skipped']}</td><td>{counts['failures'] + counts['errors']}</td>"
            f'<td><a href="reports/{name}.html">HTML</a> · '
            f'<a href="reports/{name}.xml">JUnit</a></td></tr>'
        )
    page = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KârKontrol QA raporları</title>
<style>body{{max-width:920px;margin:48px auto;padding:24px;font:17px/1.7 system-ui;
color:#182a35;background:#f3f6f8}}a{{color:#136454}}code{{overflow-wrap:anywhere}}
table{{border-collapse:collapse;width:100%}}th,td{{padding:10px;text-align:left;
border-bottom:1px solid #cdd9de}}.scroll{{overflow-x:auto}}</style></head><body>
<h1>KârKontrol QA raporları</h1>
<p>Başarılı ana dal CI çalışmasının gerçek çıktıları.</p>
<p>Toplam: {total["tests"]} test; {total["passed"]} geçti, {total["skipped"]} atlandı,
{total["failures"] + total["errors"]} başarısız. Satır ve dal kapsamı: %{html.escape(coverage)}.</p>
<div class="scroll"><table><thead><tr><th>Katman</th><th>Test</th><th>Geçti</th>
<th>Atlandı</th><th>Başarısız</th><th>Rapor</th></tr></thead><tbody>
{"".join(rows)}</tbody></table></div>
<p><a href="htmlcov/index.html">Kapsam HTML raporu</a> ·
<a href="reports/coverage.json">Kapsam JSON</a> ·
<a href="{html.escape(run_url, quote=True)}">Kaynak CI çalışması</a></p>
<p>Commit: <code>{html.escape(commit)}</code></p>
<p>İnsan altın veri kabulü ayrı human-golden işinde ölçülür; gerçek model ve insan
hakem kalibrasyonu bu raporda ölçülmez.</p></body></html>
"""
    (root / "index.html").write_text(page, encoding="utf-8")
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--commit", required=True)
    options = parser.parse_args()
    print(json.dumps(build_index(options.root, options.run_url, options.commit)))


if __name__ == "__main__":
    main()
