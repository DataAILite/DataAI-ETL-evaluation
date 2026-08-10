#!/usr/bin/env python3
"""Offline validation for the DataAI Databricks Marketplace package."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
VERSION = "0.1.0-SNAPSHOT"
MODULES = (
    "dataai-spark-api",
    "dataai-spark-quality",
    "dataai-spark-core",
    "dataai-spark-functions",
    "dataai-spark-cli",
)
STATEMENT = (
    "DataAI ETL is proprietary, source-available evaluation software from "
    "Yanbor LLC, built with open-source technologies including Apache Spark."
)
TEXT_EXTENSIONS = {".csv", ".json", ".md", ".py", ".sha256", ".sql", ".svg", ".txt"}


def require_files() -> None:
    required = [
        "README.md",
        "MARKETPLACE_SUBMISSION.md",
        "PROVIDER_CHECKLIST.md",
        "LICENSE.md",
        "COMMERCIAL_LICENSE_TEMPLATE.md",
        "THIRD_PARTY_NOTICES.md",
        "manifest.json",
        "CHECKSUMS.sha256",
        "listing/DATABRICKS_MARKETPLACE_LISTING.md",
        "docs/INSTALLATION_AND_USAGE.md",
        "docs/RUNTIME_COMPATIBILITY.md",
        "docs/SECURITY_AND_DATA_HANDLING.md",
        "docs/FUNCTION_CATALOG.md",
        "assets/dataai-databricks-icon.png",
        "assets/dataai-databricks-icon.svg",
        "screenshots/databricks-quality.png",
        "screenshots/databricks-matrix.png",
        "data/customer_orders.csv",
        "data/matrix_cells.csv",
        "data/matrix_row_targets.csv",
        "data/matrix_column_targets.csv",
        "sql/CREATE_PROVIDER_ASSETS.sql",
        "sql/CREATE_CONSUMER_OUTPUTS.sql",
        "configs/cluster-library-paths.json",
        "configs/evaluation-job-template.json",
        "notebooks/00_INSTALL_AND_VERIFY.py",
        "notebooks/01_QUALITY_PIPELINE.py",
        "notebooks/02_ANALYTICS_AND_MARKET.py",
        "notebooks/03_MATRIX_BALANCING.py",
        "notebooks/04_PUBLISH_FOR_BI.py",
        "distribution/EVALUATION_CHECKSUMS.sha256",
        "distribution/DataAI_ETL_Databricks_Evaluation.zip",
    ]
    required.extend(f"lib/{module}-{VERSION}.jar" for module in MODULES)
    missing = [name for name in required if not (ROOT / name).is_file()]
    missing.extend(
        name for name in ("DataAIETLDatabricks.zip", "DataAIETLDatabricks.zip.sha256")
        if not (REPOSITORY / name).is_file()
    )
    assert not missing, f"Required files are missing: {missing}"


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    assert manifest["provider"] == "Yanbor LLC"
    assert manifest["providerDescription"] == "provider of the DataAI product"
    assert manifest["packageVersion"] == VERSION
    assert manifest["packageStatus"] == "evaluation-development"
    assert manifest["listing"]["assetTypes"] == ["files", "notebooks"]
    assert manifest["listing"]["availability"] == "personalized-provider-approval"
    assert len(manifest["listing"]["name"]) < 100
    assert len(manifest["listing"]["shortDescription"]) <= 160
    assert manifest["runtime"]["java"] == "17"
    assert manifest["runtime"]["scalaBinary"] == "2.12"
    assert manifest["runtime"]["externalDatabricksValidation"] is False
    assert all(value is False for value in manifest["dataHandling"].values())

    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    listing = (ROOT / "listing" / "DATABRICKS_MARKETPLACE_LISTING.md").read_text(encoding="utf-8-sig")
    assert STATEMENT in readme
    assert STATEMENT in listing
    assert "not been executed on an external Databricks workspace" in readme


def validate_json() -> None:
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8-sig"))


def validate_notebooks() -> None:
    notebooks = sorted((ROOT / "notebooks").glob("*.py"))
    assert len(notebooks) == 5
    for path in notebooks:
        source = path.read_text(encoding="utf-8-sig")
        assert source.startswith("# Databricks notebook source")
        assert source.count("# COMMAND ----------") >= 2
        ast.parse(source, filename=str(path))

    quality = (ROOT / "notebooks" / "01_QUALITY_PIPELINE.py").read_text(encoding="utf-8-sig")
    assert '"persist_results", "false"' in quality
    assert "DataAiPipeline.fromDataset" in quality
    assert "RuleSpec.required" in quality
    assert "RuleSpec.unique" in quality
    assert "RuleSpec.between" in quality
    assert "RuleSpec.dateFormat" in quality
    assert "RuleSpec.inSet" in quality

    matrix = (ROOT / "notebooks" / "03_MATRIX_BALANCING.py").read_text(encoding="utf-8-sig")
    assert "MatrixFunctions.balance" in matrix
    assert "maximumError" in matrix
    assert "converged" in matrix

    publish = (ROOT / "notebooks" / "04_PUBLISH_FOR_BI.py").read_text(encoding="utf-8-sig")
    assert '"publish_views", "false"' in publish


def validate_data() -> None:
    with (ROOT / "data" / "customer_orders.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        orders = list(csv.DictReader(handle))
    assert len(orders) == 12
    assert any(not row["customer_id"] for row in orders)
    assert len({row["order_id"] for row in orders}) < len(orders)
    assert any(row["order_date"] == "not-a-date" for row in orders)
    assert any(float(row["amount"]) < 0 for row in orders)
    assert all(row["customer_id"].startswith("CUST-") for row in orders if row["customer_id"])

    with (ROOT / "data" / "matrix_row_targets.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        row_targets = list(csv.DictReader(handle))
    with (ROOT / "data" / "matrix_column_targets.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        column_targets = list(csv.DictReader(handle))
    row_total = sum(float(row["target"]) for row in row_targets)
    column_total = sum(float(row["target"]) for row in column_targets)
    assert row_total == column_total == 420.0


def validate_images() -> None:
    expected = {
        "assets/dataai-databricks-icon.png": (512, 512),
        "screenshots/databricks-quality.png": (1600, 900),
        "screenshots/databricks-matrix.png": (1600, 900),
    }
    for name, size in expected.items():
        with Image.open(ROOT / name) as image:
            assert image.size == size, f"Unexpected dimensions for {name}: {image.size}"


def validate_jars() -> None:
    required_entries = {
        "dataai-spark-api": "com/dataai/etl/spark/api/DataAiResult.class",
        "dataai-spark-quality": "com/dataai/etl/spark/quality/QualityEvaluator.class",
        "dataai-spark-core": "com/dataai/etl/spark/core/DataAiPipeline.class",
        "dataai-spark-functions": "com/dataai/etl/spark/functions/MatrixFunctions.class",
        "dataai-spark-cli": "com/dataai/etl/spark/cli/DataAiJob.class",
    }
    for module, required in required_entries.items():
        path = ROOT / "lib" / f"{module}-{VERSION}.jar"
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, f"Corrupt JAR: {path.name}"
            names = set(archive.namelist())
            assert required in names, f"{required} missing from {path.name}"
            forbidden = [
                name for name in names
                if name.startswith("org/apache/spark/") or name.startswith("org/apache/hadoop/")
            ]
            assert not forbidden, f"Spark/Hadoop classes bundled in {path.name}: {forbidden[:3]}"

    with zipfile.ZipFile(ROOT / "lib" / f"dataai-spark-functions-{VERSION}.jar") as archive:
        names = set(archive.namelist())
        for class_name in (
            "AnalyticsFunctions",
            "BusinessFunctions",
            "DataQualityFunctions",
            "InsightFunctions",
            "MapFunctions",
            "MarketFunctions",
            "MatrixFunctions",
            "TimeSeriesFunctions",
        ):
            assert f"com/dataai/etl/spark/functions/{class_name}.class" in names


def validate_checksum_file(path: Path, base: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        digest, name = line.split("  ", 1)
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
        target = base / PurePosixPath(name)
        assert target.is_file(), f"Checksum path missing: {name}"
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, f"Checksum mismatch: {name}"
        entries[name] = digest
    return entries


def validate_checksums() -> None:
    entries = validate_checksum_file(ROOT / "CHECKSUMS.sha256", ROOT)
    required = {
        "LICENSE.md",
        "manifest.json",
        f"lib/dataai-spark-functions-{VERSION}.jar",
        "notebooks/03_MATRIX_BALANCING.py",
        "distribution/DataAI_ETL_Databricks_Evaluation.zip",
    }
    assert required <= entries.keys(), f"Main checksums missing: {sorted(required - entries.keys())}"

    evaluation_entries = validate_checksum_file(
        ROOT / "distribution" / "EVALUATION_CHECKSUMS.sha256",
        ROOT,
    )
    assert f"lib/dataai-spark-core-{VERSION}.jar" in evaluation_entries
    assert "notebooks/00_INSTALL_AND_VERIFY.py" in evaluation_entries

    digest, name = (REPOSITORY / "DataAIETLDatabricks.zip.sha256").read_text(
        encoding="utf-8-sig"
    ).strip().split("  ", 1)
    assert name == "DataAIETLDatabricks.zip"
    assert hashlib.sha256((REPOSITORY / name).read_bytes()).hexdigest() == digest


def validate_zip(path: Path, prefix: str, required: set[str]) -> None:
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f"Corrupt archive: {path.name}"
        names = set(archive.namelist())
    expected = {f"{prefix}/{name}" for name in required}
    assert expected <= names, f"{path.name} missing: {sorted(expected - names)}"


def validate_archives() -> None:
    validate_zip(
        ROOT / "distribution" / "DataAI_ETL_Databricks_Evaluation.zip",
        "DataAI_ETL_Databricks_Evaluation",
        {
            "README.md",
            "LICENSE.md",
            "CHECKSUMS.sha256",
            f"lib/dataai-spark-functions-{VERSION}.jar",
            "notebooks/00_INSTALL_AND_VERIFY.py",
            "notebooks/03_MATRIX_BALANCING.py",
            "data/customer_orders.csv",
            "docs/FUNCTION_CATALOG.md",
        },
    )
    validate_zip(
        REPOSITORY / "DataAIETLDatabricks.zip",
        "Databricks",
        {
            "README.md",
            "MARKETPLACE_SUBMISSION.md",
            "PROVIDER_CHECKLIST.md",
            "LICENSE.md",
            "CHECKSUMS.sha256",
            "listing/DATABRICKS_MARKETPLACE_LISTING.md",
            "distribution/DataAI_ETL_Databricks_Evaluation.zip",
        },
    )


def validate_text() -> None:
    forbidden_patterns = {
        "Databricks personal access token": re.compile(r"\bdapi[0-9a-zA-Z]{20,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        assert b"\n" not in raw.replace(b"\r\n", b""), f"Non-CRLF line ending: {path}"
        for label, pattern in forbidden_patterns.items():
            assert not pattern.search(text), f"Possible {label} in {path}"


def main() -> None:
    require_files()
    validate_manifest()
    validate_json()
    validate_notebooks()
    validate_data()
    validate_images()
    validate_jars()
    validate_archives()
    validate_checksums()
    validate_text()
    print("DataAI Databricks Marketplace package validation passed.")
    print("External gates remain: provider approval, public URLs, immutable release, and actual Databricks runtime execution.")


if __name__ == "__main__":
    main()
