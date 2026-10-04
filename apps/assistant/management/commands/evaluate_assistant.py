"""Run actual model prompts against the SQL fixture in a rolled-back transaction."""

import csv
import hashlib
import json
import os
import subprocess
from datetime import date
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.assistant.llm import PROMPTS, ask_llm
from apps.assistant.remote import MODEL, haiku_completion
from apps.assistant.service import ask
from qa.acceptance import eval_gate
from qa.evaluation import score_result, seed_evaluation


def source_metadata():
    root = Path(__file__).resolve().parents[4]
    commit = os.getenv("GITHUB_SHA")
    modified = None
    try:
        if not commit:
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
        modified = bool(
            subprocess.run(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--untracked-files=all",
                    "--",
                    "apps",
                    "engine",
                    "qa",
                    "scripts",
                    "pyproject.toml",
                    "uv.lock",
                ],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
        )
    except (OSError, subprocess.SubprocessError):
        pass
    paths = (
        "apps/assistant/llm.py",
        "apps/assistant/remote.py",
        "apps/assistant/dates.py",
        "apps/assistant/service.py",
        "apps/assistant/tools.py",
        "qa/evaluation.py",
        "apps/assistant/management/commands/evaluate_assistant.py",
        "engine/profit.py",
    )
    return {
        "source_commit": commit or "local-unknown",
        "source_worktree_modified": modified,
        "source_sha256": {
            path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths
        },
    }


class Command(BaseCommand):
    help = "Actual local LLM/offline eval; fixture data always rolled back."

    def add_arguments(self, parser):
        parser.add_argument("--backend", choices=["local", "offline", "haiku"], default="local")
        parser.add_argument("--versions", default="v3")
        parser.add_argument(
            "--cases", type=Path, default=settings.BASE_DIR / "tests/eval/questions_v3.jsonl"
        )
        parser.add_argument(
            "--output", type=Path, default=settings.BASE_DIR / "reports/llm-eval.json"
        )
        parser.add_argument("--baseline", type=float, default=100)
        parser.add_argument("--baseline-file", type=Path)
        parser.add_argument("--today", type=date.fromisoformat, default=date(2026, 10, 4))

    def handle(self, *args, **options):
        versions = options["versions"].split(",")
        if any(version not in {"v1", "v2", "v3"} for version in versions):
            raise CommandError("Unknown prompt version")
        cases = [
            json.loads(line)
            for line in options["cases"].read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if options["backend"] == "haiku":
            if (
                options["cases"].resolve()
                != (settings.BASE_DIR / "tests/eval/questions_v3.jsonl").resolve()
            ):
                raise CommandError("Haiku yalnız sabit sentetik geliştirme sorularına açıktır.")
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise CommandError("ANTHROPIC_API_KEY Environment secret eksik; çağrı yapılmadı.")
            if versions != ["v3"] or len(cases) > 60:
                raise CommandError("Haiku tek v3 turunda en fazla 60 sentetik soru çalıştırır.")
        report = {
            **source_metadata(),
            "backend": options["backend"],
            "model": os.getenv("KARKONTROL_LLM_MODEL", "Qwen3-1.7B-Q8_0")
            if options["backend"] == "local"
            else MODEL
            if options["backend"] == "haiku"
            else None,
            "dataset_sha256": hashlib.sha256(options["cases"].read_bytes()).hexdigest(),
            "numeric_oracle": "parameterized SQL on synthetic ledger, integer cents",
            "human_judge_calibrated": False,
            "clock_date": options["today"].isoformat(),
            "fixture": "ranking-v3-six-distinct-profits",
            "versions": {},
        }
        with (
            transaction.atomic(),
            patch("django.utils.timezone.localdate", return_value=options["today"]),
        ):
            owner, store = seed_evaluation(rich=True)
            for version in versions:
                results = []
                for case in cases:
                    result = (
                        ask_llm(
                            user=owner,
                            store_pk=store.pk,
                            question=case["question"],
                            version=version,
                            backend=options["backend"],
                            **(
                                {"completion": haiku_completion}
                                if options["backend"] == "haiku"
                                else {}
                            ),
                        )
                        if options["backend"] in {"local", "haiku"}
                        else ask(user=owner, store_pk=store.pk, question=case["question"])
                    )
                    score = score_result(case, result, store)
                    results.append({**score, "question": case["question"], "response": result})
                    outcome = "PASS" if score["passed"] else "FAIL " + ",".join(score["errors"])
                    self.stdout.write(f"{version} {case['id']}: {outcome}")
                    self.stdout.flush()
                report["versions"][version] = {
                    "prompt_sha256": hashlib.sha256(
                        (PROMPTS / f"{version}.txt").read_bytes()
                    ).hexdigest(),
                    "gate": eval_gate(results, options["baseline"]),
                    "model_requests": sum(
                        row["response"].get("model_attempted", False) for row in results
                    ),
                    "successful_selections": sum("selection" in row["response"] for row in results),
                    "router_accuracy": {
                        "passed": sum(
                            row["passed"]
                            for row in results
                            if row["response"].get("model_attempted", False)
                        ),
                        "count": sum(
                            row["response"].get("model_attempted", False) for row in results
                        ),
                    },
                    "cases": results,
                }
            transaction.set_rollback(True)
        if len(versions) > 1:
            before, after = (
                report["versions"][version]["cases"] for version in (versions[0], versions[-1])
            )
            before = {row["id"]: row for row in before}
            report["regressions"] = [
                a["id"] for a in after if before[a["id"]]["passed"] and not a["passed"]
            ]
            report["improvements"] = [
                a["id"] for a in after if not before[a["id"]]["passed"] and a["passed"]
            ]
        if options["baseline_file"]:
            previous = json.loads(options["baseline_file"].read_text(encoding="utf-8"))
            last = list(previous["versions"].values())[-1]
            by_id = {row["id"]: row for row in last["cases"]}
            current = report["versions"][versions[-1]]["cases"]
            report["release_comparison"] = {
                "baseline_sha256": hashlib.sha256(
                    options["baseline_file"].read_bytes()
                ).hexdigest(),
                "shared_cases": len(set(by_id) & {row["id"] for row in current}),
                "regressions": [
                    row["id"]
                    for row in current
                    if row["id"] in by_id and by_id[row["id"]]["passed"] and not row["passed"]
                ],
                "improvements": [
                    row["id"]
                    for row in current
                    if row["id"] in by_id and not by_id[row["id"]]["passed"] and row["passed"]
                ],
                "new_cases": [row["id"] for row in current if row["id"] not in by_id],
            }
        output = options["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        with output.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["version", "category", "passed", "count"])
            for version, summary in report["versions"].items():
                for category in sorted({row["category"] for row in summary["cases"]}):
                    rows = [row for row in summary["cases"] if row["category"] == category]
                    writer.writerow(
                        [version, category, sum(row["passed"] for row in rows), len(rows)]
                    )
        gate = report["versions"][versions[-1]]["gate"]
        self.stdout.write(json.dumps(gate, ensure_ascii=False))
        if not gate["passed"]:
            raise CommandError("Eval gate failed; see actual response report")
