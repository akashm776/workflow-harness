from __future__ import annotations

import unittest

from compiler.approval_resolution import resolve_review_required


class ApprovalResolutionTests(unittest.TestCase):
    def test_approved_matching_decision_makes_review_not_required(self) -> None:
        review_required = resolve_review_required(
            node_id="execute-1",
            approval_subject_hash="approval-subject-001",
            approval_decisions={
                "decisions": [
                    {
                        "node_id": "execute-1",
                        "approval_subject_hash": "approval-subject-001",
                        "decision": "approved",
                    }
                ]
            },
        )

        self.assertFalse(review_required)

    def test_missing_decision_keeps_review_required(self) -> None:
        review_required = resolve_review_required(
            node_id="execute-1",
            approval_subject_hash="approval-subject-001",
            approval_decisions={"decisions": []},
        )

        self.assertTrue(review_required)

    def test_wrong_approval_subject_hash_keeps_review_required(self) -> None:
        review_required = resolve_review_required(
            node_id="execute-1",
            approval_subject_hash="approval-subject-001",
            approval_decisions={
                "decisions": [
                    {
                        "node_id": "execute-1",
                        "approval_subject_hash": "approval-subject-other",
                        "decision": "approved",
                    }
                ]
            },
        )

        self.assertTrue(review_required)

    def test_rejected_or_denied_decision_keeps_review_required(self) -> None:
        for field_name, field_value in (
            ("decision", "rejected"),
            ("status", "denied"),
        ):
            review_required = resolve_review_required(
                node_id="execute-1",
                approval_subject_hash="approval-subject-001",
                approval_decisions={
                    "decisions": [
                        {
                            "node_id": "execute-1",
                            "approval_subject_hash": "approval-subject-001",
                            field_name: field_value,
                        }
                    ]
                },
            )

            with self.subTest(field_name=field_name, field_value=field_value):
                self.assertTrue(review_required)

    def test_multiple_conflicting_decisions_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            resolve_review_required(
                node_id="execute-1",
                approval_subject_hash="approval-subject-001",
                approval_decisions={
                    "decisions": [
                        {
                            "node_id": "execute-1",
                            "approval_subject_hash": "approval-subject-001",
                            "decision": "approved",
                        },
                        {
                            "node_id": "execute-1",
                            "approval_subject_hash": "approval-subject-001",
                            "decision": "rejected",
                        },
                    ]
                },
            )


if __name__ == "__main__":
    unittest.main()
