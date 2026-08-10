"""Alteryx AMP input tool that launches the embedded DataAI Spark ETL job."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pyarrow as pa
from ayx_python_sdk.core import PluginV2
from ayx_python_sdk.providers.amp_provider.amp_provider_v2 import AMPProviderV2

from .configuration import ConfigurationError, DataAiEtlConfiguration
from .runner import RunResult, run_dataai_job


class DataAiEtlQuality(PluginV2):
    """Execute the DataAI quality pipeline in a customer-controlled Spark runtime."""

    def __init__(self, provider: AMPProviderV2) -> None:
        self.provider = provider
        self.provider.io.info("DataAI ETL quality tool initialized.")

    def on_incoming_connection_complete(self, anchor: NamedTuple) -> None:
        raise NotImplementedError("DataAI ETL Quality is an input-style tool.")

    def on_record_batch(self, batch: pa.Table, anchor: NamedTuple) -> None:
        raise NotImplementedError("DataAI ETL Quality does not receive Alteryx rows.")

    def on_complete(self) -> None:
        try:
            configuration = DataAiEtlConfiguration.from_mapping(
                self.provider.tool_config
            )
            runtime_jar = (
                Path(__file__).resolve().parent
                / "runtime"
                / "dataai-spark-cli-0.1.0-SNAPSHOT.jar"
            )
            result = run_dataai_job(configuration, runtime_jar)
        except (ConfigurationError, FileNotFoundError) as exc:
            result = RunResult(False, 2, str(exc))
        except Exception:
            result = RunResult(
                False,
                1,
                "DataAI ETL could not start. Review local Designer and Spark logs.",
            )

        if result.succeeded:
            self.provider.io.info(result.message)
        else:
            self.provider.io.error(result.message)

        status = pa.table(
            {
                "Status": ["Succeeded" if result.succeeded else "Failed"],
                "ExitCode": [result.exit_code],
                "Message": [result.message],
            }
        )
        self.provider.write_to_anchor("Status", status)
