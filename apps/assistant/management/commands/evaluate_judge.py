import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.assistant.judge import grade
from apps.assistant.llm import ModelUnavailable
from apps.assistant.tools import RULES
from qa.acceptance import calibrate

NEGATIVE = {
    "stopaj": "Stopaj net kârın gideridir; hakedişi hiç etkilemez.",
    "kupon": "Platform kuponunu tamamen satıcı karşılar; satış geliri azalır.",
    "iade": "Tam iadede gidiş kargosu her zaman tamamen iade edilir.",
    "kdv": "Hakedişte komisyon faturasının KDV'si düşülmez.",
    "kargo": "Her sipariş satırına ayrı bir tam kargo ücreti yazılır.",
    "kur": "Sipariş kuru her rapor açılışında canlı piyasa kuruyla değiştirilir.",
}


class Command(BaseCommand):
    help = (
        "Save 20 actual judge scores with blank human fields, or calibrate human-reviewed scores."
    )

    def add_arguments(self, parser):
        parser.add_argument("--human-review", type=Path)
        parser.add_argument(
            "--output", type=Path, default=settings.BASE_DIR / "reports/judge-review.json"
        )

    def handle(self, *args, **options):
        if options["human_review"]:
            rows = json.loads(options["human_review"].read_text(encoding="utf-8"))["cases"]
            if any(
                hashlib.sha256(row["answer"].encode()).hexdigest() != row["answer_sha256"]
                for row in rows
            ):
                raise CommandError("Calibration answer changed after judge scoring")
            try:
                result = calibrate(rows)
            except ValueError as error:
                raise CommandError(str(error)) from error
            self.stdout.write(json.dumps(result))
            if not result["passed"]:
                raise CommandError("Human/judge agreement below 85 percent")
            return
        rows = []
        for index in range(20):
            topic = list(RULES)[index % len(RULES)]
            answer = RULES[topic] if index < 10 else NEGATIVE[topic]
            question = f"{topic} kuralı nasıl uygulanır?"
            try:
                score = grade(question=question, answer=answer, source=RULES[topic])
            except ModelUnavailable:
                score = {"judge_pass": None, "unavailable": True}
            identifier = f"J-{index + 1:02}"
            rows.append(
                {
                    "id": identifier,
                    "question": question,
                    "answer": answer,
                    "source": RULES[topic],
                    "answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
                    **score,
                    "human_pass": None,
                    "reviewer": "",
                    "reviewed_at": "",
                }
            )
            self.stdout.write(f"{identifier}: model score saved; human review missing")
            self.stdout.flush()
        report = {
            "status": "uncalibrated",
            "sample_origin": "AI-authored synthetic rubric candidates",
            "same_model_as_assistant": True,
            "human_agreement_percent": None,
            "cases": rows,
        }
        options["output"].parent.mkdir(parents=True, exist_ok=True)
        options["output"].write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        if any(row["judge_pass"] is None for row in rows):
            raise CommandError("Some real judge calls unavailable; no calibration claim")
