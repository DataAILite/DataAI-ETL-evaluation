#!/usr/bin/env python3
"""Offline structural validation for the DataAI IRIS evaluation package."""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-SNAPSHOT"
JAR_NAME = f"dataai-spark-iris-{VERSION}.jar"
TEXT_EXTENSIONS = {".cls", ".csv", ".java", ".json", ".md", ".py", ".sql", ".svg", ".xml"}


def require_files() -> None:
    names = [
        "pom.xml", "README.md", "LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md",
        "THIRD_PARTY_NOTICES.md", "manifest.json", "CHECKSUMS.sha256",
        "mapping/IRIS_OUTPUT_SCHEMA.md", "mapping/FUNCTION_OUTPUTS_FOR_IRIS.md",
        "examples/java/IrisDataAiPipelineExample.java", "examples/java/IrisMatrixBalancingExample.java",
        "examples/sql/iris_setup.sql", "examples/spark-submit/README.md",
        "ipm/module.xml", "ipm/src/DataAI/ETL/Status.cls", "ipm/README.md",
        "listing/INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md",
        "assets/dataai-iris-icon.svg", "assets/dataai-iris-icon.png",
        "screenshots/iris-pipeline.png", "screenshots/iris-data-quality.png",
        "distribution/DataAI_ETL_IRIS_Evaluation.zip", f"target/{JAR_NAME}",
    ]
    missing = [name for name in names if not (ROOT / name).is_file()]
    assert not missing, f"Missing required files: {missing}"


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    handling = manifest["dataHandling"]
    assert manifest["adapterCoordinate"] == f"com.dataai:dataai-spark-iris:{VERSION}"
    assert handling == {
        "hostedService": False,
        "requiredDataAiNetworkCalls": False,
        "telemetry": False,
        "automaticWrites": False,
        "bundledIrisDriver": False,
    }


def csv_rows(name: str) -> list[dict[str, str]]:
    with (ROOT / "sample-data" / name).open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def validate_sample_data() -> None:
    orders = csv_rows("customer_orders.csv")
    assert len(orders) == 6 and all(row["Order ID"] for row in orders)
    cells = csv_rows("matrix_cells.csv")
    rows = csv_rows("matrix_row_targets.csv")
    columns = csv_rows("matrix_column_targets.csv")
    assert len(cells) == 4 and len(rows) == 2 and len(columns) == 2
    row_total = sum(float(row["target_total"]) for row in rows)
    column_total = sum(float(row["target_total"]) for row in columns)
    assert abs(row_total - column_total) < 1e-9, "Matrix target totals must match."


def validate_ipm() -> None:
    root = ElementTree.parse(ROOT / "ipm" / "module.xml").getroot()
    assert root.findtext("./Document/Module/Name") == "dataai-etl-iris"
    assert root.findtext("./Document/Module/Version") == "0.1.0"
    assert root.find("./Document/Module/Resource") is not None


def validate_images() -> None:
    expected = {
        "assets/dataai-iris-icon.png": (512, 512),
        "screenshots/iris-pipeline.png": (1440, 900),
        "screenshots/iris-data-quality.png": (1440, 900),
    }
    for name, size in expected.items():
        with Image.open(ROOT / name) as image:
            assert image.size == size, f"Unexpected image size for {name}: {image.size}"
            image.verify()


def validate_distribution() -> None:
    package = ROOT / "distribution" / "DataAI_ETL_IRIS_Evaluation.zip"
    with zipfile.ZipFile(package) as archive:
        names = set(archive.namelist())
        assert archive.testzip() is None, "Evaluation ZIP contains a corrupt member."
        for name in names:
            path = PurePosixPath(name)
            assert not path.is_absolute() and ".." not in path.parts, f"Unsafe ZIP path: {name}"
        required = {"README.md", "LICENSE.md", "manifest.json", f"lib/{JAR_NAME}", "ipm/module.xml"}
        assert required <= names, f"Evaluation ZIP is missing: {sorted(required - names)}"
        assert not any("intersystems-jdbc" in name.lower() for name in names), "IRIS JDBC driver must not be bundled."


def validate_crlf() -> None:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS or "target" in path.parts:
            continue
        data = path.read_bytes()
        if b"\n" in data.replace(b"\r\n", b""):
            failures.append(path.relative_to(ROOT).as_posix())
    assert not failures, f"Text files with non-CRLF newlines: {failures}"


def validate_checksums() -> None:
    lines = (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8-sig").splitlines()
    entries = {}
    for line in lines:
        digest, name = line.split("  ", 1)
        entries[name] = digest
    required = {"LICENSE.md", "manifest.json", f"target/{JAR_NAME}", "distribution/DataAI_ETL_IRIS_Evaluation.zip"}
    assert required <= entries.keys(), f"Checksum manifest is missing: {sorted(required - entries.keys())}"
    for name, expected in entries.items():
        path = ROOT / Path(name)
        assert path.is_file(), f"Checksum path does not exist: {name}"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, f"Checksum mismatch: {name}"


def validate_marketplace_copy() -> None:
    listing = (ROOT / "listing" / "INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md").read_text(encoding="utf-8-sig")
    assert "FICTIONAL" in (ROOT / "screenshots" / "iris-pipeline.png").name.upper() or "fictional" in listing.lower()
    assert "Send for Approval" in listing
    assert "[DATAAI IRIS EVALUATION URL]" in listing, "Keep launch placeholders visible until release approval."


def main() -> None:
    require_files()
    validate_manifest()
    validate_sample_data()
    validate_ipm()
    validate_images()
    validate_distribution()
    validate_crlf()
    validate_checksums()
    validate_marketplace_copy()
    print("IRIS package validation passed.")
    print("Publication gate remains: test against the exact customer IRIS server and JDBC driver.")


if __name__ == "__main__":
    main()
