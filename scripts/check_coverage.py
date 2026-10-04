import json
import sys
from pathlib import Path


def main():
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    engine = [
        value["summary"]
        for name, value in report["files"].items()
        if name.replace("\\", "/").startswith("engine/")
    ]
    branches = sum(item["num_branches"] for item in engine)
    covered = sum(item["covered_branches"] for item in engine)
    if not branches or covered / branches < 0.90:
        raise SystemExit("Motor dal kapsamı %90 altına düştü veya motor ölçülmedi.")
    print(f"Motor dal kapsamı: {covered}/{branches} = %{covered / branches * 100:.2f}")


if __name__ == "__main__":
    main()
