import copy
import unittest
from resolve_source_window import resolve, timestamp


class SourceWindowTests(unittest.TestCase):
    def setUp(self):
        self.scope = dict(account_ref="account", target_ref="account-platform",
                          pipeline_ref="pipeline", strategy_ref="strategy", baseline="P1D")
        self.item = dict(id="window-v1", version=1, status="active", accountRef="account",
                         targetRef="account-platform", pipelineRef="pipeline", strategyRef="strategy",
                         startsAt="2026-10-14T00:00:00+08:00", expiresAt="2026-10-21T00:00:00+08:00",
                         authorizedBy="user_request", evidenceRef="loop/authorized-experiment.md",
                         overrides={"lookback": "P2D"}, rollbackValue="P1D")

    def run_at(self, when, items=None, **scope):
        return resolve({"strategyOverrides": [self.item] if items is None else items},
                       **(self.scope | scope), now=timestamp(when))

    def test_active_and_timezone(self):
        self.assertEqual(self.run_at("2026-10-13T16:00:00Z")["effectiveLookback"], "P2D")

    def test_start_end_and_missing(self):
        for when in ("2026-10-13T23:59:59+08:00", "2026-10-21T00:00:00+08:00"):
            self.assertEqual(self.run_at(when)["effectiveLookback"], "P1D")
        self.assertIsNone(self.run_at("2026-10-14T19:20:00+08:00", [])["overrideRef"])

    def test_scope_isolated(self):
        for key in ("account_ref", "target_ref", "pipeline_ref", "strategy_ref"):
            self.assertEqual(self.run_at("2026-10-14T19:20:00+08:00", **{key: "other"})["effectiveLookback"], "P1D")

    def test_no_config_mutation(self):
        before = copy.deepcopy(self.item)
        self.run_at("2026-10-14T19:20:00+08:00")
        self.assertEqual(before, self.item)

    def test_reject_unauthorized_and_gate_changes(self):
        for change in ({"authorizedBy": "inferred"}, {"evidenceRef": ""},
                       {"overrides": {"lookback": "P2D", "minScore": 0}},
                       {"overrides": {"lookback": "P20Y"}}, {"rollbackValue": "P3D"},
                       {"expiresAt": "2026-10-10T00:00:00+08:00"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_at("2026-10-14T19:20:00+08:00", [self.item | change])

    def test_conflict_and_inactive(self):
        with self.assertRaises(ValueError):
            self.run_at("2026-10-14T19:20:00+08:00", [self.item, self.item | {"id": "second"}])
        self.assertEqual(self.run_at("2026-10-14T19:20:00+08:00", [self.item | {"status": "stopped"}])["effectiveLookback"], "P1D")


if __name__ == "__main__":
    unittest.main()
