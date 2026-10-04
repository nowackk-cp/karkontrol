"""Run actual model prompts against the SQL fixture in a rolled-back transaction."""

import hashlib
import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.assistant.llm import PROMPTS, ask_llm
from apps.assistant.service import ask
from qa.acceptance import eval_gate
from qa.evaluation import score_result, seed_evaluation


class Command(BaseCommand):
    help = "Actual local LLM/offline eval; fixture data always rolled back."

    def add_arguments(self, parser):
        parser.add_argument("--backend", choices=["local", "offline"], default="local")
        parser.add_argument("--versions", default="v1,v2")
        parser.add_argument(
            "--cases", type=Path, default=settings.BASE_DIR / "tests/eval/questions.jsonl"
        )
        parser.add_argument(
            "--output", type=Path, default=settings.BASE_DIR / "reports/llm-eval.json"
        )
        parser.add_argument("--baseline", type=float, default=100)

    def handle(self, *args, **options):
        versions = options["versions"].split(",")
        if any(version not in {"v1", "v2"} for version in versions):
            raise CommandError("Unknown prompt version")
        cases = [
            json.loads(line)
            for line in options["cases"].read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        report = {
            "backend": options["backend"],
            "model": os.getenv("KARKONTROL_LLM_MODEL", "Qwen3-1.7B-Q8_0")
            if options["backend"] == "local"
            else None,
            "dataset_sha256": hashlib.sha256(options["cases"].read_bytes()).hexdigest(),
            "numeric_oracle": "parameterized SQL on synthetic ledger, integer cents",
            "human_judge_calibrated": False,
            "versions": {},
        }
        with transaction.atomic():
            owner, store = seed_evaluation()
            for version in versions:
                results = []
                for case in cases:
                    result = (
                        ask_llm(
                            user=owner,
                            store_pk=store.pk,
                            question=case["question"],
                            version=version,
                        )
                        if options["backend"] == "local"
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
                    "model_requests": sum("selection" in row["response"] for row in results),
                    "cases": results,
                }
            transaction.set_rollback(True)
        if len(versions) > 1:
            before, after = (
                report["versions"][version]["cases"] for version in (versions[0], versions[-1])
            )
            report["regressions"] = [
                a["id"]
                for b, a in zip(before, after, strict=True)
                if b["passed"] and not a["passed"]
            ]
            report["improvements"] = [
                a["id"]
                for b, a in zip(before, after, strict=True)
                if not b["passed"] and a["passed"]
            ]
        output = options["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        gate = report["versions"][versions[-1]]["gate"]
        self.stdout.write(json.dumps(gate, ensure_ascii=False))
        if not gate["passed"]:
            raise CommandError("Eval gate failed; see actual response report")
