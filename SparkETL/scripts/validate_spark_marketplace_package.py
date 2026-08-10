#!/usr/bin/env python3
"""Offline validation for the DataAI Spark marketplace submission kit."""

from __future__ import annotations

import hashlib
import json
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
TEXT_EXTENSIONS = {
    ".csv", ".java", ".json", ".md", ".properties", ".py", ".sql",
    ".svg", ".txt", ".xml",
}


def require_files() -> None:
    required = [
        "README.md", "MARKETPLACE_SUBMISSION.md", "LICENSE.md",
        "COMMERCIAL_LICENSE_TEMPLATE.md", "THIRD_PARTY_NOTICES.md",
        "manifest.json", "CHECKSUMS.sha256",
        "listing/SPARK_MARKETPLACE_LISTING.md",
        "assets/dataai-spark-icon.png", "assets/dataai-spark-icon.svg",
        "screenshots/spark-pipeline.png", "screenshots/spark-functions.png",
        "docs/INSTALLATION_AND_USAGE.md", "docs/FUNCTION_CATALOG.md",
        "distribution/DataAI_ETL_Spark_Evaluation.zip",
        "poms/dataai-etl-spark-parent.pom", "source/spark/README.md",
    ]
    for module in MODULES:
        required.extend(
            [
                f"lib/{module}-{VERSION}.jar",
                f"lib/{module}-{VERSION}-sources.jar",
                f"lib/{module}-{VERSION}-javadoc.jar",
                f"poms/{module}.pom",
            ]
        )
    missing = [name for name in required if not (ROOT / name).is_file()]
    missing.extend(
        name for name in ("SparkETL.zip", "SparkETL.zip.sha256")
        if not (REPOSITORY / name).is_file()
    )
    assert not missing, f"Missing required files: {missing}"


def validate_identity_and_manifest() -> None:
    assert STATEMENT in (ROOT / "README.md").read_text(encoding="utf-8-sig")
    assert STATEMENT in (ROOT / "source" / "spark" / "README.md").read_text(encoding="utf-8-sig")
    license_text = (ROOT / "LICENSE.md").read_text(encoding="utf-8-sig")
    assert "Copyright © 2026 Yanbor LLC" in license_text
    assert "Copyright © 2026 DataAI." not in license_text
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    assert manifest["provider"] == "Yanbor LLC"
    assert manifest["packageVersion"] == VERSION
    assert manifest["dataHandling"] == {
        "hostedService": False,
        "requiredDataAiNetworkCalls": False,
        "telemetry": False,
        "automaticWrites": False,
        "bundledSpark": False,
        "bundledHadoop": False,
    }


def validate_images() -> None:
    expected = {
        "assets/dataai-spark-icon.png": (512, 512),
        "screenshots/spark-pipeline.png": (1440, 900),
        "screenshots/spark-functions.png": (1440, 900),
    }
    for name, size in expected.items():
        with Image.open(ROOT / name) as image:
            assert image.size == size, f"Unexpected image size for {name}: {image.size}"
            image.verify()


def validate_jars() -> None:
    for module in MODULES:
        path = ROOT / "lib" / f"{module}-{VERSION}.jar"
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, f"Corrupt JAR: {path.name}"
            names = archive.namelist()
            forbidden = [
                name for name in names
                if name.startswith("org/apache/spark/") or name.startswith("org/apache/hadoop/")
            ]
            assert not forbidden, f"Spark/Hadoop classes bundled in {path.name}: {forbidden[:3]}"
            if module == "dataai-spark-cli":
                manifest = archive.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
                assert "com.dataai.etl.spark.cli.DataAiJob" in manifest


def validate_zip(path: Path, prefix: str, required: set[str]) -> None:
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f"Corrupt ZIP member in {path.name}"
        names = set(archive.namelist())
        for name in names:
            pure = PurePosixPath(name)
            assert not pure.is_absolute() and ".." not in pure.parts and "\\" not in name, f"Unsafe ZIP path: {name}"
        expected = {f"{prefix}/{name}" for name in required}
        assert expected <= names, f"{path.name} is missing: {sorted(expected - names)}"


def validate_archives() -> None:
    validate_zip(
        ROOT / "distribution" / "DataAI_ETL_Spark_Evaluation.zip",
        "DataAI_ETL_Spark_Evaluation",
        {"README.md", "LICENSE.md", f"lib/dataai-spark-cli-{VERSION}.jar", "docs/FUNCTION_CATALOG.md"},
    )
    validate_zip(
        REPOSITORY / "SparkETL.zip",
        "SparkETL",
        {"README.md", "MARKETPLACE_SUBMISSION.md", "LICENSE.md", f"lib/dataai-spark-functions-{VERSION}.jar", "CHECKSUMS.sha256"},
    )


def validate_checksums() -> None:
    entries = {}
    for line in (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8-sig").splitlines():
        digest, name = line.split("  ", 1)
        entries[name] = digest
    assert "SparkETL.zip" not in entries
    required = {"LICENSE.md", "manifest.json", f"lib/dataai-spark-cli-{VERSION}.jar", "distribution/DataAI_ETL_Spark_Evaluation.zip"}
    assert required <= entries.keys(), f"Checksum entries missing: {sorted(required - entries.keys())}"
    for name, expected in entries.items():
        path = ROOT / Path(name)
        assert path.is_file(), f"Checksum path missing: {name}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"Checksum mismatch: {name}"
    archive_digest, archive_name = (REPOSITORY / "SparkETL.zip.sha256").read_text(
        encoding="utf-8-sig").strip().split("  ", 1)
    assert archive_name == "SparkETL.zip"
    assert hashlib.sha256((REPOSITORY / archive_name).read_bytes()).hexdigest() == archive_digest


def validate_text() -> None:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        data = path.read_bytes()
        if b"\n" in data.replace(b"\r\n", b""):
            failures.append(path.relative_to(ROOT).as_posix())
    assert not failures, f"Non-CRLF text files: {failures}"
    listing = (ROOT / "listing" / "SPARK_MARKETPLACE_LISTING.md").read_text(encoding="utf-8-sig")
    assert "[DATAAI SPARK EVALUATION URL]" in listing
    assert "0.1.0-SNAPSHOT" in listing


def main() -> None:
    require_files()
    validate_identity_and_manifest()
    validate_images()
    validate_jars()
    validate_archives()
    validate_checksums()
    validate_text()
    print("DataAI Spark marketplace package validation passed.")
    print("Publication gates remain: immutable version, verified namespace, complete POM metadata, PGP signatures, SBOM, and target-channel approval.")


if __name__ == "__main__":
    main()
