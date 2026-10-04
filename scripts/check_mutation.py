"""mutmut 3.8: exit 1 killed, exit 0 survived; others never counted as kills."""

import json
import os
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path


def main():
    root = Path(sys.argv[1])
    codes = Counter()
    for path in root.rglob("*.meta"):
        codes.update(json.loads(path.read_text(encoding="utf-8"))["exit_code_by_key"].values())
    total = sum(codes.values())
    killed = codes[1]
    if not total:
        raise SystemExit("Mutasyon verisi yok; boş set başarı sayılmaz.")
    summary = {
        "commit": os.environ.get("GITHUB_SHA", "local-artifact-check"),
        "total": total,
        "killed": killed,
        "survived": codes[0],
        "other": total - killed - codes[0],
        "score_percent": str((Decimal(killed) * 100 / total).quantize(Decimal("0.01"))),
    }
    target = Path("reports/mutation-summary.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if killed * 100 < total * 85:
        raise SystemExit("Motor mutasyon skoru %85 altında.")


if __name__ == "__main__":
    main()
