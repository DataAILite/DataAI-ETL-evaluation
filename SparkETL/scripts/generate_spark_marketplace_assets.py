#!/usr/bin/env python3
"""Generate the DataAI Spark marketplace and evaluation packages offline."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

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
TEXT_EXTENSIONS = {
    ".csv", ".java", ".json", ".md", ".properties", ".py", ".sql",
    ".svg", ".txt", ".xml",
}


def write_text_crlf(path: Path, value: str) -> None:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")
    for name in names:
        candidate = Path("C:/Windows/Fonts") / name
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Required source file is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def copy_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Required source directory is missing: {source}")
    shutil.copytree(source, destination, dirs_exist_ok=True)


def copy_distribution_inputs() -> None:
    for name in ("LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md"):
        copy_file(REPOSITORY / name, ROOT / name)

    copy_file(REPOSITORY / "docs" / "INSTALLATION_AND_USAGE.md", ROOT / "docs" / "INSTALLATION_AND_USAGE.md")
    copy_file(REPOSITORY / "docs" / "FUNCTION_CATALOG.md", ROOT / "docs" / "FUNCTION_CATALOG.md")
    copy_tree(REPOSITORY / "examples" / "oracle-aidp", ROOT / "examples" / "oracle-aidp")

    source_root = ROOT / "source" / "spark"
    copy_file(SPARK / "pom.xml", source_root / "pom.xml")
    copy_file(SPARK / "README.md", source_root / "README.md")
    copy_file(SPARK / "pom.xml", ROOT / "poms" / "dataai-etl-spark-parent.pom")
    for module in MODULES + ("dataai-spark-testkit",):
        module_root = SPARK / module
        copy_file(module_root / "pom.xml", source_root / module / "pom.xml")
        copy_file(module_root / "pom.xml", ROOT / "poms" / f"{module}.pom")
        if (module_root / "src").is_dir():
            copy_tree(module_root / "src", source_root / module / "src")

    for module in MODULES:
        target = SPARK / module / "target"
        expected = (
            target / f"{module}-{VERSION}.jar",
            target / f"{module}-{VERSION}-sources.jar",
            target / f"{module}-{VERSION}-javadoc.jar",
        )
        for artifact in expected:
            copy_file(artifact, ROOT / "lib" / artifact.name)


def create_icon() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="1" stop-color="#7c2d12"/></linearGradient></defs>
  <rect width="512" height="512" rx="96" fill="url(#g)"/>
  <path d="M98 326L180 188L258 286L330 142L414 326" fill="none" stroke="#fb923c" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="98" cy="326" r="20" fill="#fff"/><circle cx="180" cy="188" r="20" fill="#fff"/><circle cx="258" cy="286" r="20" fill="#fff"/><circle cx="330" cy="142" r="20" fill="#fff"/><circle cx="414" cy="326" r="20" fill="#fff"/>
  <text x="256" y="418" fill="#fff" font-family="Segoe UI,Arial" font-size="52" font-weight="700" text-anchor="middle">DataAI Spark</text>
</svg>"""
    write_text_crlf(assets / "dataai-spark-icon.svg", svg)

    image = Image.new("RGB", (512, 512), "#111827")
    draw = ImageDraw.Draw(image)
    for y in range(512):
        ratio = y / 511
        draw.line((0, y, 512, y), fill=(int(17 + 107 * ratio), int(24 + 21 * ratio), int(39 - 21 * ratio)))
    points = [(98, 326), (180, 188), (258, 286), (330, 142), (414, 326)]
    draw.line(points, fill="#fb923c", width=28, joint="curve")
    for x, y in points:
        draw.ellipse((x - 20, y - 20, x + 20, y + 20), fill="white")
    label = "DataAI Spark"
    label_font = font(52, True)
    bounds = draw.textbbox((0, 0), label, font=label_font)
    draw.text(((512 - bounds[2] + bounds[0]) / 2, 388), label, fill="white", font=label_font)
    image.save(assets / "dataai-spark-icon.png", optimize=True)


def canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1440, 900), "#f5f7fb")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1440, 118), fill="#111827")
    draw.text((54, 25), title, fill="white", font=font(39, True))
    draw.text((56, 78), subtitle, fill="#fdba74", font=font(20))
    draw.rounded_rectangle((1180, 31, 1384, 87), radius=16, fill="#c2410c")
    draw.text((1204, 48), "FICTIONAL DATA", fill="white", font=font(18, True))
    return image, draw


def create_screenshots() -> None:
    screenshots = ROOT / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)

    image, draw = canvas("DataAI ETL Spark Libraries", "Customer-controlled execution • embedded Java SDK • no hosted DataAI service")
    stages = (
        (58, "Customer sources", "Catalogs, files, JDBC"),
        (346, "DataAI quality", "Normalize and validate"),
        (634, "DataAI functions", "Analytics and models"),
        (922, "Governed results", "Clean, findings, profiles"),
        (1210, "Customer targets", "Explicit writes"),
    )
    for index, (x, title, detail) in enumerate(stages):
        width = 228 if index < 4 else 174
        draw.rounded_rectangle((x, 220, x + width, 420), radius=20, fill="white", outline="#cbd5e1", width=2)
        draw.ellipse((x + 18, 244, x + 72, 298), fill="#c2410c")
        draw.text((x + 45, 270), str(index + 1), anchor="mm", fill="white", font=font(23, True))
        draw.text((x + 18, 324), title, fill="#111827", font=font(21, True))
        draw.text((x + 18, 362), detail, fill="#52616f", font=font(16))
        if index < len(stages) - 1:
            draw.line((x + width, 320, stages[index + 1][0] - 12, 320), fill="#ea580c", width=5)

    cards = (("Rows evaluated", "25,000"), ("Accepted", "24,180"), ("Rejected", "820"), ("Quality score", "96.7%"))
    for index, (title, value) in enumerate(cards):
        x = 58 + index * 334
        draw.rounded_rectangle((x, 510, x + 304, 672), radius=18, fill="white", outline="#dbe5ef", width=2)
        draw.rectangle((x, 510, x + 8, 672), fill="#f97316")
        draw.text((x + 28, 540), title, fill="#52616f", font=font(21))
        draw.text((x + 28, 590), value, fill="#111827", font=font(42, True))
    draw.rounded_rectangle((58, 730, 1384, 830), radius=18, fill="#fff7ed", outline="#fed7aa", width=2)
    draw.text((84, 757), "Credentials, source data, destinations, scheduling, save modes and retention remain under customer control.", fill="#7c2d12", font=font(22, True))
    draw.text((84, 794), "Design preview for marketplace review — not a live customer environment", fill="#52616f", font=font(17))
    image.save(screenshots / "spark-pipeline.png", optimize=True)

    image, draw = canvas("Complete DataAI Function Library", "One Spark dependency • reusable DataFrames • matrix convergence metadata retained")
    families = (
        ("ETL & quality", "Normalization • rules • profiles • routing", "#ea580c"),
        ("Analytics", "Statistics • pivot • regression • time series", "#2563eb"),
        ("Detection", "Outliers • anomalies • drift • alerts", "#7c3aed"),
        ("Business", "Pareto • cohorts • funnels • KPIs", "#0f766e"),
        ("Market", "Demand • pricing • churn • inventory • profit", "#be123c"),
        ("Geographic", "Map readiness • classification • diagnostics", "#0369a1"),
        ("Matrix", "Cross-tabs • iterative balancing • convergence", "#b45309"),
        ("Insights", "Dictionary • charts • local narratives", "#4d7c0f"),
    )
    for index, (title, detail, accent) in enumerate(families):
        row, column = divmod(index, 2)
        x, y = 58 + column * 680, 154 + row * 164
        draw.rounded_rectangle((x, y, x + 646, y + 132), radius=18, fill="white", outline="#dbe5ef", width=2)
        draw.rectangle((x, y, x + 10, y + 132), fill=accent)
        draw.text((x + 32, y + 24), title, fill="#111827", font=font(25, True))
        draw.text((x + 32, y + 72), detail, fill="#52616f", font=font(19))
    draw.text((58, 830), "All values and examples shown are fictional. Function availability depends on the licensed artifact version.", fill="#52616f", font=font(17))
    image.save(screenshots / "spark-functions.png", optimize=True)


def normalize_text_files() -> None:
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS and path.name != "CHECKSUMS.sha256":
            write_text_crlf(path, path.read_text(encoding="utf-8-sig"))


def add_tree(archive: zipfile.ZipFile, base: Path, prefix: str, excluded: set[str] | None = None) -> None:
    exclusions = excluded or set()
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.name in exclusions or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(base).as_posix()
        archive.write(path, f"{prefix}/{relative}" if prefix else relative)


def create_evaluation_zip() -> None:
    package = ROOT / "distribution" / "DataAI_ETL_Spark_Evaluation.zip"
    package.parent.mkdir(parents=True, exist_ok=True)
    prefix = "DataAI_ETL_Spark_Evaluation"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ("README.md", "LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md", "THIRD_PARTY_NOTICES.md", "manifest.json"):
            archive.write(ROOT / name, f"{prefix}/{name}")
        for directory in ("lib", "poms", "docs", "examples", "source"):
            add_tree(archive, ROOT / directory, f"{prefix}/{directory}")


def checksum_candidates() -> list[Path]:
    excluded = {"CHECKSUMS.sha256", "SparkETL.zip", "SparkETL.zip.sha256"}
    return sorted(
        (path for path in ROOT.rglob("*") if path.is_file() and path.name not in excluded and "__pycache__" not in path.parts),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def create_checksums() -> None:
    lines = []
    for path in checksum_candidates():
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT).as_posix()}")
    write_text_crlf(ROOT / "CHECKSUMS.sha256", "\n".join(lines))


def create_marketplace_zip() -> None:
    package = REPOSITORY / "SparkETL.zip"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        add_tree(archive, ROOT, "SparkETL", {"SparkETL.zip", "SparkETL.zip.sha256"})


def create_marketplace_zip_checksum() -> None:
    package = REPOSITORY / "SparkETL.zip"
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    write_text_crlf(REPOSITORY / "SparkETL.zip.sha256", f"{digest}  SparkETL.zip")


def main() -> None:
    copy_distribution_inputs()
    create_icon()
    create_screenshots()
    normalize_text_files()
    create_evaluation_zip()
    create_checksums()
    create_marketplace_zip()
    create_marketplace_zip_checksum()
    print("Generated Spark marketplace media, artifacts, checksums, evaluation ZIP, and SparkETL.zip.")


if __name__ == "__main__":
    main()
