import json
import sys
from pathlib import Path

REQUIRED = {
    "runId", "runType", "accountRef", "platform", "window", "dataQuality",
    "phase", "outcome", "reasonCode", "idempotencyKey", "healthStatus",
    "inventoryStatus", "artifactRefs", "nextAction", "resumeCondition",
    "strategyVersion", "experimentRefs", "writeBackStatus", "cleanupStatus",
}
OUTCOMES = {"success", "blocked", "skipped", "retryable_failure", "unknown", "data_insufficient"}
EXPECTED = {
    "published": ("success", "published"),
    "adaptation_backlog": ("blocked", "adaptation_backlog_present"),
    "adaptation_backlog_unchanged": ("skipped", "adaptation_backlog_unchanged"),
    "ready_supply_starved": ("blocked", "ready_supply_starved"),
    "published_pending_review": ("success", "published_pending_review"),
    "publish_unconfirmed": ("unknown", "publish_unconfirmed"),
}


def validate(path: Path) -> None:
    scenarios = json.loads(path.read_text(encoding="utf-8"))
    names = {item.get("name") for item in scenarios}
    errors = []

    if names != set(EXPECTED):
        errors.append(f"scenario names: expected {sorted(EXPECTED)}, got {sorted(names)}")

    for item in scenarios:
        name = item.get("name", "<missing>")
        record = item.get("record", {})
        missing = REQUIRED - record.keys()
        if missing:
            errors.append(f"{name}: missing {sorted(missing)}")
        if record.get("outcome") not in OUTCOMES:
            errors.append(f"{name}: invalid outcome {record.get('outcome')!r}")
        if name in EXPECTED and (record.get("outcome"), record.get("reasonCode")) != EXPECTED[name]:
            errors.append(f"{name}: expected outcome/reason {EXPECTED[name]}")
        if not record.get("nextAction") or not record.get("resumeCondition"):
            errors.append(f"{name}: nextAction and resumeCondition must be non-empty")

    unchanged = next((item["record"] for item in scenarios if item.get("name") == "adaptation_backlog_unchanged"), {})
    if unchanged.get("sideEffects"):
        errors.append("adaptation_backlog_unchanged: sideEffects must be empty")
    if unchanged.get("inventoryStatus") != "adaptation_backlog":
        errors.append("adaptation_backlog_unchanged: inventoryStatus must remain adaptation_backlog")

    starved = next((item["record"] for item in scenarios if item.get("name") == "ready_supply_starved"), {})
    if starved.get("inventoryStatus") != "ready_supply_starved":
        errors.append("ready_supply_starved: inventoryStatus must be ready_supply_starved")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"validated {len(scenarios)} runtime-contract scenarios")


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[1] / "references" / "acceptance-scenarios.json"
    validate(Path(sys.argv[1]) if len(sys.argv) > 1 else default)
