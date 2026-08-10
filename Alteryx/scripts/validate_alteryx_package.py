"""Offline validation for the DataAI ETL Alteryx marketplace package."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
YXI = ROOT / "build" / "DataAI_ETL_Alteryx_2026_1_Evaluation.yxi"
EVALUATION = ROOT / "distribution" / "DataAI_ETL_Alteryx_Evaluation.zip"
SUBMISSION = PROJECT_ROOT / "DataAIETLAlteryx.zip"
TEXT_SUFFIXES = {".md", ".py", ".json", ".xml", ".txt", ".csv", ".svg", ".tsx", ".js"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def archive_names(path: Path) -> set[str]:
    require(path.is_file(), f"Missing archive: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
    for name in names:
        require(not name.startswith(("/", "\\")), f"Absolute archive entry: {name}")
        require(".." not in Path(name).parts, f"Traversal archive entry: {name}")
    return names


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["provider"] == "Yanbor LLC", "Provider is incorrect.")
    require(manifest["submissionReady"] is False, "Unvalidated candidate claims ready.")
    require(
        manifest["alteryx"]["externalDesignerValidation"] is False,
        "Unexecuted Designer validation is claimed.",
    )
    require(manifest["alteryx"]["ayxPythonSdk"] == "2.5.3", "SDK pin changed.")
    require(manifest["dataHandling"]["hostedService"] is False, "Hosted-service claim changed.")
    require(manifest["dataHandling"]["telemetry"] is False, "Telemetry claim changed.")
    require(
        manifest["dataHandling"]["configuredOutputTablesUseOverwrite"] is True,
        "Output behavior is not disclosed.",
    )


def validate_source() -> None:
    backend = ROOT / "yxi-source" / "backends" / "ayx_plugins"
    source = "\n".join(path.read_text(encoding="utf-8") for path in backend.glob("*.py"))
    require("shell=False" in source, "Subprocess shell control is missing.")
    require("shell=True" not in source, "Unsafe shell execution found.")
    require("subprocess.run" in source, "Spark process runner is missing.")
    require("requests." not in source, "Unexpected HTTP client usage found.")
    require("socket." not in source, "Unexpected socket usage found.")
    require("telemetry" not in source.lower(), "Telemetry code marker found.")

    runtime_jar = backend / "runtime" / "dataai-spark-cli-0.1.0-SNAPSHOT.jar"
    canonical = ROOT / "lib" / runtime_jar.name
    require(runtime_jar.is_file(), "Packaged runtime JAR is missing.")
    require(digest(runtime_jar) == digest(canonical), "YXI runtime JAR differs from evaluation JAR.")


def validate_licenses_and_docs() -> None:
    for name in ("LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        require("AS IS" in text, f"{name} lacks AS IS text.")
        require(
            re.search(r"no\s+obligation", text, re.IGNORECASE) is not None,
            f"{name} lacks no-obligation text.",
        )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("proprietary, source-available evaluation software" in readme, "Required positioning is absent.")
    usage = (ROOT / "docs" / "INSTALLATION_AND_USAGE.md").read_text(encoding="utf-8")
    require("overwritten" in usage.lower(), "Usage guide omits overwrite disclosure.")
    require((ROOT / "docs" / "FUNCTION_CATALOG.md").is_file(), "Function catalog is missing.")


def validate_yxi() -> None:
    names = archive_names(YXI)
    required = {
        "Config.xml",
        "dataai-alteryx-icon.png",
        "DataAiEtlQuality_1_0/DataAiEtlQuality_1_0Config.xml",
        "DataAiEtlQuality_1_0/manifest.json",
        "DataAiEtlQuality_1_0/main.pyz",
        "DataAiEtlQuality_1_0/index.html",
        "DataAiEtlQuality_1_0/site-packages/ayx_plugins/data_ai_etl_quality.py",
        "DataAiEtlQuality_1_0/site-packages/ayx_plugins/runtime/dataai-spark-cli-0.1.0-SNAPSHOT.jar",
    }
    require(required.issubset(names), f"YXI is missing: {sorted(required - names)}")
    require(
        any(name.startswith("DataAiEtlQuality_1_0/site-packages/ayx_python_sdk/") for name in names),
        "AYX Python SDK is missing from YXI.",
    )
    require(
        any(name.startswith("DataAiEtlQuality_1_0/") and name.endswith(".js") for name in names),
        "Compiled tool UI JavaScript is missing.",
    )


def validate_evaluation_and_submission() -> None:
    evaluation_names = archive_names(EVALUATION)
    prefix = "DataAI_ETL_Alteryx_Evaluation/"
    require(prefix + f"install/{YXI.name}" in evaluation_names, "Evaluation ZIP lacks YXI.")
    require(prefix + "LICENSE.md" in evaluation_names, "Evaluation ZIP lacks license.")
    require(
        prefix + "docs/FUNCTION_CATALOG.md" in evaluation_names,
        "Evaluation ZIP lacks function catalog.",
    )

    submission_names = archive_names(SUBMISSION)
    root = "DataAIETLAlteryx/"
    require(root + "MARKETPLACE_SUBMISSION.md" in submission_names, "Submission guide missing.")
    require(root + "PROVIDER_CHECKLIST.md" in submission_names, "Provider checklist missing.")
    require(
        root + "distribution/DataAI_ETL_Alteryx_Evaluation.zip" in submission_names,
        "Submission ZIP lacks evaluation distribution.",
    )
    require(
        root + "yxi-source/backends/ayx_plugins/runner.py" in submission_names,
        "Submission ZIP lacks inspectable adapter source.",
    )


def validate_checksums() -> None:
    for line in (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
        expected, relative = re.split(r"\s{2,}", line, maxsplit=1)
        path = ROOT / relative
        require(path.is_file(), f"Checksum target missing: {relative}")
        require(digest(path) == expected, f"Checksum mismatch: {relative}")
    outer = SUBMISSION.with_suffix(SUBMISSION.suffix + ".sha256")
    expected, name = re.split(r"\s{2,}", outer.read_text(encoding="utf-8").strip(), maxsplit=1)
    require(name == SUBMISSION.name, "Outer checksum filename is incorrect.")
    require(expected == digest(SUBMISSION), "Outer submission checksum mismatch.")


def validate_crlf() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in {"node_modules", "dist", "__pycache__"} for part in path.parts):
            continue
        data = path.read_bytes()
        require(b"\n" not in data.replace(b"\r\n", b""), f"Non-CRLF text: {path}")


def run_unit_tests() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v"],
        shell=False,
        check=False,
    )
    require(completed.returncode == 0, "Alteryx adapter unit tests failed.")


def main() -> None:
    validate_manifest()
    validate_source()
    validate_licenses_and_docs()
    validate_yxi()
    validate_evaluation_and_submission()
    validate_checksums()
    validate_crlf()
    run_unit_tests()
    print("DataAI ETL Alteryx package validation passed.")


if __name__ == "__main__":
    main()
