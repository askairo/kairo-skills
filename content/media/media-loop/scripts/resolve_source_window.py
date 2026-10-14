"""Resolve authorized, time-bounded discovery overrides; no config/platform writes."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("override timestamps must include timezone")
    return parsed


def resolve(config, *, account_ref, target_ref, pipeline_ref, strategy_ref, baseline, now):
    if now.tzinfo is None:
        raise ValueError("now must include timezone")
    scope = dict(accountRef=account_ref, targetRef=target_ref,
                 pipelineRef=pipeline_ref, strategyRef=strategy_ref)
    matches = []
    for item in config.get("strategyOverrides", []):
        if item.get("status") != "active" or any(item.get(k) != v for k, v in scope.items()):
            continue
        start, end = timestamp(item["startsAt"]), timestamp(item["expiresAt"])
        if end <= start:
            raise ValueError("override expiresAt must follow startsAt")
        if not start <= now < end:
            continue
        if item.get("authorizedBy") != "user_request" or not item.get("evidenceRef"):
            raise ValueError("active override requires explicit user authorization evidence")
        if not item.get("id") or not item.get("version"):
            raise ValueError("override requires id and version")
        values = item.get("overrides", {})
        if set(values) != {"lookback"} or not re.fullmatch(r"P[1-7]D", values["lookback"]):
            raise ValueError("source-window overrides support only lookback P1D..P7D")
        if item.get("rollbackValue") != baseline:
            raise ValueError("baseline changed; review override before applying")
        matches.append(item)
    if len(matches) > 1:
        raise ValueError("conflicting active source-window overrides")
    result = dict(scope, baselineLookback=baseline, effectiveLookback=baseline,
                  overrideRef=None, resolvedAt=now.isoformat())
    if matches:
        item = matches[0]
        result.update(effectiveLookback=item["overrides"]["lookback"],
                      overrideRef=item["id"], overrideVersion=item["version"],
                      expiresAt=item["expiresAt"], evidenceRef=item["evidenceRef"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(Path.home() / ".agents/local-config/media-loop/config.json"))
    for name in ("account-ref", "target-ref", "pipeline-ref", "strategy-ref", "baseline"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--now", help="timezone-aware ISO time; default current UTC")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    result = resolve(config, account_ref=args.account_ref, target_ref=args.target_ref,
                     pipeline_ref=args.pipeline_ref, strategy_ref=args.strategy_ref,
                     baseline=args.baseline,
                     now=timestamp(args.now) if args.now else datetime.now(timezone.utc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
