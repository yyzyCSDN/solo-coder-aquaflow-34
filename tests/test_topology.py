import unittest
from aquaflow.api import AquaFlowService
from aquaflow.network.topology import Revision, at


def rev(revision, sequence, pipes):
    return Revision(revision, sequence, frozenset(pipes))


class TopologyAtTest(unittest.TestCase):
    def test_future_revision_does_not_leak(self):
        rows = [
            rev(1, 10, ["P1"]),
            rev(2, 20, ["P1", "P2"]),
        ]
        picked = at(10, rows)
        self.assertEqual(picked.revision, 1)
        self.assertEqual(picked.sequence, 10)
        self.assertEqual(picked.open_pipes, frozenset(["P1"]))

    def test_past_query_uses_latest_effective_revision(self):
        rows = [
            rev(1, 10, ["P1"]),
            rev(2, 20, ["P1", "P2"]),
            rev(3, 30, ["P1", "P2", "P3"]),
        ]
        picked = at(25, rows)
        self.assertEqual(picked.revision, 2)
        self.assertEqual(picked.open_pipes, frozenset(["P1", "P2"]))

    def test_same_sequence_picks_higher_revision_deterministically(self):
        lower_first = [rev(1, 10, ["P1"]), rev(2, 10, ["P1", "P2"])]
        higher_first = [rev(2, 10, ["P1", "P2"]), rev(1, 10, ["P1"])]
        for rows in (lower_first, higher_first):
            picked = at(10, rows)
            self.assertEqual(picked.revision, 2)
            self.assertEqual(picked.sequence, 10)
            self.assertEqual(picked.open_pipes, frozenset(["P1", "P2"]))

    def test_before_first_revision_raises(self):
        rows = [rev(1, 10, ["P1"]), rev(2, 20, ["P1", "P2"])]
        with self.assertRaises(ValueError):
            at(9, rows)


class TopologyWorkflowTest(unittest.TestCase):
    def service_rows(self):
        return [
            {"revision": 1, "sequence": 10, "open_pipes": ["P1"]},
            {"revision": 2, "sequence": 20, "open_pipes": ["P1", "P2"]},
        ]

    def test_service_future_revision_does_not_leak(self):
        result = AquaFlowService().run_workflow(
            "topology_revision", {"sequence": 10, "revisions": self.service_rows()}
        )
        self.assertEqual(result["decision"], "use")
        self.assertEqual(result["value"], 1)
        self.assertEqual(result["evidence"], {"open_pipes": ["P1"]})
        self.assertEqual(result["workflow"], "topology_revision")

    def test_service_same_sequence_deterministic(self):
        revisions = [
            {"revision": 1, "sequence": 10, "open_pipes": ["P1"]},
            {"revision": 2, "sequence": 10, "open_pipes": ["P1", "P2"]},
        ]
        result = AquaFlowService().run_workflow(
            "topology_revision", {"sequence": 10, "revisions": revisions}
        )
        self.assertEqual(result["value"], 2)
        self.assertEqual(result["evidence"], {"open_pipes": ["P1", "P2"]})

    def test_service_before_first_revision_raises(self):
        with self.assertRaises(ValueError):
            AquaFlowService().run_workflow(
                "topology_revision", {"sequence": 9, "revisions": self.service_rows()}
            )


if __name__ == "__main__":
    unittest.main()
