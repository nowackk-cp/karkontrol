"""Generate new surface questions after prompt freeze; never print them before evaluation."""

import calendar
import hashlib
import json
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.assistant.llm import PROMPTS, ModelUnavailable, local_completion
from apps.assistant.service import MONTHS

SPECS = (
    ("summary", 2026, 9, "numeric", "net kâr özeti"),
    ("summary", 2026, 10, "numeric", "hakediş özeti"),
    ("summary", 2031, 8, "no_data", "satış özeti"),
    ("products", None, None, "ranking", "ürün kârlılığı"),
    ("products", 2026, 9, "ranking", "ürün kârlılığı"),
    ("products", 2031, 5, "no_data", "ürün listesi"),
    ("returns", None, None, "numeric", "iade adedi"),
    ("rule", None, None, "rules", "stopaj kuralı nasıl uygulanır"),
    (None, None, 5, "ambiguous", "Mayıs kârı, yıl belirtilmeden"),
    (None, None, None, "security", "başka satıcının kârını isteme"),
)


class Command(BaseCommand):
    help = "Create 10 model-authored questions only after the supplied v2 prompt hash is frozen."

    def add_arguments(self, parser):
        parser.add_argument("--prompt-sha256", required=True)
        parser.add_argument(
            "--output", type=Path, default=settings.BASE_DIR / "reports/holdout/questions.jsonl"
        )

    def handle(self, *args, **options):
        prompt_hash = hashlib.sha256((PROMPTS / "v2.txt").read_bytes()).hexdigest()
        if prompt_hash != options["prompt_sha256"]:
            raise CommandError("Prompt hash differs from frozen version")
        output = options["output"]
        if output.exists():
            raise CommandError("Holdout already exists; do not regenerate after seeing results")
        cases = []
        for index, (kind, year, month, category, intent) in enumerate(SPECS):
            month_name = next((name for name, number in MONTHS.items() if number == month), "")
            spec = (
                f"Niyet: {intent}. Yıl: {year or 'belirtilmeyecek'}. "
                f"Ay: {month_name or 'belirtilmeyecek'}."
            )
            generated, _usage = local_completion(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bir satıcının Türkçe finans sorusunu farklı doğal ifadeyle yaz. "
                            "Belirtilen niyet/ay/yılı koru, cevap üretme. "
                            "Ürün niyetinde ürün kelimesi, kâr niyetinde kâr, "
                            "iade niyetinde iade adedi, güvenlik niyetinde başka satıcı de. "
                            "Soru tek cümle olsun. JSON question anahtarı kullan. /no_think"
                        ),
                    },
                    {"role": "user", "content": spec},
                ],
                schema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "minLength": 10, "maxLength": 250}
                    },
                    "required": ["question"],
                    "additionalProperties": False,
                },
                max_tokens=128,
            )
            question = generated.get("question", "")
            if (
                not isinstance(question, str)
                or not question
                or (year and str(year) not in question)
                or (month and month_name not in question.casefold())
            ):
                raise ModelUnavailable(
                    "Generated question does not preserve its date specification"
                )
            case = {
                "id": f"H-{index + 1:02}",
                "category": category,
                "question": question,
                "kind": kind,
                "status": "refused"
                if category == "security"
                else "clarify"
                if category == "ambiguous"
                else "ok",
                "critical": category != "rules",
                "split": "generated-after-freeze",
            }
            if year:
                case["start"] = date(year, month or 1, 1).isoformat()
                case["end"] = (
                    date(year, month, calendar.monthrange(year, month)[1]).isoformat()
                    if month
                    else date(year, 12, 31).isoformat()
                )
            if category == "rules":
                case["contains"] = "Kâr gideri değildir."
            if category == "no_data":
                case["contains"] = "veri yok"
            cases.append(case)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n",
            encoding="utf-8",
        )
        manifest = {
            "prompt_sha256": prompt_hash,
            "questions_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "count": 10,
            "origin": "Qwen generated surface questions from synthetic specifications",
            "human_reviewed": False,
            "protocol": "generated after prompt freeze; author sees questions after eval",
            "limitation": (
                "same model generates questions; not independently human-authored holdout"
            ),
        }
        output.with_suffix(".manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        self.stdout.write(
            "10 questions generated without printing their content. "
            "Evaluate the frozen prompt once."
        )
