#!/usr/bin/env python3
"""Generate the DataAI Databricks Marketplace package entirely offline."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
SPARK = REPOSITORY / "spark"
VERSION = "0.1.0-SNAPSHOT"
MODULES = (
    "dataai-spark-api",
    "dataai-spark-quality",
    "dataai-spark-core",
    "dataai-spark-functions",
    "dataai-spark-cli",
)
ZIP_DATE = (2026, 8, 7, 0, 0, 0)


def write_text_crlf(path: Path, value: str) -> None:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Required source file is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")
    for name in names:
        candidate = Path("C:/Windows/Fonts") / name
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def copy_distribution_files() -> None:
    copy_file(REPOSITORY / "LICENSE.md", ROOT / "LICENSE.md")
    copy_file(
        REPOSITORY / "COMMERCIAL_LICENSE_TEMPLATE.md",
        ROOT / "COMMERCIAL_LICENSE_TEMPLATE.md",
    )
    copy_file(REPOSITORY / "docs" / "FUNCTION_CATALOG.md", ROOT / "docs" / "FUNCTION_CATALOG.md")
    for module in MODULES:
        source = SPARK / module / "target" / f"{module}-{VERSION}.jar"
        copy_file(source, ROOT / "lib" / source.name)


def create_icon() -> None:
    image = Image.new("RGB", (512, 512), "#071426")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((46, 46, 466, 466), 70, fill="#102a43", outline="#35c5f0", width=7)
    colors = ("#35c5f0", "#52e0a7", "#ffcc66")
    for index, color in enumerate(colors):
        y = 150 + index * 64
        draw.polygon(((116, y), (256, y - 42), (396, y), (256, y + 42)), outline=color, width=10)
    draw.text((256, 65), "DataAI", font=font(52, True), fill="white", anchor="ma")
    draw.text((256, 407), "ETL", font=font(64, True), fill="white", anchor="ma")
    draw.text((256, 466), "DATABRICKS", font=font(21, True), fill="#b9d7ef", anchor="ma")
    image.save(ROOT / "assets" / "dataai-databricks-icon.png", optimize=True)

    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="70" fill="#071426"/>
  <rect x="46" y="46" width="420" height="420" rx="70" fill="#102a43" stroke="#35c5f0" stroke-width="7"/>
  <text x="256" y="105" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,Arial" font-size="52" font-weight="700">DataAI</text>
  <path d="M116 150 L256 108 L396 150 L256 192 Z" fill="none" stroke="#35c5f0" stroke-width="10"/>
  <path d="M116 214 L256 172 L396 214 L256 256 Z" fill="none" stroke="#52e0a7" stroke-width="10"/>
  <path d="M116 278 L256 236 L396 278 L256 320 Z" fill="none" stroke="#ffcc66" stroke-width="10"/>
  <text x="256" y="435" text-anchor="middle" fill="#ffffff" font-family="Segoe UI,Arial" font-size="64" font-weight="700">ETL</text>
  <text x="256" y="475" text-anchor="middle" fill="#b9d7ef" font-family="Segoe UI,Arial" font-size="21" font-weight="700">DATABRICKS</text>
</svg>"""
    write_text_crlf(ROOT / "assets" / "dataai-databricks-icon.svg", svg)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str) -> None:
    draw.rounded_rectangle(box, 24, fill="#102a43", outline="#264d6d", width=2)
    draw.text((box[0] + 28, box[1] + 22), title, font=font(24, True), fill="#d7e9f7")


def screenshot_canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1600, 900), "#071426")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1600, 96), fill="#0d2238")
    draw.text((55, 25), "DataAI ETL", font=font(34, True), fill="white")
    draw.text((1545, 32), "Customer-controlled Spark", font=font(20), fill="#b9d7ef", anchor="ra")
    draw.text((55, 125), title, font=font(42, True), fill="white")
    draw.text((55, 181), subtitle, font=font(24), fill="#b9d7ef")
    draw.text(
        (55, 866),
        "Design preview · fictional data · not a Databricks screenshot",
        font=font(18),
        fill="#7fa7c4",
    )
    return image, draw


def create_screenshots() -> None:
    image, draw = screenshot_canvas(
        "Quality pipeline evaluation",
        "Traceable findings, customer-selected persistence, no DataAI service",
    )
    metrics = (("Rows read", "12"), ("Accepted", "6"), ("Rejected", "6"), ("Quality score", "50.0"))
    for index, (label, value) in enumerate(metrics):
        left = 55 + index * 375
        panel(draw, (left, 235, left + 335, 365), label)
        draw.text((left + 28, 298), value, font=font(42, True), fill="#52e0a7")
    panel(draw, (55, 405, 1000, 825), "Findings by rule")
    findings = (
        ("customer-required", 1, "#ffcc66"),
        ("order-unique", 2, "#35c5f0"),
        ("amount-range", 1, "#ff7c8c"),
        ("order-date", 1, "#9d8cff"),
        ("status-values", 1, "#52e0a7"),
    )
    for index, (name, count, color) in enumerate(findings):
        y = 475 + index * 60
        draw.text((90, y), name, font=font(21), fill="#d7e9f7")
        draw.rounded_rectangle((340, y + 4, 340 + count * 185, y + 32), 10, fill=color)
        draw.text((735, y), str(count), font=font(21, True), fill="white")
    panel(draw, (1030, 405, 1545, 825), "Execution boundary")
    boundaries = (
        "Runs inside customer compute",
        "Unity Catalog governs files",
        "Outputs are DataFrames",
        "Writes default to disabled",
        "No required DataAI network call",
    )
    for index, value in enumerate(boundaries):
        y = 485 + index * 62
        draw.ellipse((1070, y, 1090, y + 20), fill="#52e0a7")
        draw.text((1110, y - 4), value, font=font(20), fill="#d7e9f7")
    image.save(ROOT / "screenshots" / "databricks-quality.png", optimize=True)

    image, draw = screenshot_canvas(
        "Matrix balancing",
        "Row and column controls with explicit convergence metadata",
    )
    panel(draw, (55, 235, 1010, 825), "Balanced region × channel cells")
    rows = ("North", "South", "East")
    columns = ("Retail", "Online")
    values = ((76.7, 63.3), (70.4, 59.6), (82.9, 67.1))
    draw.text((380, 300), columns[0], font=font(22, True), fill="#b9d7ef", anchor="mm")
    draw.text((700, 300), columns[1], font=font(22, True), fill="#b9d7ef", anchor="mm")
    for row_index, row in enumerate(rows):
        y = 365 + row_index * 135
        draw.text((120, y + 44), row, font=font(24, True), fill="white")
        for column_index in range(2):
            x = 260 + column_index * 320
            intensity = int(min(values[row_index][column_index] / 90.0, 1.0) * 115)
            color = (20, 85 + intensity, 120 + intensity)
            draw.rounded_rectangle((x, y, x + 245, y + 95), 18, fill=color)
            draw.text(
                (x + 122, y + 48),
                f"{values[row_index][column_index]:.1f}",
                font=font(30, True),
                fill="white",
                anchor="mm",
            )
    panel(draw, (1040, 235, 1545, 825), "Convergence")
    facts = (("Iterations", "6"), ("Maximum error", "< 0.0001"), ("Converged", "true"), ("Control total", "420.0"))
    for index, (label, value) in enumerate(facts):
        y = 320 + index * 110
        draw.text((1085, y), label, font=font(20), fill="#b9d7ef")
        draw.text((1085, y + 34), value, font=font(32, True), fill="#52e0a7")
    image.save(ROOT / "screenshots" / "databricks-matrix.png", optimize=True)


def zip_add(archive: zipfile.ZipFile, source: Path, destination: PurePosixPath) -> None:
    info = zipfile.ZipInfo(destination.as_posix(), date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, source.read_bytes())


def evaluation_files() -> list[Path]:
    selected = [
        ROOT / "README.md",
        ROOT / "LICENSE.md",
        ROOT / "COMMERCIAL_LICENSE_TEMPLATE.md",
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "manifest.json",
    ]
    for name in ("notebooks", "data", "lib", "docs", "configs"):
        selected.extend(path for path in (ROOT / name).rglob("*") if path.is_file())
    return sorted(selected, key=lambda path: path.relative_to(ROOT).as_posix())


def create_evaluation_zip() -> None:
    files = evaluation_files()
    checksum_lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}"
        for path in files
    ]
    evaluation_checksums = ROOT / "distribution" / "EVALUATION_CHECKSUMS.sha256"
    write_text_crlf(evaluation_checksums, "\n".join(checksum_lines))

    package = ROOT / "distribution" / "DataAI_ETL_Databricks_Evaluation.zip"
    prefix = PurePosixPath("DataAI_ETL_Databricks_Evaluation")
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            zip_add(archive, path, prefix / path.relative_to(ROOT).as_posix())
        zip_add(archive, evaluation_checksums, prefix / "CHECKSUMS.sha256")


def checksum_candidates() -> list[Path]:
    return sorted(
        (
            path for path in ROOT.rglob("*")
            if path.is_file()
            and path.name != "CHECKSUMS.sha256"
            and "__pycache__" not in path.parts
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def create_checksums() -> None:
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}"
        for path in checksum_candidates()
    ]
    write_text_crlf(ROOT / "CHECKSUMS.sha256", "\n".join(lines))


def create_submission_zip() -> None:
    package = REPOSITORY / "DataAIETLDatabricks.zip"
    if package.exists():
        package.unlink()
    files = sorted(
        (path for path in ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            zip_add(archive, path, PurePosixPath("Databricks") / path.relative_to(ROOT).as_posix())
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    write_text_crlf(REPOSITORY / "DataAIETLDatabricks.zip.sha256", f"{digest}  DataAIETLDatabricks.zip")


def main() -> None:
    copy_distribution_files()
    create_icon()
    create_screenshots()
    create_evaluation_zip()
    create_checksums()
    create_submission_zip()
    print("Generated DataAI Databricks assets, evaluation package, checksums, and provider ZIP.")


if __name__ == "__main__":
    main()
