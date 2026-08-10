#!/usr/bin/env python3
"""Generate deterministic IRIS marketplace and controlled-evaluation assets."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
VERSION = "0.1.0-SNAPSHOT"
JAR_NAME = f"dataai-spark-iris-{VERSION}.jar"
TEXT_EXTENSIONS = {".cls", ".csv", ".java", ".json", ".md", ".py", ".sql", ".svg", ".xml"}


def write_text_crlf(path: Path, value: str) -> None:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        candidate = Path("C:/Windows/Fonts") / name
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def create_icon() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#172554"/><stop offset="1" stop-color="#0f766e"/></linearGradient></defs>
  <rect width="512" height="512" rx="96" fill="url(#g)"/>
  <path d="M102 340L190 172L256 288L322 132L410 340" fill="none" stroke="#5eead4" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="102" cy="340" r="22" fill="#ffffff"/><circle cx="190" cy="172" r="22" fill="#ffffff"/><circle cx="256" cy="288" r="22" fill="#ffffff"/><circle cx="322" cy="132" r="22" fill="#ffffff"/><circle cx="410" cy="340" r="22" fill="#ffffff"/>
  <text x="256" y="422" fill="#ffffff" font-family="Segoe UI,Arial" font-size="54" font-weight="700" text-anchor="middle">DataAI IRIS</text>
</svg>"""
    write_text_crlf(assets / "dataai-iris-icon.svg", svg)

    image = Image.new("RGB", (512, 512), "#172554")
    draw = ImageDraw.Draw(image)
    for y in range(512):
        ratio = y / 511
        color = (int(23 - 8 * ratio), int(37 + 81 * ratio), int(84 + 26 * ratio))
        draw.line((0, y, 512, y), fill=color)
    points = [(102, 340), (190, 172), (256, 288), (322, 132), (410, 340)]
    draw.line(points, fill="#5eead4", width=30, joint="curve")
    for x, y in points:
        draw.ellipse((x - 22, y - 22, x + 22, y + 22), fill="white")
    label = "DataAI IRIS"
    label_font = font(54, True)
    bounds = draw.textbbox((0, 0), label, font=label_font)
    draw.text(((512 - (bounds[2] - bounds[0])) / 2, 392), label, fill="white", font=label_font)
    image.save(assets / "dataai-iris-icon.png", optimize=True)


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, value: str, accent: str) -> None:
    draw.rounded_rectangle(box, radius=18, fill="#ffffff", outline="#dbe5ef", width=2)
    x1, y1, _, _ = box
    draw.rectangle((x1, y1, x1 + 8, box[3]), fill=accent)
    draw.text((x1 + 28, y1 + 22), title, fill="#52616f", font=font(23))
    draw.text((x1 + 28, y1 + 62), value, fill="#172554", font=font(44, True))


def new_canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1440, 900), "#f4f7fb")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1440, 118), fill="#172554")
    draw.text((54, 26), title, fill="white", font=font(39, True))
    draw.text((56, 78), subtitle, fill="#99f6e4", font=font(20))
    draw.rounded_rectangle((1180, 31, 1384, 87), radius=16, fill="#0f766e")
    draw.text((1204, 48), "FICTIONAL DATA", fill="white", font=font(18, True))
    return image, draw


def create_screenshots() -> None:
    screenshots = ROOT / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)

    image, draw = new_canvas("DataAI ETL for InterSystems IRIS", "Customer-controlled Spark processing • JDBC read/write • no hosted service")
    card(draw, (54, 154, 350, 292), "Rows evaluated", "25,000", "#0f766e")
    card(draw, (378, 154, 674, 292), "Accepted", "24,180", "#2563eb")
    card(draw, (702, 154, 998, 292), "Rejected", "820", "#f59e0b")
    card(draw, (1026, 154, 1384, 292), "Quality score", "96.7%", "#7c3aed")
    stages = [(70, "IRIS source", "Read-only JDBC"), (390, "DataAI Spark", "Quality + analytics"), (710, "Governed outputs", "Run metadata"), (1030, "IRIS targets", "Explicit save")]
    for index, (x, heading, detail) in enumerate(stages):
        draw.rounded_rectangle((x, 390, x + 270, 550), radius=22, fill="white", outline="#b8cadb", width=2)
        draw.ellipse((x + 102, 410, x + 168, 476), fill="#0f766e")
        draw.text((x + 128, 424), str(index + 1), anchor="mm", fill="white", font=font(25, True))
        draw.text((x + 24, 493), heading, fill="#172554", font=font(24, True))
        draw.text((x + 24, 526), detail, fill="#52616f", font=font(18))
        if index < len(stages) - 1:
            draw.line((x + 270, 470, stages[index + 1][0] - 14, 470), fill="#0f766e", width=6)
    draw.rounded_rectangle((54, 650, 1384, 824), radius=20, fill="#e6fffb", outline="#99f6e4", width=2)
    draw.text((82, 680), "Embedded-library boundary", fill="#115e59", font=font(25, True))
    draw.text((82, 726), "Credentials stay with the customer. DataAI prepares DataFrames; the customer selects tables, save modes, scheduling and retention.", fill="#234e52", font=font(22))
    draw.text((82, 770), "Design preview for marketplace review — not a live IRIS screenshot", fill="#52616f", font=font(18))
    image.save(screenshots / "iris-pipeline.png", optimize=True)

    image, draw = new_canvas("DataAI Quality & Matrix Results", "Prepared IRIS table contracts • auditable run metadata • matrix convergence retained")
    card(draw, (54, 154, 374, 292), "Critical findings", "0", "#16a34a")
    card(draw, (402, 154, 722, 292), "Errors", "31", "#dc2626")
    card(draw, (750, 154, 1070, 292), "Warnings", "94", "#f59e0b")
    card(draw, (1098, 154, 1384, 292), "Matrix error", "0.0008", "#7c3aed")
    draw.rounded_rectangle((54, 342, 782, 824), radius=20, fill="white", outline="#dbe5ef", width=2)
    draw.text((82, 370), "Quality findings by rule", fill="#172554", font=font(26, True))
    bars = [("customer_required", 31, "#dc2626"), ("amount_nonnegative", 22, "#f59e0b"), ("order_date_format", 18, "#2563eb"), ("region_accepted", 11, "#0f766e")]
    maximum = max(value for _, value, _ in bars)
    for i, (label, value, color) in enumerate(bars):
        y = 438 + i * 82
        draw.text((82, y), label, fill="#52616f", font=font(19))
        draw.rounded_rectangle((310, y, 710, y + 28), radius=10, fill="#e8eef5")
        draw.rounded_rectangle((310, y, 310 + int(400 * value / maximum), y + 28), radius=10, fill=color)
        draw.text((728, y - 2), str(value), fill="#172554", font=font(20, True))
    draw.rounded_rectangle((816, 342, 1384, 824), radius=20, fill="white", outline="#dbe5ef", width=2)
    draw.text((844, 370), "Balanced matrix", fill="#172554", font=font(26, True))
    values = [[18.2, 21.8], [31.8, 28.2]]
    colors = [["#ccfbf1", "#99f6e4"], ["#5eead4", "#2dd4bf"]]
    for row in range(2):
        for column in range(2):
            x1, y1 = 900 + column * 180, 465 + row * 130
            draw.rounded_rectangle((x1, y1, x1 + 150, y1 + 102), radius=15, fill=colors[row][column])
            draw.text((x1 + 75, y1 + 50), f"{values[row][column]:.1f}", anchor="mm", fill="#134e4a", font=font(30, True))
    draw.text((915, 728), "Converged: true • 7 iterations", fill="#115e59", font=font(21, True))
    draw.text((915, 770), "Fictional matrix targets", fill="#52616f", font=font(18))
    image.save(screenshots / "iris-data-quality.png", optimize=True)


def copy_licenses() -> None:
    for name in ("LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md"):
        shutil.copyfile(REPOSITORY / name, ROOT / name)


def distribution_files() -> list[tuple[Path, str]]:
    result: list[tuple[Path, str]] = []
    for name in ("README.md", "LICENSE.md", "COMMERCIAL_LICENSE_TEMPLATE.md", "THIRD_PARTY_NOTICES.md", "manifest.json"):
        result.append((ROOT / name, name))
    for directory in ("examples", "mapping", "sample-data", "ipm", "listing", "assets", "screenshots"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file():
                result.append((path, path.relative_to(ROOT).as_posix()))
    jar = ROOT / "target" / JAR_NAME
    if not jar.exists():
        raise FileNotFoundError(f"Build the Maven reactor before packaging: {jar}")
    result.append((jar, f"lib/{JAR_NAME}"))
    return result


def create_distribution() -> None:
    destination = ROOT / "distribution"
    destination.mkdir(parents=True, exist_ok=True)
    package = destination / "DataAI_ETL_IRIS_Evaluation.zip"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, archive_name in distribution_files():
            archive.write(source, archive_name)


def checksum_candidates() -> list[Path]:
    candidates = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == "CHECKSUMS.sha256" or "__pycache__" in path.parts:
            continue
        if "target" in path.parts and path.name != JAR_NAME:
            continue
        candidates.append(path)
    return sorted(candidates, key=lambda item: item.relative_to(ROOT).as_posix())


def create_checksums() -> None:
    lines = []
    for path in checksum_candidates():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    write_text_crlf(ROOT / "CHECKSUMS.sha256", "\n".join(lines))


def normalize_text_files() -> None:
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS and "target" not in path.parts:
            write_text_crlf(path, path.read_text(encoding="utf-8-sig"))


def main() -> None:
    copy_licenses()
    create_icon()
    create_screenshots()
    normalize_text_files()
    create_distribution()
    create_checksums()
    print("Generated IRIS licenses, marketplace assets, evaluation ZIP, and SHA-256 checksums.")


if __name__ == "__main__":
    main()
