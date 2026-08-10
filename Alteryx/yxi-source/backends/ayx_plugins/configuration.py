"""Validated configuration and command construction for the Alteryx adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class ConfigurationError(ValueError):
    """Raised when an Alteryx tool configuration is unsafe or incomplete."""


def _value(mapping: Mapping[str, Any], name: str, default: Any = None) -> Any:
    value = mapping.get(name, default)
    if isinstance(value, Mapping) and "@Value" in value:
        return value["@Value"]
    return value


def _text(mapping: Mapping[str, Any], name: str, default: str = "") -> str:
    value = _value(mapping, name, default)
    return "" if value is None else str(value).strip()


def _boolean(mapping: Mapping[str, Any], name: str, default: bool = False) -> bool:
    value = _value(mapping, name, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _json_array(raw: str, name: str) -> list[Any]:
    try:
        value = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"{name} must be valid JSON: {exc.msg}.") from exc
    if not isinstance(value, list):
        raise ConfigurationError(f"{name} must be a JSON array.")
    return value


def _safe_table_name(value: str, name: str, required: bool = False) -> str | None:
    value = value.strip()
    if not value:
        if required:
            raise ConfigurationError(f"{name} is required.")
        return None
    if any(character in value for character in ("\x00", "\r", "\n")):
        raise ConfigurationError(f"{name} contains an unsupported control character.")
    return value


@dataclass(frozen=True)
class DataAiEtlConfiguration:
    """Customer-controlled inputs accepted by the DataAI ETL Alteryx tool."""

    spark_submit: str
    master: str
    deploy_mode: str
    source_table: str
    clean_table: str | None
    rejected_table: str | None
    profile_table: str | None
    findings_table: str | None
    normalize: bool
    record_key_columns: tuple[str, ...]
    rules: tuple[dict[str, Any], ...]
    minimum_quality_score: float | None
    extra_spark_args: tuple[str, ...]
    timeout_seconds: int

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "DataAiEtlConfiguration":
        """Build and validate configuration received from the Designer UI."""
        if "Configuration" in mapping and isinstance(mapping["Configuration"], Mapping):
            mapping = mapping["Configuration"]

        if not _boolean(mapping, "evaluationAccepted"):
            raise ConfigurationError(
                "Accept the evaluation license in the DataAI ETL tool configuration."
            )

        spark_submit = _text(mapping, "sparkSubmit", "spark-submit.cmd")
        executable_name = Path(spark_submit).name.lower()
        if executable_name not in {
            "spark-submit",
            "spark-submit.cmd",
            "spark-submit.bat",
            "spark-submit.exe",
        }:
            raise ConfigurationError(
                "Spark Submit must point to spark-submit, spark-submit.cmd, "
                "spark-submit.bat, or spark-submit.exe."
            )

        deploy_mode = _text(mapping, "deployMode", "client").lower()
        if deploy_mode not in {"client", "cluster"}:
            raise ConfigurationError("Deploy Mode must be client or cluster.")

        master = _text(mapping, "master", "local[*]")
        if not master or any(character in master for character in ("\x00", "\r", "\n")):
            raise ConfigurationError("Spark Master is required and must be one line.")

        record_keys = tuple(
            part.strip()
            for part in _text(mapping, "recordKeyColumns").split(",")
            if part.strip()
        )

        raw_rules = _json_array(_text(mapping, "rulesJson", "[]"), "Rules JSON")
        rules: list[dict[str, Any]] = []
        allowed_rule_keys = {"id", "type", "field", "parameter", "severity"}
        allowed_rule_types = {
            "REQUIRED",
            "UNIQUE",
            "MINIMUM",
            "MAXIMUM",
            "BETWEEN",
            "IN_SET",
            "DATE_FORMAT",
            "LENGTH",
            "EQUALS",
            "REGEX",
        }
        allowed_severities = {"INFO", "WARNING", "ERROR", "CRITICAL"}
        for index, rule in enumerate(raw_rules):
            if not isinstance(rule, dict):
                raise ConfigurationError(f"Rule {index + 1} must be a JSON object.")
            unknown_keys = set(rule) - allowed_rule_keys
            if unknown_keys:
                raise ConfigurationError(
                    f"Rule {index + 1} has unsupported fields: "
                    f"{', '.join(sorted(unknown_keys))}."
                )
            for required_name in ("id", "type", "field"):
                if not isinstance(rule.get(required_name), str) or not str(
                    rule[required_name]
                ).strip():
                    raise ConfigurationError(
                        f"Rule {index + 1} requires a non-empty {required_name}."
                    )
            if str(rule["type"]).upper() not in allowed_rule_types:
                raise ConfigurationError(f"Rule {index + 1} has an unsupported type.")
            severity = rule.get("severity", "ERROR")
            if not isinstance(severity, str) or severity.upper() not in allowed_severities:
                raise ConfigurationError(f"Rule {index + 1} has an unsupported severity.")
            parameter = rule.get("parameter")
            if parameter is not None and not isinstance(parameter, str):
                raise ConfigurationError(
                    f"Rule {index + 1} parameter must be a string or null."
                )
            rules.append(rule)

        raw_extra_args = _json_array(
            _text(mapping, "extraSparkArgs", "[]"), "Extra Spark Arguments"
        )
        extra_args: list[str] = []
        for argument in raw_extra_args:
            if not isinstance(argument, str) or not argument.strip():
                raise ConfigurationError(
                    "Every Extra Spark Arguments item must be a non-empty string."
                )
            if any(character in argument for character in ("\x00", "\r", "\n")):
                raise ConfigurationError("Extra Spark Arguments must be one-line values.")
            if argument.strip().lower() == "--class":
                raise ConfigurationError("Extra Spark Arguments cannot replace --class.")
            extra_args.append(argument)

        minimum_score_text = _text(mapping, "minimumQualityScore")
        minimum_score: float | None = None
        if minimum_score_text:
            try:
                minimum_score = float(minimum_score_text)
            except ValueError as exc:
                raise ConfigurationError(
                    "Minimum Quality Score must be a number from 0 through 100."
                ) from exc
            if not 0.0 <= minimum_score <= 100.0:
                raise ConfigurationError(
                    "Minimum Quality Score must be from 0 through 100."
                )

        timeout_text = _text(mapping, "timeoutSeconds", "3600")
        try:
            timeout_seconds = int(timeout_text)
        except ValueError as exc:
            raise ConfigurationError("Timeout Seconds must be a whole number.") from exc
        if not 1 <= timeout_seconds <= 86400:
            raise ConfigurationError("Timeout Seconds must be from 1 through 86400.")

        return cls(
            spark_submit=spark_submit,
            master=master,
            deploy_mode=deploy_mode,
            source_table=_safe_table_name(
                _text(mapping, "sourceTable"), "Source Table", required=True
            )
            or "",
            clean_table=_safe_table_name(_text(mapping, "cleanTable"), "Clean Table"),
            rejected_table=_safe_table_name(
                _text(mapping, "rejectedTable"), "Rejected Table"
            ),
            profile_table=_safe_table_name(
                _text(mapping, "profileTable"), "Profile Table"
            ),
            findings_table=_safe_table_name(
                _text(mapping, "findingsTable"), "Findings Table"
            ),
            normalize=_boolean(mapping, "normalize", True),
            record_key_columns=record_keys,
            rules=tuple(rules),
            minimum_quality_score=minimum_score,
            extra_spark_args=tuple(extra_args),
            timeout_seconds=timeout_seconds,
        )

    def to_job_configuration(self) -> dict[str, Any]:
        """Return the JSON object consumed by the shaded DataAI Spark CLI."""
        return {
            "sourceTable": self.source_table,
            "cleanTable": self.clean_table,
            "rejectedTable": self.rejected_table,
            "profileTable": self.profile_table,
            "findingsTable": self.findings_table,
            "normalize": self.normalize,
            "recordKeyColumns": list(self.record_key_columns),
            "rules": list(self.rules),
            "minimumQualityScore": self.minimum_quality_score,
        }

    def command(self, runtime_jar: Path, configuration_file: Path) -> list[str]:
        """Build an argument vector; it is never passed through a command shell."""
        return [
            self.spark_submit,
            "--class",
            "com.dataai.etl.spark.cli.DataAiJob",
            "--master",
            self.master,
            "--deploy-mode",
            self.deploy_mode,
            *self.extra_spark_args,
            str(runtime_jar),
            "--config",
            str(configuration_file),
        ]


def masked_command(command: Sequence[str]) -> str:
    """Return a non-secret operational summary, not the literal argument list."""
    return f"{Path(command[0]).name} [DataAI ETL arguments omitted]"
