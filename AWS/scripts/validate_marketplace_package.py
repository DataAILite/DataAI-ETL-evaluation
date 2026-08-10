#!/usr/bin/env python3
"""Validate a generated DataAI cloud-marketplace or Maven review package."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
CHANNEL = ROOT.name
VERSION = "0.1.0-SNAPSHOT"
MODULES = (
    "dataai-spark-api",
    "dataai-spark-quality",
    "dataai-spark-core",
    "dataai-spark-functions",
    "dataai-spark-cli",
)
ARCHIVES = {
    "AWS": "DataAIETLAWS.zip",
    "Microsoft": "DataAIETLMicrosoft.zip",
    "Oracle": "DataAIETLOracle.zip",
    "Google": "DataAIETLGoogle.zip",
    "Maven": "DataAIETLMaven.zip",
}
STATEMENT = (
    "DataAI ETL is proprietary, source-available evaluation software from "
    "Yanbor LLC, built with open-source technologies including Apache Spark."
)
TEXT_EXTENSIONS = {
    ".csv", ".json", ".md", ".pom", ".py", ".sha256", ".sql", ".svg", ".txt", ".xml"
}


def require_files() -> None:
    assert CHANNEL in ARCHIVES, f"Unsupported package folder: {CHANNEL}"
    required = [
        "README.md",
        "MARKETPLACE_SUBMISSION.md",
        "PROVIDER_CHECKLIST.md",
        "LICENSE.md",
        "COMMERCIAL_LICENSE_TEMPLATE.md",
        "THIRD_PARTY_NOTICES.md",
        "manifest.json",
        "CHECKSUMS.sha256",
        f"listing/{CHANNEL.upper()}_LISTING.md",
        "docs/INSTALLATION_AND_USAGE.md",
        "docs/RELEASE_GATES.md",
        "docs/FUNCTION_CATALOG.md",
        f"assets/dataai-{CHANNEL.lower()}-icon.png",
        f"assets/dataai-{CHANNEL.lower()}-icon-130.png",
        f"assets/dataai-{CHANNEL.lower()}-icon.svg",
        f"screenshots/{CHANNEL.lower()}-pipeline.png",
        f"screenshots/{CHANNEL.lower()}-functions.png",
        f"distribution/DataAI_ETL_{CHANNEL}_Evaluation.zip",
        "distribution/EVALUATION_CHECKSUMS.sha256",
        "scripts/generate_marketplace_package.py",
        "scripts/validate_marketplace_package.py",
    ]
    if CHANNEL == "Maven":
        required.extend(
            [
                "central/settings.xml.template",
                "central/central-publishing-plugin.xml",
                "central/MAVEN_CENTRAL_UPLOAD_BLOCKED.txt",
                "poms/dataai-etl-spark-parent.pom",
            ]
        )
        for module in MODULES:
            required.append(f"poms/{module}.pom")
            for classifier in ("", "-sources", "-javadoc"):
                required.append(f"lib/{module}-{VERSION}{classifier}.jar")
    else:
        required.extend(["container/Dockerfile", "container/README.md"])
        required.extend(f"lib/{module}-{VERSION}.jar" for module in MODULES)

    missing = [name for name in required if not (ROOT / name).is_file()]
    archive = ARCHIVES[CHANNEL]
    for name in (archive, f"{archive}.sha256"):
        if not (REPOSITORY / name).is_file():
            missing.append(name)
    assert not missing, f"Missing required files: {missing}"


def validate_manifest_and_copy() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8-sig"))
    assert manifest["channel"] == CHANNEL
    assert manifest["provider"] == "Yanbor LLC"
    assert manifest["providerDescription"] == "provider of the DataAI product"
    assert manifest["packageVersion"] == VERSION
    assert manifest["packageStatus"] == "evaluation-development"
    assert manifest["submissionReady"] is False
    assert manifest["runtime"] == {"java": "17", "spark": "3.5.0", "scalaBinary": "2.12"}
    assert all(value is False for value in manifest["dataHandling"].values())
    assert len(manifest["releaseGates"]) >= 5

    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    listing = (ROOT / "listing" / f"{CHANNEL.upper()}_LISTING.md").read_text(encoding="utf-8-sig")
    assert STATEMENT in readme
    assert STATEMENT in listing
    assert "not submission-ready" in readme
    assert VERSION in readme


def validate_channel_assets() -> None:
    if CHANNEL == "Maven":
        blocked = (ROOT / "central" / "MAVEN_CENTRAL_UPLOAD_BLOCKED.txt").read_text(encoding="utf-8-sig")
        assert "UPLOAD IS BLOCKED" in blocked
        assert "SNAPSHOT" in blocked
        assert "PGP" in blocked
        plugin = (ROOT / "central" / "central-publishing-plugin.xml").read_text(encoding="utf-8-sig")
        assert "central-publishing-maven-plugin" in plugin
        assert "<autoPublish>false</autoPublish>" in plugin
        for module in MODULES:
            base = ROOT / "repository-layout" / "com" / "dataai" / module / VERSION
            assert (base / f"{module}-{VERSION}.pom").is_file()
            for classifier in ("", "-sources", "-javadoc"):
                assert (base / f"{module}-{VERSION}{classifier}.jar").is_file()
        parent = ROOT / "repository-layout" / "com" / "dataai" / "dataai-etl-spark-parent" / VERSION
        assert (parent / f"dataai-etl-spark-parent-{VERSION}.pom").is_file()
        return

    dockerfile = (ROOT / "container" / "Dockerfile").read_text(encoding="utf-8-sig")
    assert "COPY lib/*.jar /opt/dataai/lib/" in dockerfile
    assert "org.opencontainers.image.vendor=\"Yanbor LLC\"" in dockerfile
    assert "ENTRYPOINT" not in dockerfile
    if CHANNEL == "AWS":
        assert "ARG BASE_IMAGE" in dockerfile
        assert "USER hadoop:hadoop" in dockerfile
        assert "/usr/lib/spark/jars" in dockerfile
    elif CHANNEL == "Microsoft":
        submission = (ROOT / "MARKETPLACE_SUBMISSION.md").read_text(encoding="utf-8-sig")
        assert "CNAB" in submission
        assert "single containers are unsupported" in submission
    elif CHANNEL == "Google":
        assert "com.googleapis.cloudmarketplace.product.service.name" in dockerfile
        assert "<SERVICE_NAME>" in dockerfile
    elif CHANNEL == "Oracle":
        assert "Oracle Cloud Marketplace" in (ROOT / "README.md").read_text(encoding="utf-8-sig")


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

    if CHANNEL == "Maven":
        for module in MODULES:
            for classifier in ("-sources", "-javadoc"):
                path = ROOT / "lib" / f"{module}-{VERSION}{classifier}.jar"
                with zipfile.ZipFile(path) as archive:
                    assert archive.testzip() is None, f"Corrupt classified JAR: {path.name}"


def validate_images() -> None:
    expected = {
        f"assets/dataai-{CHANNEL.lower()}-icon.png": (512, 512),
        f"assets/dataai-{CHANNEL.lower()}-icon-130.png": (130, 130),
        f"screenshots/{CHANNEL.lower()}-pipeline.png": (1600, 900),
        f"screenshots/{CHANNEL.lower()}-functions.png": (1600, 900),
    }
    for name, size in expected.items():
        with Image.open(ROOT / name) as image:
            assert image.size == size, f"Unexpected image size for {name}: {image.size}"


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
        f"distribution/DataAI_ETL_{CHANNEL}_Evaluation.zip",
    }
    assert required <= entries.keys(), f"Missing checksum entries: {sorted(required - entries.keys())}"
    evaluation = validate_checksum_file(ROOT / "distribution" / "EVALUATION_CHECKSUMS.sha256", ROOT)
    assert f"lib/dataai-spark-core-{VERSION}.jar" in evaluation

    archive = ARCHIVES[CHANNEL]
    digest, name = (REPOSITORY / f"{archive}.sha256").read_text(encoding="utf-8-sig").strip().split("  ", 1)
    assert name == archive
    assert hashlib.sha256((REPOSITORY / archive).read_bytes()).hexdigest() == digest


def validate_zip(path: Path, prefix: str, required: set[str]) -> None:
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f"Corrupt archive: {path.name}"
        names = set(archive.namelist())
    expected = {f"{prefix}/{name}" for name in required}
    assert expected <= names, f"{path.name} missing entries: {sorted(expected - names)}"


def validate_archives() -> None:
    validate_zip(
        ROOT / "distribution" / f"DataAI_ETL_{CHANNEL}_Evaluation.zip",
        f"DataAI_ETL_{CHANNEL}_Evaluation",
        {
            "README.md",
            "LICENSE.md",
            "CHECKSUMS.sha256",
            "docs/FUNCTION_CATALOG.md",
            f"lib/dataai-spark-functions-{VERSION}.jar",
        },
    )
    validate_zip(
        REPOSITORY / ARCHIVES[CHANNEL],
        CHANNEL,
        {
            "README.md",
            "MARKETPLACE_SUBMISSION.md",
            "PROVIDER_CHECKLIST.md",
            "LICENSE.md",
            "CHECKSUMS.sha256",
            f"listing/{CHANNEL.upper()}_LISTING.md",
            f"distribution/DataAI_ETL_{CHANNEL}_Evaluation.zip",
        },
    )


def validate_text() -> None:
    forbidden = {
        "Databricks token": re.compile(r"\bdapi[0-9a-zA-Z]{20,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or (path.suffix.lower() not in TEXT_EXTENSIONS and path.name != "Dockerfile"):
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        assert b"\n" not in raw.replace(b"\r\n", b""), f"Non-CRLF line ending: {path}"
        for label, pattern in forbidden.items():
            assert not pattern.search(text), f"Possible {label} in {path}"


def main() -> None:
    require_files()
    validate_manifest_and_copy()
    validate_channel_assets()
    validate_jars()
    validate_images()
    validate_archives()
    validate_checksums()
    validate_text()
    print(f"DataAI {CHANNEL} marketplace review package validation passed.")
    print("Package remains blocked from publication until manifest release gates are completed and authorized.")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        raise
