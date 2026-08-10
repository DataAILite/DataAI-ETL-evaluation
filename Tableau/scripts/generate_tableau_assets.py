#!/usr/bin/env python3
"""Generate fictional Tableau evaluation assets without network calls."""

from __future__ import annotations

import csv
import hashlib
import sys
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_HYPER = ROOT.parent / ".tools" / "tableauhyper"
if LOCAL_HYPER.is_dir():
    sys.path.insert(0, str(LOCAL_HYPER))


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / "sample-data" / name).open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_text_crlf(path: Path, value: str) -> None:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def create_hyper_extract() -> None:
    try:
        from tableauhyperapi import (
            Connection,
            CreateMode,
            HyperProcess,
            Inserter,
            SqlType,
            TableDefinition,
            TableName,
            Telemetry,
            Timestamp,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Install tableauhyperapi or place it in ../.tools/tableauhyper before generation."
        ) from exc

    destination = ROOT / "sample-data" / "dataai_tableau_sample.hyper"
    dashboard_columns = [
        ("run_id", SqlType.text(), str),
        ("completed_at", SqlType.timestamp(), lambda value: Timestamp.from_datetime(datetime.fromisoformat(value))),
        ("status", SqlType.text(), str),
        ("rows_read", SqlType.big_int(), int),
        ("rows_accepted", SqlType.big_int(), int),
        ("rows_rejected", SqlType.big_int(), int),
        ("quality_score", SqlType.double(), float),
        ("critical_findings", SqlType.big_int(), int),
        ("error_findings", SqlType.big_int(), int),
        ("warning_findings", SqlType.big_int(), int),
        ("info_findings", SqlType.big_int(), int),
        ("fields_profiled", SqlType.big_int(), int),
        ("total_null_values", SqlType.big_int(), int),
    ]
    finding_columns = [
        ("run_id", SqlType.text(), str),
        ("record_key", SqlType.text(), str),
        ("rule_id", SqlType.text(), str),
        ("field_name", SqlType.text(), str),
        ("severity", SqlType.text(), str),
        ("finding_code", SqlType.text(), str),
        ("message", SqlType.text(), str),
        ("original_value", SqlType.text(), str),
        ("normalized_value", SqlType.text(), str),
    ]
    profile_columns = [
        ("run_id", SqlType.text(), str),
        ("field_name", SqlType.text(), str),
        ("source_type", SqlType.text(), str),
        ("record_count", SqlType.big_int(), int),
        ("null_count", SqlType.big_int(), int),
        ("distinct_count", SqlType.big_int(), int),
        ("minimum_value", SqlType.text(), str),
        ("maximum_value", SqlType.text(), str),
        ("mean_value", SqlType.double(), float),
        ("standard_deviation", SqlType.double(), float),
    ]
    kpi_columns = [
        ("run_id", SqlType.text(), str),
        ("metric_name", SqlType.text(), str),
        ("metric_value", SqlType.double(), float),
        ("target_value", SqlType.double(), float),
        ("status", SqlType.text(), str),
    ]

    tables = [
        ("Extract", "Extract", "dataai_dashboard_metrics.csv", dashboard_columns),
        ("DataAI", "DashboardMetrics", "dataai_dashboard_metrics.csv", dashboard_columns),
        ("DataAI", "QualityFindings", "dataai_quality_findings.csv", finding_columns),
        ("DataAI", "FieldProfiles", "dataai_field_profiles.csv", profile_columns),
        ("DataAI", "Kpis", "dataai_kpis.csv", kpi_columns),
    ]

    with HyperProcess(
        Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
        parameters={"log_config": ""},
    ) as process:
        with Connection(
            endpoint=process.endpoint,
            database=destination,
            create_mode=CreateMode.CREATE_AND_REPLACE,
        ) as connection:
            connection.catalog.create_schema("Extract")
            connection.catalog.create_schema("DataAI")
            for schema_name, table_name, csv_name, columns in tables:
                definition = TableDefinition(
                    TableName(schema_name, table_name),
                    [TableDefinition.Column(name, sql_type) for name, sql_type, _ in columns],
                )
                connection.catalog.create_table(definition)
                converted_rows = []
                for source in read_csv(csv_name):
                    converted = []
                    for name, _, converter in columns:
                        raw = source[name]
                        converted.append(None if raw == "" else converter(raw))
                    converted_rows.append(converted)
                with Inserter(connection, definition) as inserter:
                    inserter.add_rows(converted_rows)
                    inserter.execute()


def workbook_xml() -> str:
    datasource = "dataai_dashboard_metrics"
    dependency_columns = "\n".join(
        [
            "          <column datatype='string' name='[run_id]' role='dimension' type='nominal' />",
            "          <column datatype='datetime' name='[completed_at]' role='dimension' type='ordinal' />",
            "          <column datatype='string' name='[status]' role='dimension' type='nominal' />",
            "          <column datatype='integer' name='[rows_read]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[rows_accepted]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[rows_rejected]' role='measure' type='quantitative' />",
            "          <column datatype='real' name='[quality_score]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[critical_findings]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[error_findings]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[warning_findings]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[info_findings]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[fields_profiled]' role='measure' type='quantitative' />",
            "          <column datatype='integer' name='[total_null_values]' role='measure' type='quantitative' />",
        ]
    )

    def worksheet(name: str, measure: str, aggregation: str, mark: str = "Automatic") -> str:
        instance = f"[{aggregation.lower()}:{measure}:qk]"
        return f"""
    <worksheet name='{name}'>
      <table>
        <view>
          <datasources><datasource caption='DataAI Dashboard Metrics' name='{datasource}' /></datasources>
          <datasource-dependencies datasource='{datasource}'>
{dependency_columns}
            <column-instance column='[completed_at]' derivation='Exact' name='[attr:completed_at:qk]' pivot='key' type='ordinal' />
            <column-instance column='[{measure}]' derivation='{aggregation}' name='{instance}' pivot='key' type='quantitative' />
          </datasource-dependencies>
          <aggregation value='true' />
        </view>
        <style><style-rule element='worksheet'><format attr='display-field-labels' value='false' /></style-rule></style>
        <panes><pane><view><breakdown value='auto' /></view><mark class='{mark}' /></pane></panes>
        <rows>{datasource}.{instance}</rows>
        <cols>{datasource}.[attr:completed_at:qk]</cols>
      </table>
    </worksheet>"""

    worksheets = "".join(
        [
            worksheet("Quality Score Trend", "quality_score", "Avg", "Line"),
            worksheet("Rows Accepted", "rows_accepted", "Sum", "Bar"),
            worksheet("Rows Rejected", "rows_rejected", "Sum", "Bar"),
            worksheet("Critical Findings", "critical_findings", "Sum", "Bar"),
            worksheet("Error Findings", "error_findings", "Sum", "Bar"),
            worksheet("Null Values", "total_null_values", "Sum", "Line"),
        ]
    )

    return textwrap.dedent(
        f"""\
        <?xml version='1.0' encoding='utf-8' ?>
        <workbook original-version='18.1' source-build='2024.2.0 (20242.24.0715.1602)' source-platform='win' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
          <document-format-change-manifest>
            <AccessibleZoneTabOrder />
            <SheetIdentifierTracking />
          </document-format-change-manifest>
          <preferences>
            <preference name='ui.encoding.shelf.height' value='24' />
          </preferences>
          <datasources>
            <datasource caption='DataAI Dashboard Metrics' inline='true' name='{datasource}' version='18.1'>
              <aliases enabled='yes' />
              <connection access_mode='readonly' authentication='auth-none' class='textscan' directory='Data' filename='dataai_dashboard_metrics.csv' password='' server=''>
                <relation name='dataai_dashboard_metrics.csv' table='[dataai_dashboard_metrics#csv]' type='table' />
              </connection>
              <column datatype='string' name='[run_id]' role='dimension' type='nominal' />
              <column datatype='datetime' date-parse-format='yyyy-MM-ddTHH:mm:ss' name='[completed_at]' role='dimension' type='ordinal' />
              <column datatype='string' name='[status]' role='dimension' type='nominal' />
              <column datatype='integer' name='[rows_read]' role='measure' type='quantitative' />
              <column datatype='integer' name='[rows_accepted]' role='measure' type='quantitative' />
              <column datatype='integer' name='[rows_rejected]' role='measure' type='quantitative' />
              <column datatype='real' default-format='f2' name='[quality_score]' role='measure' type='quantitative' />
              <column datatype='integer' name='[critical_findings]' role='measure' type='quantitative' />
              <column datatype='integer' name='[error_findings]' role='measure' type='quantitative' />
              <column datatype='integer' name='[warning_findings]' role='measure' type='quantitative' />
              <column datatype='integer' name='[info_findings]' role='measure' type='quantitative' />
              <column datatype='integer' name='[fields_profiled]' role='measure' type='quantitative' />
              <column datatype='integer' name='[total_null_values]' role='measure' type='quantitative' />
            </datasource>
          </datasources>
          <worksheets>{worksheets}
          </worksheets>
          <dashboards>
            <dashboard enable-sort-zone-taborder='true' name='DataAI Executive Summary'>
              <style><style-rule element='dashboard'><format attr='background-color' value='#F4F7FB' /></style-rule></style>
              <size sizing-mode='automatic' />
              <zones>
                <zone h='100000' id='1' type-v2='layout-basic' w='100000' x='0' y='0'>
                  <zone h='50000' id='2' name='Quality Score Trend' w='66000' x='1000' y='2000' />
                  <zone h='24000' id='3' name='Rows Accepted' w='31000' x='68000' y='2000' />
                  <zone h='24000' id='4' name='Rows Rejected' w='31000' x='68000' y='27000' />
                  <zone h='45000' id='5' name='Critical Findings' w='32000' x='1000' y='53000' />
                  <zone h='45000' id='6' name='Error Findings' w='32000' x='34000' y='53000' />
                  <zone h='45000' id='7' name='Null Values' w='32000' x='67000' y='53000' />
                </zone>
              </zones>
            </dashboard>
          </dashboards>
          <windows>
            <window class='dashboard' name='DataAI Executive Summary'>
              <viewpoints>
                <viewpoint name='Quality Score Trend' />
                <viewpoint name='Rows Accepted' />
                <viewpoint name='Rows Rejected' />
                <viewpoint name='Critical Findings' />
                <viewpoint name='Error Findings' />
                <viewpoint name='Null Values' />
              </viewpoints>
            </window>
          </windows>
        </workbook>
        """
    ).lstrip()


def create_workbook() -> None:
    source = ROOT / "accelerator" / "DataAI_ETL_Accelerator.twb"
    package = ROOT / "accelerator" / "DataAI_ETL_Accelerator.twbx"
    write_text_crlf(source, workbook_xml())
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(source, source.name)
        archive.write(
            ROOT / "sample-data" / "dataai_dashboard_metrics.csv",
            "Data/dataai_dashboard_metrics.csv",
        )
        archive.write(
            ROOT / "sample-data" / "dataai_tableau_sample.hyper",
            "Data/Extracts/dataai_tableau_sample.hyper",
        )


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_header(draw, title: str, subtitle: str) -> None:
    draw.text((70, 46), "DataAI", font=load_font(28, True), fill="#55D6BE")
    draw.text((70, 92), title, font=load_font(38, True), fill="#F7FAFC")
    draw.text((70, 146), subtitle, font=load_font(18), fill="#A9B9CE")
    draw.rounded_rectangle((1185, 55, 1365, 105), radius=18, fill="#163A5F")
    draw.text((1220, 68), "FICTIONAL DATA", font=load_font(13, True), fill="#A8E6CF")


def draw_card(draw, box, label: str, value: str, note: str, accent: str) -> None:
    draw.rounded_rectangle(box, radius=18, fill="#132C46", outline="#274765", width=2)
    x1, y1, _, _ = box
    draw.rounded_rectangle((x1 + 18, y1 + 18, x1 + 28, y1 + 72), radius=5, fill=accent)
    draw.text((x1 + 46, y1 + 20), label, font=load_font(15, True), fill="#9FB3C8")
    draw.text((x1 + 46, y1 + 48), value, font=load_font(30, True), fill="#FFFFFF")
    draw.text((x1 + 46, y1 + 91), note, font=load_font(13), fill="#89A4BE")


def create_screenshots() -> None:
    from PIL import Image, ImageDraw

    rows = read_csv("dataai_dashboard_metrics.csv")
    latest = rows[-1]
    colors = {"green": "#55D6BE", "blue": "#5AA9E6", "orange": "#FFB35C", "red": "#FF6B6B"}

    image = Image.new("RGB", (1440, 900), "#0B1F33")
    draw = ImageDraw.Draw(image)
    draw_header(draw, "ETL Executive Summary", "Run health, throughput, and quality trend")
    cards = [
        ((70, 205, 380, 340), "QUALITY SCORE", f"{latest['quality_score']}%", "+6.07 pts in 12 weeks", colors["green"]),
        ((400, 205, 710, 340), "ROWS READ", f"{int(latest['rows_read']):,}", "Latest pipeline run", colors["blue"]),
        ((730, 205, 1040, 340), "ROWS ACCEPTED", f"{int(latest['rows_accepted']):,}", "97.53% acceptance", colors["green"]),
        ((1060, 205, 1370, 340), "ROWS REJECTED", f"{int(latest['rows_rejected']):,}", "2.47% routed for review", colors["orange"]),
    ]
    for card in cards:
        draw_card(draw, *card)
    draw.rounded_rectangle((70, 380, 920, 825), radius=20, fill="#102942", outline="#274765", width=2)
    draw.text((100, 410), "Quality score trend", font=load_font(20, True), fill="#FFFFFF")
    values = [float(row["quality_score"]) for row in rows]
    x0, y0, width, height = 120, 745, 750, 260
    points = []
    for index, value in enumerate(values):
        x = x0 + index * width / (len(values) - 1)
        y = y0 - (value - 90.0) / 8.0 * height
        points.append((x, y))
    for tick in [90, 92, 94, 96, 98]:
        y = y0 - (tick - 90) / 8 * height
        draw.line((x0, y, x0 + width, y), fill="#23405C", width=1)
        draw.text((82, y - 9), str(tick), font=load_font(12), fill="#8199B1")
    draw.line(points, fill=colors["green"], width=5, joint="curve")
    for point in points:
        draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill="#0B1F33", outline=colors["green"], width=3)
    draw.rounded_rectangle((950, 380, 1370, 825), radius=20, fill="#102942", outline="#274765", width=2)
    draw.text((980, 410), "Latest run status", font=load_font(20, True), fill="#FFFFFF")
    draw.text((980, 465), "SUCCEEDED", font=load_font(28, True), fill=colors["green"])
    metrics = [("Critical findings", "1", colors["red"]), ("Error findings", "34", colors["orange"]), ("Warning findings", "84", colors["blue"]), ("Fields profiled", "18", colors["green"]), ("Null values", "642", "#C4A7E7")]
    for index, (label, value, color) in enumerate(metrics):
        y = 535 + index * 52
        draw.ellipse((985, y + 5, 997, y + 17), fill=color)
        draw.text((1010, y), label, font=load_font(15), fill="#A9B9CE")
        draw.text((1310, y), value, font=load_font(16, True), fill="#FFFFFF", anchor="ra")
    image.save(ROOT / "screenshots" / "executive-summary.png")

    image = Image.new("RGB", (1440, 900), "#0B1F33")
    draw = ImageDraw.Draw(image)
    draw_header(draw, "Data Quality", "Finding severity and field completeness")
    severity = [("Critical", 1, colors["red"]), ("Error", 34, colors["orange"]), ("Warning", 84, colors["blue"]), ("Info", 12, colors["green"])]
    draw.rounded_rectangle((70, 205, 760, 820), radius=20, fill="#102942", outline="#274765", width=2)
    draw.text((105, 240), "Findings by severity", font=load_font(22, True), fill="#FFFFFF")
    for index, (label, value, color) in enumerate(severity):
        y = 330 + index * 105
        draw.text((110, y), label, font=load_font(17), fill="#B8C7D9")
        draw.rounded_rectangle((230, y, 690, y + 36), radius=12, fill="#1A3854")
        bar_width = max(12, value / 84 * 440)
        draw.rounded_rectangle((230, y, 230 + bar_width, y + 36), radius=12, fill=color)
        draw.text((710, y + 4), str(value), font=load_font(18, True), fill="#FFFFFF", anchor="ra")
    draw.rounded_rectangle((790, 205, 1370, 820), radius=20, fill="#102942", outline="#274765", width=2)
    draw.text((825, 240), "Fields requiring attention", font=load_font(22, True), fill="#FFFFFF")
    fields = [("email", 214, 102450), ("customer_id", 112, 102450), ("region", 97, 102450), ("order_date", 84, 102450), ("product_category", 82, 102450)]
    for index, (field, nulls, total) in enumerate(fields):
        y = 325 + index * 90
        pct = nulls / total * 100
        draw.text((830, y), field, font=load_font(17, True), fill="#DCE6F2")
        draw.text((1330, y), f"{nulls:,} nulls  |  {pct:.2f}%", font=load_font(14), fill="#9FB3C8", anchor="ra")
        draw.rounded_rectangle((830, y + 35, 1330, y + 49), radius=7, fill="#1A3854")
        draw.rounded_rectangle((830, y + 35, 830 + max(10, pct / 0.25 * 500), y + 49), radius=7, fill=colors["orange"])
    image.save(ROOT / "screenshots" / "data-quality.png")

    image = Image.new("RGB", (1440, 900), "#0B1F33")
    draw = ImageDraw.Draw(image)
    draw_header(draw, "Pipeline Analytics", "Accepted/rejected volume and missing-value improvement")
    draw.rounded_rectangle((70, 205, 895, 820), radius=20, fill="#102942", outline="#274765", width=2)
    draw.text((105, 240), "Weekly row disposition", font=load_font(22, True), fill="#FFFFFF")
    max_rows = max(int(row["rows_read"]) for row in rows)
    for index, row in enumerate(rows):
        x = 115 + index * 61
        accepted = int(row["rows_accepted"])
        rejected = int(row["rows_rejected"])
        total_h = int((accepted + rejected) / max_rows * 430)
        rejected_h = max(4, int(rejected / max_rows * 430))
        draw.rectangle((x, 755 - total_h, x + 34, 755 - rejected_h), fill=colors["green"])
        draw.rectangle((x, 755 - rejected_h, x + 34, 755), fill=colors["orange"])
        if index % 2 == 0:
            draw.text((x + 17, 770), row["completed_at"][5:10], font=load_font(11), fill="#8FA6BC", anchor="ma")
    draw.rectangle((110, 285, 125, 300), fill=colors["green"])
    draw.text((135, 282), "Accepted", font=load_font(13), fill="#A9B9CE")
    draw.rectangle((225, 285, 240, 300), fill=colors["orange"])
    draw.text((250, 282), "Rejected", font=load_font(13), fill="#A9B9CE")
    draw.rounded_rectangle((925, 205, 1370, 820), radius=20, fill="#102942", outline="#274765", width=2)
    draw.text((960, 240), "Null-value trend", font=load_font(22, True), fill="#FFFFFF")
    nulls = [int(row["total_null_values"]) for row in rows]
    points = []
    for index, value in enumerate(nulls):
        x = 970 + index * 32
        y = 690 - (value - min(nulls)) / (max(nulls) - min(nulls)) * 330
        points.append((x, y))
    draw.line(points, fill="#C4A7E7", width=5, joint="curve")
    for point in points:
        draw.ellipse((point[0] - 4, point[1] - 4, point[0] + 4, point[1] + 4), fill="#C4A7E7")
    draw.text((960, 725), f"{nulls[0]:,} → {nulls[-1]:,}", font=load_font(30, True), fill="#FFFFFF")
    draw.text((960, 770), "55.8% reduction in 12 weeks", font=load_font(15), fill=colors["green"])
    image.save(ROOT / "screenshots" / "analytics.png")


def create_icon() -> None:
    from PIL import Image, ImageDraw

    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#0B1F33"/>
  <path d="M116 346V166h66v180zm107 0V116h66v230zm107 0V214h66v132z" fill="#55D6BE"/>
  <path d="M100 382h312" stroke="#F7FAFC" stroke-width="20" stroke-linecap="round"/>
  <circle cx="149" cy="143" r="17" fill="#5AA9E6"/>
  <circle cx="256" cy="93" r="17" fill="#5AA9E6"/>
  <circle cx="363" cy="191" r="17" fill="#5AA9E6"/>
</svg>"""
    write_text_crlf(ROOT / "assets" / "dataai-tableau-icon.svg", svg)
    image = Image.new("RGB", (512, 512), "#0B1F33")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, 511, 511), radius=96, fill="#0B1F33")
    draw.rectangle((116, 166, 182, 346), fill="#55D6BE")
    draw.rectangle((223, 116, 289, 346), fill="#55D6BE")
    draw.rectangle((330, 214, 396, 346), fill="#55D6BE")
    draw.line((100, 382, 412, 382), fill="#F7FAFC", width=20)
    for x, y in [(149, 143), (256, 93), (363, 191)]:
        draw.ellipse((x - 17, y - 17, x + 17, y + 17), fill="#5AA9E6")
    image.save(ROOT / "assets" / "dataai-tableau-icon.png")


def copy_distribution_licenses() -> None:
    for name in ("LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md"):
        source = ROOT.parent / name
        if not source.is_file():
            raise RuntimeError(f"Required distribution license is missing: {source}")
        (ROOT / name).write_bytes(source.read_bytes())


def create_checksums() -> None:
    excluded_parts = {"target", "__pycache__"}
    candidates = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name != "CHECKSUMS.sha256"
        and not any(part in excluded_parts for part in path.parts)
        and path.suffix.lower() != ".log"
        and path.suffix != ".pyc"
    ]
    adapter_jar = ROOT / "target" / "dataai-spark-tableau-0.1.0-SNAPSHOT.jar"
    if adapter_jar.is_file():
        candidates.append(adapter_jar)
    lines = []
    for path in sorted(candidates, key=lambda value: value.relative_to(ROOT).as_posix().lower()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    write_text_crlf(ROOT / "CHECKSUMS.sha256", "\n".join(lines))


def main() -> None:
    create_hyper_extract()
    create_workbook()
    create_icon()
    create_screenshots()
    copy_distribution_licenses()
    create_checksums()
    print("Generated Tableau workbook, Hyper extract, images, and checksums.")


if __name__ == "__main__":
    main()
