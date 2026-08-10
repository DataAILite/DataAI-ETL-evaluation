"""Offline tests for the DataAI ETL Alteryx configuration adapter."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND = Path(__file__).resolve().parents[1] / "yxi-source" / "backends"
sys.path.insert(0, str(BACKEND))

from ayx_plugins.configuration import ConfigurationError, DataAiEtlConfiguration
from ayx_plugins.runner import run_dataai_job


def valid_mapping() -> dict[str, object]:
    return {
        "evaluationAccepted": True,
        "sparkSubmit": r"C:\Spark\bin\spark-submit.cmd",
        "master": "local[*]",
        "deployMode": "client",
        "sourceTable": "dataai_eval.customer_orders",
        "cleanTable": "dataai_eval.customer_orders_clean",
        "rejectedTable": "dataai_eval.customer_orders_rejected",
        "profileTable": "dataai_eval.customer_orders_profile",
        "findingsTable": "dataai_eval.customer_orders_findings",
        "normalize": True,
        "recordKeyColumns": "order_id, customer_id",
        "minimumQualityScore": "85",
        "rulesJson": json.dumps(
            [
                {
                    "id": "order-id-required",
                    "type": "REQUIRED",
                    "field": "order_id",
                    "parameter": None,
                    "severity": "ERROR",
                }
            ]
        ),
        "extraSparkArgs": '["--conf", "spark.sql.session.timeZone=UTC"]',
        "timeoutSeconds": "120",
    }


class ConfigurationTests(unittest.TestCase):
    def test_builds_fixed_main_class_command(self) -> None:
        config = DataAiEtlConfiguration.from_mapping(valid_mapping())
        command = config.command(Path("dataai.jar"), Path("job.json"))

        self.assertEqual(command[0], r"C:\Spark\bin\spark-submit.cmd")
        self.assertEqual(command[1:3], ["--class", "com.dataai.etl.spark.cli.DataAiJob"])
        self.assertIn("spark.sql.session.timeZone=UTC", command)
        self.assertEqual(command[-2:], ["--config", "job.json"])

    def test_rejects_arbitrary_executable(self) -> None:
        mapping = valid_mapping()
        mapping["sparkSubmit"] = "powershell.exe"
        with self.assertRaises(ConfigurationError):
            DataAiEtlConfiguration.from_mapping(mapping)

    def test_requires_license_acceptance(self) -> None:
        mapping = valid_mapping()
        mapping["evaluationAccepted"] = False
        with self.assertRaisesRegex(ConfigurationError, "evaluation license"):
            DataAiEtlConfiguration.from_mapping(mapping)

    def test_rejects_class_override(self) -> None:
        mapping = valid_mapping()
        mapping["extraSparkArgs"] = '["--class", "example.Other"]'
        with self.assertRaisesRegex(ConfigurationError, "cannot replace --class"):
            DataAiEtlConfiguration.from_mapping(mapping)

    def test_rejects_invalid_rule_schema(self) -> None:
        mapping = valid_mapping()
        mapping["rulesJson"] = '[{"ruleId":"wrong-shape"}]'
        with self.assertRaisesRegex(ConfigurationError, "unsupported fields"):
            DataAiEtlConfiguration.from_mapping(mapping)

    def test_job_configuration_matches_java_cli_schema(self) -> None:
        config = DataAiEtlConfiguration.from_mapping(valid_mapping())
        job = config.to_job_configuration()

        self.assertEqual(job["sourceTable"], "dataai_eval.customer_orders")
        self.assertEqual(job["recordKeyColumns"], ["order_id", "customer_id"])
        self.assertEqual(job["minimumQualityScore"], 85.0)
        self.assertTrue(job["normalize"])

    def test_runner_uses_shell_false_and_removes_temporary_config(self) -> None:
        config = DataAiEtlConfiguration.from_mapping(valid_mapping())
        with tempfile.TemporaryDirectory() as directory:
            jar = Path(directory) / "dataai.jar"
            jar.write_bytes(b"test")
            observed_config: Path | None = None

            def fake_run(command, **kwargs):
                nonlocal observed_config
                observed_config = Path(command[-1])
                self.assertTrue(observed_config.is_file())
                self.assertFalse(kwargs["shell"])
                self.assertEqual(kwargs["timeout"], 120)
                payload = json.loads(observed_config.read_text(encoding="utf-8"))
                self.assertEqual(payload["sourceTable"], "dataai_eval.customer_orders")

                class Completed:
                    returncode = 0
                    stdout = ""
                    stderr = ""

                return Completed()

            with patch("ayx_plugins.runner.subprocess.run", side_effect=fake_run):
                result = run_dataai_job(config, jar)

            self.assertTrue(result.succeeded)
            self.assertIsNotNone(observed_config)
            self.assertFalse(observed_config.exists())


if __name__ == "__main__":
    unittest.main()
