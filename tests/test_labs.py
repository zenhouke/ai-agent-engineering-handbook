import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from labs.attention import example, softmax
from labs.gradient import update
from labs.recovery import demonstration
from labs.retrieval import evaluate, retrieve


class TeachingMechanisms(unittest.TestCase):
    def test_gradient_known_derivative(self):
        weight, loss = update(1, 0.1)
        self.assertAlmostEqual(weight, 1.8)
        self.assertAlmostEqual(loss, 0.16)

    def test_large_step_can_increase_loss(self):
        self.assertAlmostEqual(update(1, 0.3)[1], 7.84)

    def test_softmax_is_shift_invariant(self):
        for a, b in zip(
            softmax([1, 0], [True, True]), softmax([1001, 1000], [True, True])
        ):
            self.assertAlmostEqual(a, b)

    def test_known_attention(self):
        weights, output = example(False)
        self.assertAlmostEqual(sum(weights), 1)
        self.assertAlmostEqual(output[0], 1.4621171573)

    def test_mask_removes_future_position(self):
        weights, output = example(True)
        self.assertEqual(weights, [1, 0])
        self.assertEqual(output, [2, 0])

    def test_all_masked_is_an_error(self):
        with self.assertRaises(ValueError):
            softmax([1, 0], [False, False])

    def test_unauthorized_candidates_never_appear(self):
        candidates = retrieve("A", {"delivery", "price", "quantity"}, 10)
        self.assertEqual(
            {chunk.chunk_id for chunk in candidates}, {"quote", "condition"}
        )
        self.assertEqual(retrieve("unknown", {"delivery"}, 10), [])

    def test_partial_evidence_is_not_complete(self):
        self.assertEqual(evaluate({"quote"}, {"quote", "condition"}), (0.5, False))
        self.assertEqual(
            evaluate({"quote", "condition"}, {"quote", "condition"}), (1, True)
        )

    def test_crash_and_reopen_does_not_duplicate_external_draft(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            receipt, count = demonstration(Path(directory))
        self.assertEqual(receipt, "draft-1")
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
