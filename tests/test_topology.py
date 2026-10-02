import unittest
from aquaflow.api import AquaFlowService
from aquaflow.network.topology import Revision, at

def _rows():
    return [
        Revision(revision=1, sequence=10, open_pipes=frozenset({"P1"})),
        Revision(revision=2, sequence=20, open_pipes=frozenset({"P1", "P2"})),
        # Future revision: sequence beyond any historical query below.
        Revision(revision=3, sequence=30, open_pipes=frozenset({"P9"})),
    ]

class TopologyHistoryTest(unittest.TestCase):
    def test_future_revision_does_not_leak(self):
        # Querying at sequence 20 must not expose the sequence-30 revision.
        chosen = at(20, _rows())
        self.assertEqual(chosen.revision, 2)
        self.assertEqual(chosen.sequence, 20)
        self.assertEqual(chosen.open_pipes, frozenset({"P1", "P2"}))

    def test_between_sequences_stays_on_older_revision(self):
        # Sequence 25 has no exact revision; latest effective <= 25 is seq 20.
        chosen = at(25, _rows())
        self.assertEqual(chosen.revision, 2)

    def test_two_revisions_same_sequence_are_deterministic(self):
        rows = [
            Revision(revision=5, sequence=10, open_pipes=frozenset({"OLD"})),
            Revision(revision=7, sequence=10, open_pipes=frozenset({"NEW"})),
        ]
        # Higher revision id wins regardless of input ordering.
        self.assertEqual(at(10, rows).revision, 7)
        self.assertEqual(at(10, list(reversed(rows))).revision, 7)

    def test_before_first_revision_raises(self):
        with self.assertRaises(ValueError):
            at(5, _rows())

    def test_service_returns_revision_and_open_pipe_evidence(self):
        response = AquaFlowService().topology(20, _rows())
        self.assertEqual(response["revision"].revision, 2)
        self.assertEqual(response["open_pipes"], frozenset({"P1", "P2"}))
        # The future revision's evidence must be absent.
        self.assertNotIn("P9", response["open_pipes"])

if __name__ == "__main__":
    unittest.main()
