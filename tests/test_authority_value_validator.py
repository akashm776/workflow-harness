from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from compiler.authority_value_validator import (
    DisallowedAuthorityValueError,
    assert_no_disallowed_authority_values,
    find_disallowed_authority_values,
)
from compiler.compile_run import compile_static_artifacts


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
INPUT_FILES = (
    "WorkflowSpec.json",
    "NodeTypeRegistry.json",
    "RequestedAuth.json",
    "ApprovalRequests.json",
)


class AuthorityValueValidatorUnitTests(unittest.TestCase):
    def test_integer_fields_are_accepted(self) -> None:
        self.assertEqual(
            find_disallowed_authority_values({"timeout": 30, "retries": 0}),
            [],
        )

    def test_bool_fields_are_accepted_and_not_treated_as_ints(self) -> None:
        self.assertEqual(
            find_disallowed_authority_values({"review_required": True, "auto": False}),
            [],
        )

    def test_float_is_rejected_including_integral_float(self) -> None:
        findings = find_disallowed_authority_values({"timeout": 1.0})

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["path"], "$.timeout")
        self.assertEqual(findings[0]["reason"], "float")

    def test_nan_is_rejected(self) -> None:
        findings = find_disallowed_authority_values({"score": float("nan")})

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["reason"], "non-finite-nan")

    def test_infinity_is_rejected(self) -> None:
        findings = find_disallowed_authority_values(
            {"a": float("inf"), "b": float("-inf")}
        )

        reasons = sorted(finding["reason"] for finding in findings)
        self.assertEqual(
            reasons,
            ["non-finite-infinity", "non-finite-negative-infinity"],
        )

    def test_path_is_reported_for_nested_array_value(self) -> None:
        findings = find_disallowed_authority_values(
            {"requested_tools": [{"scope": 1.0}]}
        )

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["path"], "$.requested_tools[0].scope")

    def test_assert_raises_with_artifact_name_and_path(self) -> None:
        with self.assertRaises(DisallowedAuthorityValueError) as caught:
            assert_no_disallowed_authority_values(
                {"requested_tools": [{"scope": 1.0}]},
                artifact_name="RequestedAuth.json",
            )

        message = str(caught.exception)
        self.assertEqual(caught.exception.artifact_name, "RequestedAuth.json")
        self.assertIn("RequestedAuth.json", message)
        self.assertIn("$.requested_tools[0].scope", message)


class AuthorityValueCompileIntegrationTests(unittest.TestCase):
    def _compile_with_modified_input(self, file_name: str, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            for name in INPUT_FILES:
                shutil.copy(SIMPLE_FIXTURE_INPUT / name, tmp_dir / name)

            data = json.loads(
                (SIMPLE_FIXTURE_INPUT / file_name).read_text(encoding="utf-8")
            )
            modify(data)
            # allow_nan=True so NaN/Infinity can be written for characterization.
            (tmp_dir / file_name).write_text(
                json.dumps(data, allow_nan=True), encoding="utf-8"
            )

            return compile_static_artifacts(
                tmp_dir / "WorkflowSpec.json",
                tmp_dir / "NodeTypeRegistry.json",
                tmp_dir / "RequestedAuth.json",
                tmp_dir / "ApprovalRequests.json",
                repo_root=tmp_dir,
            )

    def _compile_with_modified_requested_auth(self, modify) -> dict:
        return self._compile_with_modified_input("RequestedAuth.json", modify)

    def _assert_disallowed_failure(self, result: dict) -> dict:
        self.assertFalse(result["ok"])
        report = result["artifacts"]["CompilationReport.json"]
        self.assertEqual(report["status"], "failed")
        diagnostics = [
            diagnostic
            for diagnostic in report["diagnostics"]
            if diagnostic["error_code"] == "DISALLOWED_AUTHORITY_VALUE"
        ]
        self.assertEqual(len(diagnostics), 1)
        return diagnostics[0]

    def test_valid_fixture_still_compiles(self) -> None:
        result = compile_static_artifacts(
            SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json",
            SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
            SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
            SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        self.assertTrue(result["ok"])

    def test_float_in_requested_auth_fails_compile(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"][0]["timeout"] = 1.0

        diagnostic = self._assert_disallowed_failure(
            self._compile_with_modified_requested_auth(modify)
        )

        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("RequestedAuth.json", diagnostic["message"])
        self.assertIn("$.requested_tools[0].timeout", diagnostic["message"])

    def test_nan_in_requested_auth_fails_compile(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"][0]["timeout"] = float("nan")

        diagnostic = self._assert_disallowed_failure(
            self._compile_with_modified_requested_auth(modify)
        )

        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("non-finite-nan", diagnostic["message"])

    def test_infinity_in_requested_auth_fails_compile(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"][0]["timeout"] = float("inf")

        diagnostic = self._assert_disallowed_failure(
            self._compile_with_modified_requested_auth(modify)
        )

        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("non-finite-infinity", diagnostic["message"])

    def test_integer_in_requested_auth_remains_accepted(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"][0]["timeout"] = 30

        result = self._compile_with_modified_requested_auth(modify)

        self.assertTrue(result["ok"])

    def test_bool_in_requested_auth_remains_accepted(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"][0]["elevated"] = True

        result = self._compile_with_modified_requested_auth(modify)

        self.assertTrue(result["ok"])

    def _compile_with_modified_approval_decisions(self, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            for name in (*INPUT_FILES, "ApprovalDecisions.json"):
                shutil.copy(SIMPLE_FIXTURE_INPUT / name, tmp_dir / name)

            approval_decisions = json.loads(
                (SIMPLE_FIXTURE_INPUT / "ApprovalDecisions.json").read_text(
                    encoding="utf-8"
                )
            )
            modify(approval_decisions)
            (tmp_dir / "ApprovalDecisions.json").write_text(
                json.dumps(approval_decisions, allow_nan=True), encoding="utf-8"
            )

            return compile_static_artifacts(
                tmp_dir / "WorkflowSpec.json",
                tmp_dir / "NodeTypeRegistry.json",
                tmp_dir / "RequestedAuth.json",
                tmp_dir / "ApprovalRequests.json",
                repo_root=tmp_dir,
                approval_decisions_path=tmp_dir / "ApprovalDecisions.json",
            )

    def test_float_in_approval_decisions_is_rejected_when_present(self) -> None:
        def modify(approval_decisions: dict) -> None:
            approval_decisions["decisions"][0]["weight"] = 1.0

        diagnostic = self._assert_disallowed_failure(
            self._compile_with_modified_approval_decisions(modify)
        )

        self.assertEqual(diagnostic["artifact"], "ApprovalDecisions.json")
        self.assertIn("$.decisions[0].weight", diagnostic["message"])

    def test_nan_in_approval_decisions_is_rejected_when_present(self) -> None:
        def modify(approval_decisions: dict) -> None:
            approval_decisions["decisions"][0]["weight"] = float("nan")

        diagnostic = self._assert_disallowed_failure(
            self._compile_with_modified_approval_decisions(modify)
        )

        self.assertEqual(diagnostic["artifact"], "ApprovalDecisions.json")
        self.assertIn("non-finite-nan", diagnostic["message"])

    def test_nan_in_workflow_revision_id_fails_compile(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["workflow_revision_id"] = float("nan")

        diagnostic = self._assert_disallowed_failure(
            self._compile_with_modified_input("WorkflowSpec.json", modify)
        )

        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.workflow_revision_id", diagnostic["message"])

    def test_nan_in_workflow_revision_id_does_not_leak_into_emitted_artifacts(
        self,
    ) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["workflow_revision_id"] = float("nan")

        result = self._compile_with_modified_input("WorkflowSpec.json", modify)

        self.assertFalse(result["ok"])
        self.assertEqual(
            find_disallowed_authority_values(
                result["artifacts"]["CompilationReport.json"]
            ),
            [],
        )
        self.assertEqual(
            find_disallowed_authority_values(
                result["artifacts"]["CompiledArtifactIndex.json"]
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
