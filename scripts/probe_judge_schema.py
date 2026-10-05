"""Compare decoder schemas with the same actual model, prompt and candidate."""

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django  # noqa: E402

django.setup()

from apps.assistant import judge  # noqa: E402
from apps.assistant.llm import ModelUnavailable  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--candidates", type=Path, default=Path("data/draft/judge_candidates30.json"))
parser.add_argument("--output", type=Path, default=Path("reports/judge-schema-probe.json"))
options = parser.parse_args()
if options.output.exists():
    raise SystemExit("Output already exists; choose a new probe path")
candidate = json.loads(options.candidates.read_text(encoding="utf-8"))["cases"][0]
completion = judge.local_completion
results = []
prompt_hashes = set()
for label, bounded in (("old_bounded", True), ("new_unbounded", False)):

    def run_completion(*, bounded_schema=bounded, **kwargs):
        request = copy.deepcopy(kwargs)
        prompt_hashes.add(
            hashlib.sha256(json.dumps(request["messages"], ensure_ascii=False).encode()).hexdigest()
        )
        reason = request["schema"]["properties"]["reason"]
        if bounded_schema:
            reason["maxLength"] = 300
        else:
            reason.pop("maxLength", None)
        return completion(**request)

    judge.local_completion = run_completion
    started = time.monotonic()
    try:
        score = judge.grade(
            question=candidate["question"], answer=candidate["answer"], source=candidate["source"]
        )
        result = {"completed": True, "score": score}
    except ModelUnavailable as error:
        result = {"completed": False, "error": str(error)}
    finally:
        judge.local_completion = completion
    results.append({"schema": label, "elapsed_seconds": time.monotonic() - started, **result})
    print(f"{label}: completed={result['completed']}", flush=True)
assert len(prompt_hashes) == 1, "Compared prompts must be identical"
report = {
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "candidate_id": candidate["id"],
    "candidate_sha256": candidate["answer_sha256"],
    "prompt_sha256": next(iter(prompt_hashes)),
    "judge_model": judge.judge_configuration()["judge_model"],
    "post_validation_max_reason_length": 300,
    "same_prompt_and_token_budget": True,
    "human_calibrated": False,
    "results": results,
}
options.output.parent.mkdir(parents=True, exist_ok=True)
with options.output.open("x", encoding="utf-8") as output:
    json.dump(report, output, indent=2, ensure_ascii=False)
    output.write("\n")
if not results[-1]["completed"]:
    raise SystemExit("New schema failed the actual model probe")
