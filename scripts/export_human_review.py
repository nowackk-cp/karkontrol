"""Read a human-completed workbook; export values without filling any expectations."""

import argparse
import csv
from datetime import date, datetime
from pathlib import Path

import openpyxl

FIELDS = (
    "id",
    "net_sales",
    "commission",
    "shipping",
    "service",
    "withholding",
    "profit",
    "payout",
    "reviewer",
    "reviewed_at",
    "source",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workbook = openpyxl.load_workbook(args.workbook, read_only=True, data_only=True)
    try:
        rows = list(
            workbook["Inceleme"].iter_rows(min_row=7, max_row=47, max_col=11, values_only=True)
        )
        if tuple(rows[0]) != FIELDS:
            raise ValueError("Review columns changed")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(FIELDS)
            for row in rows[1:]:
                writer.writerow(
                    [
                        value.isoformat()[:10]
                        if isinstance(value, (date, datetime))
                        else ""
                        if value is None
                        else value
                        for value in row
                    ]
                )
    finally:
        workbook.close()
    print("Values exported. Run check_golden; export does not establish human approval.")


if __name__ == "__main__":
    main()
