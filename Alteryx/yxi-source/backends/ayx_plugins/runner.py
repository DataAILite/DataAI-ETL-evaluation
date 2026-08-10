"""Local Spark process execution for the Alteryx adapter."""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .configuration import DataAiEtlConfiguration


@dataclass(frozen=True)
class RunResult:
    """Non-sensitive execution result returned to the Designer tool."""

    succeeded: bool
    exit_code: int
    message: str


def run_dataai_job(
    configuration: DataAiEtlConfiguration,
    runtime_jar: Path,
) -> RunResult:
    """Run DataAI through customer-selected spark-submit without a command shell."""
    runtime_jar = runtime_jar.resolve()
    if not runtime_jar.is_file():
        raise FileNotFoundError(f"DataAI runtime JAR is missing: {runtime_jar.name}")

    with tempfile.TemporaryDirectory(prefix="dataai-etl-alteryx-") as temp_directory:
        configuration_file = Path(temp_directory) / "job-config.json"
        configuration_file.write_text(
            json.dumps(configuration.to_job_configuration(), indent=2),
            encoding="utf-8",
        )
        command = configuration.command(runtime_jar, configuration_file)
        try:
            completed = subprocess.run(
                command,
                shell=False,
                check=False,
                capture_output=True,
                text=True,
                timeout=configuration.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                False,
                124,
                "DataAI ETL Spark execution timed out. Review customer-controlled Spark logs.",
            )
        except OSError as exc:
            return RunResult(
                False,
                127,
                f"spark-submit could not be started ({exc.__class__.__name__}).",
            )

    if completed.returncode == 0:
        return RunResult(True, 0, "DataAI ETL Spark execution completed successfully.")
    return RunResult(
        False,
        int(completed.returncode),
        "DataAI ETL Spark execution failed. Review customer-controlled Spark logs.",
    )
