import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.assistant.judge import grade, judge_configuration
from apps.assistant.llm import ModelUnavailable
from apps.assistant.tools import RULES
from qa.acceptance import calibrate

DRAFT_ANSWERS = {
    "stopaj": [
        "Stopaj net satıştan hesaplanır ve hakedişi azaltır; kârın gider kalemi değildir.",
        "Stopaj yalnız net kâr üzerinden hesaplanır.",
        "Kâr ile hakediş farklıdır; stopaj hakedişte kesilir, net kârdan düşülmez.",
        "Stopaj komisyon faturası üzerinden hesaplanır ve satışla ilgisizdir.",
        "Stopaj hakedişi azaltmaz; yalnız raporda bilgi olarak gösterilir.",
    ],
    "kupon": [
        "Platformun karşıladığı kupon satıcının indiriminden ayrı tutulur.",
        "Satıcı indirimi satıcının gelirini azaltır; platform kuponunu platform karşılar.",
        "Her platform kuponunun tamamını satıcı öder.",
        "Satıcı indirimi platform tarafından ödendiğinden satış geliri aynı kalır.",
        "Kuponun kaynağı sonucu değiştirmez; bütün kuponlar satıcının gideridir.",
    ],
    "iade": [
        "İade edilen stok maliyeti geri alınırken gidiş kargosu kalır.",
        "İadede dönüş kargosu eklenir; ilk gidiş kargosu kendiliğinden silinmez.",
        "Tam iadede gidiş kargosu daima eksiksiz geri ödenir.",
        "İade edilen stokun maliyeti kârdan düşülmeye devam eder.",
        "İadenin kargo gideri yoktur; gidiş ve dönüş kargosu sıfırlanır.",
    ],
    "kdv": [
        "Net tutarlardan hesaplanan kâr ile ücret KDV'si düşülen hakediş ayrı sonuçlardır.",
        "Hakedişte platform ücretlerine ait KDV de kesilir.",
        "Kâr KDV dahil satış ile KDV dahil maliyetin farkından oluşur.",
        "Komisyon faturasındaki KDV hakedişi hiçbir zaman değiştirmez.",
        "Hakediş ve kâr aynı vergi tabanından hesaplandığı için her zaman eşittir.",
    ],
    "kargo": [
        "Kargo sipariş başına belirlenir; satırlara en büyük kalan yöntemiyle paylaştırılır.",
        "Çok satırlı siparişte tek kargo gideri satırlar arasında dağıtılır.",
        "Bir siparişin her satırına tam kargo ücretinin tamamı yazılır.",
        "Kargo dağıtımında bütün kuruşlar silinir; yalnız tam lira dağıtılır.",
        "Kargo sadece ilk satıra yazılır ve diğer satırlara hiçbir pay verilmez.",
    ],
    "kur": [
        "Sipariş kuru kayıtlıdır; rapor açıldığında güncel piyasa kuruna dönüşmez.",
        "Yabancı para satışı siparişe kaydedilen sabit kurla TRY olarak raporlanır.",
        "Geçmiş siparişin kuru her raporda canlı kur servisine göre yenilenir.",
        "Yabancı para tutarı TRY'ye çevrilmeden TL raporuna aynen eklenir.",
        "Kur değişince önceki siparişin tüm satış tutarları otomatik yeniden değerlenir.",
    ],
}
BLIND_FIELDS = (
    "id",
    "question",
    "answer",
    "source",
    "answer_sha256",
    "human_pass",
    "human_reason",
    "reviewer",
    "reviewed_at",
)


def read_report(path):
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        rows = report["cases"]
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("Invalid cases")
        return report
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise CommandError("Judge review file cannot be read") from error


def validate_candidates(rows):
    if len(rows) < 30 or len({row.get("id") for row in rows}) != len(rows):
        raise CommandError("At least 30 distinct candidate IDs required")
    texts = set()
    for row in rows:
        if any(
            not isinstance(row.get(field), str) or not row[field].strip()
            for field in ("id", "question", "answer", "source")
        ):
            raise CommandError("Candidate ID/question/answer/source missing")
        if hashlib.sha256(row["answer"].encode("utf-8")).hexdigest() != row.get("answer_sha256"):
            raise CommandError("Calibration answer changed after preparation")
        text = " ".join(row["answer"].split()).casefold()
        if text in texts:
            raise CommandError("At least 30 unique answer texts required")
        texts.add(text)


def write_report(path, report):
    if path.exists():
        raise CommandError(f"Output already exists; choose a new path: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


class Command(BaseCommand):
    help = (
        "Prepare 30 unique blank human drafts, score with a distinct judge, "
        "or calibrate blind reviews."
    )

    def add_arguments(self, parser):
        parser.add_argument("--human-review", type=Path)
        parser.add_argument("--judge-scores", type=Path)
        parser.add_argument("--score", type=Path)
        parser.add_argument("--candidates", type=Path)
        parser.add_argument("--blind-output", type=Path)
        parser.add_argument(
            "--output", type=Path, default=settings.BASE_DIR / "reports/judge-review-30.json"
        )

    def handle(self, *args, **options):
        if options["human_review"]:
            if not options["judge_scores"]:
                raise CommandError("Judge scores missing; provide --judge-scores")
            review = read_report(options["human_review"])
            scores = read_report(options["judge_scores"])
            validate_candidates(review["cases"])
            validate_candidates(scores["cases"])
            if scores.get("same_model_as_assistant") is not False:
                raise CommandError("A distinct judge model is required; no calibration claim")
            if (
                not scores.get("judge_model")
                or not scores.get("assistant_model")
                or (scores["judge_model"].casefold() == scores["assistant_model"].casefold())
            ):
                raise CommandError("Judge model must differ from assistant model")
            by_id = {row["id"]: row for row in scores["cases"]}
            if set(by_id) != {row["id"] for row in review["cases"]}:
                raise CommandError("Human/judge case IDs differ")
            merged = []
            for human in review["cases"]:
                score = by_id[human["id"]]
                if any(
                    human[field] != score[field]
                    for field in ("question", "answer", "source", "answer_sha256")
                ):
                    raise CommandError("Human/judge candidate content changed")
                merged.append({**human, "judge_pass": score.get("judge_pass")})
            try:
                result = calibrate(merged)
            except ValueError as error:
                raise CommandError(str(error)) from error
            self.stdout.write(json.dumps(result))
            if not result["passed"]:
                raise CommandError("Human/judge agreement below 85 percent or degenerate labels")
            return
        if options["score"]:
            if options["output"].exists():
                raise CommandError("Output already exists; choose a new score path")
            report = read_report(options["score"])
            rows = report["cases"]
            validate_candidates(rows)
            try:
                configuration = judge_configuration()
            except ModelUnavailable as error:
                raise CommandError(str(error)) from error
            graded = []
            for row in rows:
                try:
                    score = grade(
                        question=row["question"], answer=row["answer"], source=row["source"]
                    )
                except ModelUnavailable:
                    score = {"judge_pass": None, "unavailable": True}
                graded.append({**row, **score})
                self.stdout.write(
                    f"{row['id']}: judge result saved; human review remains independent"
                )
                self.stdout.flush()
            result = {
                "status": "scored_uncalibrated",
                "sample_origin": report.get("sample_origin", "user selected candidates"),
                "same_model_as_assistant": False,
                "assistant_model": configuration["assistant_model"],
                "judge_model": configuration["judge_model"],
                "model_identity": (
                    "configured names; runtime identity requires separate verification"
                ),
                "human_agreement_percent": None,
                "cases": graded,
            }
            write_report(options["output"], result)
            if any(row.get("judge_pass") is None for row in graded):
                raise CommandError("Some judge calls unavailable; no calibration claim")
            return
        if options["candidates"]:
            report = read_report(options["candidates"])
            rows = report["cases"]
            validate_candidates(rows)
        else:
            rows = []
            for topic, answers in DRAFT_ANSWERS.items():
                for answer in answers:
                    rows.append(
                        {
                            "id": f"J30-{len(rows) + 1:02}",
                            "question": f"{topic} kuralı nasıl uygulanır?",
                            "answer": answer,
                            "source": RULES[topic],
                            "answer_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
                        }
                    )
        prepared = [
            {
                **{
                    field: row[field]
                    for field in ("id", "question", "answer", "source", "answer_sha256")
                },
                "human_pass": None,
                "human_reason": "",
                "reviewer": "",
                "reviewed_at": "",
                "judge_pass": None,
            }
            for row in rows
        ]
        report = {
            "status": "draft_pending_human_selection_and_review",
            "sample_origin": "AI-authored synthetic draft; human must select real unique answers"
            if not options["candidates"]
            else "user selected candidates; human review pending",
            "human_agreement_percent": None,
            "cases": prepared,
        }
        blind_path = options["blind_output"] or options["output"].with_name(
            options["output"].stem + "-blind.json"
        )
        if options["output"] == blind_path or options["output"].exists() or blind_path.exists():
            raise CommandError("Output already exists or blind path equals score path")
        write_report(options["output"], report)
        write_report(
            blind_path,
            {
                "status": "blind_human_review_pending",
                "sample_origin": report["sample_origin"],
                "cases": [{field: row[field] for field in BLIND_FIELDS} for row in prepared],
            },
        )
        self.stdout.write(f"{len(rows)} unique drafts prepared; human labels blank; no judge calls")
