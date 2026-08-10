#!/usr/bin/env python3
"""Offline structural validation for the DataAI ETL Tableau bundle."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
LOCAL_HYPER = ROOT.parent / ".tools" / "tableauhyper"
if LOCAL_HYPER.is_dir():
    sys.path.insert(0, str(LOCAL_HYPER))

REQUIRED_FILES = [
    "pom.xml",
    "README.md",
    "LICENSE.md",
    "COMMERCIAL_LICENSE_TEMPLATE.md",
    "THIRD_PARTY_NOTICES.md",
    "manifest.json",
    "CHECKSUMS.sha256",
    "accelerator/DataAI_ETL_Accelerator.twb",
    "accelerator/DataAI_ETL_Accelerator.twbx",
    "assets/dataai-tableau-icon.svg",
    "assets/dataai-tableau-icon.png",
    "mapping/TABLEAU_OUTPUT_SCHEMA.md",
    "sample-data/dataai_dashboard_metrics.csv",
    "sample-data/dataai_quality_findings.csv",
    "sample-data/dataai_field_profiles.csv",
    "sample-data/dataai_kpis.csv",
    "sample-data/dataai_tableau_sample.hyper",
    "screenshots/executive-summary.png",
    "screenshots/data-quality.png",
    "screenshots/analytics.png",
]

DASHBOARD_HEADERS = [
    "run_id",
    "completed_at",
    "status",
    "rows_read",
    "rows_accepted",
    "rows_rejected",
    "quality_score",
    "critical_findings",
    "error_findings",
    "warning_findings",
    "info_findings",
    "fields_profiled",
    "total_null_values",
]

TEXT_SUFFIXES = {".csv", ".java", ".json", ".md", ".py", ".sql", ".svg", ".twb", ".xml"}


def require_files() -> None:
    missing = [relative for relative in REQUIRED_FILES if not (ROOT / relative).is_file()]
    if missing:
        raise AssertionError("Missing required files: " + ", ".join(missing))


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "DataAI ETL for Tableau"
    assert manifest["dataHandling"] == {
        "hostedService": False,
        "requiredNetworkCalls": False,
        "telemetry": False,
        "automaticWrites": False,
    }


def validate_csv() -> None:
    dashboard = ROOT / "sample-data" / "dataai_dashboard_metrics.csv"
    with dashboard.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == DASHBOARD_HEADERS
        rows = list(reader)
    assert len(rows) == 12
    assert all(row["status"] == "SUCCEEDED" for row in rows)
    assert all(0.0 <= float(row["quality_score"]) <= 100.0 for row in rows)
    assert all(int(row["rows_read"]) == int(row["rows_accepted"]) + int(row["rows_rejected"]) for row in rows)

    expected = {
        "dataai_quality_findings.csv": "record_key",
        "dataai_field_profiles.csv": "field_name",
        "dataai_kpis.csv": "metric_name",
    }
    for name, required_column in expected.items():
        with (ROOT / "sample-data" / name).open("r", encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert rows and required_column in rows[0]
        assert all(row["run_id"].startswith("RUN-") for row in rows)


def validate_workbook() -> None:
    twb = ROOT / "accelerator" / "DataAI_ETL_Accelerator.twb"
    root = ElementTree.parse(twb).getroot()
    assert root.tag == "workbook"
    worksheet_names = {element.attrib["name"] for element in root.findall("./worksheets/worksheet")}
    assert {
        "Quality Score Trend",
        "Rows Accepted",
        "Rows Rejected",
        "Critical Findings",
        "Error Findings",
        "Null Values",
    }.issubset(worksheet_names)
    assert root.find("./dashboards/dashboard[@name='DataAI Executive Summary']") is not None
    workbook_text = twb.read_text(encoding="utf-8")
    for field in DASHBOARD_HEADERS:
        assert f"[{field}]" in workbook_text

    package = ROOT / "accelerator" / "DataAI_ETL_Accelerator.twbx"
    with zipfile.ZipFile(package, "r") as archive:
        names = set(archive.namelist())
        assert "DataAI_ETL_Accelerator.twb" in names
        assert "Data/dataai_dashboard_metrics.csv" in names
        assert "Data/Extracts/dataai_tableau_sample.hyper" in names
        for name in names:
            path = Path(name)
            assert not path.is_absolute()
            assert ".." not in path.parts
        packaged_xml = archive.read("DataAI_ETL_Accelerator.twb")
        ElementTree.fromstring(packaged_xml)


def validate_hyper() -> None:
    try:
        from tableauhyperapi import Connection, HyperProcess, Telemetry
    except ImportError as exc:
        raise AssertionError("tableauhyperapi is required to validate the Hyper extract") from exc

    path = ROOT / "sample-data" / "dataai_tableau_sample.hyper"
    with HyperProcess(
        Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
        parameters={"log_config": ""},
    ) as process:
        with Connection(endpoint=process.endpoint, database=path) as connection:
            count = connection.execute_scalar_query('SELECT COUNT(*) FROM "Extract"."Extract"')
            assert count == 12
            schemas = {str(value).strip('"') for value in connection.catalog.get_schema_names()}
            assert "Extract" in schemas and "DataAI" in schemas
            dataai_tables = {str(value).split(".")[-1].strip('"') for value in connection.catalog.get_table_names("DataAI")}
            assert {"DashboardMetrics", "QualityFindings", "FieldProfiles", "Kpis"}.issubset(dataai_tables)


def validate_images() -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise AssertionError("Pillow is required to validate PNG assets") from exc

    expected_sizes = {
        "assets/dataai-tableau-icon.png": (512, 512),
        "screenshots/executive-summary.png": (1440, 900),
        "screenshots/data-quality.png": (1440, 900),
        "screenshots/analytics.png": (1440, 900),
    }
    for relative, expected_size in expected_sizes.items():
        with Image.open(ROOT / relative) as image:
            image.verify()
        with Image.open(ROOT / relative) as image:
            assert image.size == expected_size


def validate_line_endings() -> None:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or "target" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        data = path.read_bytes()
        without_crlf = data.replace(b"\r\n", b"")
        if b"\n" in without_crlf or b"\r" in without_crlf:
            failures.append(path.relative_to(ROOT).as_posix())
    if failures:
        raise AssertionError("Non-CRLF text files: " + ", ".join(failures))


def validate_checksums() -> None:
    failures = []
    lines = (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()
    assert lines
    for line in lines:
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file():
            failures.append(relative + " (missing)")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(relative + " (checksum mismatch)")
    if failures:
        raise AssertionError("Checksum failures: " + ", ".join(failures))


def main() -> None:
    checks = [
        ("required files", require_files),
        ("manifest", validate_manifest),
        ("sample data", validate_csv),
        ("workbook package", validate_workbook),
        ("Hyper extract", validate_hyper),
        ("images", validate_images),
        ("CRLF line endings", validate_line_endings),
        ("checksums", validate_checksums),
    ]
    for label, check in checks:
        check()
        print(f"PASS: {label}")
    print("DataAI ETL Tableau package passed offline structural validation.")
    print("Tableau Desktop rendering/interaction validation remains a publication gate.")


if __name__ == "__main__":
    main()
