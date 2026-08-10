"""Generate deterministic Alteryx listing graphics for the DataAI ETL kit."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
NAVY = "#0b1f33"
BLUE = "#2f6fed"
CYAN = "#49c6e5"
ORANGE = "#fb923c"
WHITE = "#ffffff"
MUTED = "#d8e2ef"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "seguisb.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def icon() -> Image.Image:
    image = Image.new("RGB", (512, 512), NAVY)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, 492, 492), 88, fill=NAVY, outline=BLUE, width=10)
    points = [(92, 308), (174, 190), (254, 278), (330, 142), (420, 308)]
    draw.line(points, fill=CYAN, width=28, joint="curve")
    for x, y in points:
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=WHITE)
    draw.text((256, 382), "DataAI ETL", anchor="mm", fill=WHITE, font=font(50, True))
    draw.text((256, 438), "ALTERYX + SPARK", anchor="mm", fill=ORANGE, font=font(23, True))
    return image


def header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.rectangle((0, 0, 1440, 118), fill=NAVY)
    draw.text((58, 34), title, fill=WHITE, font=font(34, True))
    draw.text((58, 78), subtitle, fill=MUTED, font=font(19))
    draw.rounded_rectangle((1135, 26, 1384, 90), 12, fill="#7c2d12")
    draw.text((1259, 58), "DESIGN PREVIEW", anchor="mm", fill=WHITE, font=font(18, True))


def configuration_preview() -> Image.Image:
    image = Image.new("RGB", (1440, 900), "#eef3f8")
    draw = ImageDraw.Draw(image)
    header(draw, "DataAI ETL Quality", "Alteryx configuration panel — replace with tested Designer screenshot")
    draw.rounded_rectangle((70, 150, 1370, 840), 18, fill=WHITE, outline="#c7d4e3", width=2)
    draw.text((110, 182), "Spark runtime", fill=NAVY, font=font(26, True))
    fields = [
        ("Spark Submit", r"C:\Spark\bin\spark-submit.cmd"),
        ("Spark Master", "local[*]"),
        ("Source Table", "dataai_eval.customer_orders"),
        ("Clean Table", "dataai_eval.customer_orders_clean"),
        ("Rejected Table", "dataai_eval.customer_orders_rejected"),
        ("Minimum Quality Score", "80"),
    ]
    positions = [(110, 235), (750, 235), (110, 355), (750, 355), (110, 475), (750, 475)]
    for (label, value), (x, y) in zip(fields, positions):
        draw.text((x, y), label, fill="#42566c", font=font(17, True))
        draw.rounded_rectangle((x, y + 28, x + 540, y + 86), 8, fill="#f8fafc", outline="#9eb0c4")
        draw.text((x + 16, y + 56), value, anchor="lm", fill=NAVY, font=font(18))
    draw.text((110, 610), "Rules JSON", fill="#42566c", font=font(17, True))
    draw.rounded_rectangle((110, 642, 1290, 742), 8, fill="#f8fafc", outline="#9eb0c4")
    draw.text((128, 662), '[{"id":"order-id-required","type":"REQUIRED","field":"order_id","parameter":null}]', fill=NAVY, font=font(17))
    draw.rectangle((112, 780, 138, 806), fill=BLUE)
    draw.text((154, 793), "Evaluation license accepted; configured output tables may be overwritten", anchor="lm", fill=NAVY, font=font(17))
    return image


def workflow_preview() -> Image.Image:
    image = Image.new("RGB", (1440, 900), "#edf2f7")
    draw = ImageDraw.Draw(image)
    header(draw, "Customer-controlled ETL flow", "No Yanbor-hosted service or customer-data transfer")
    boxes = [
        (90, 310, 330, 505, "Alteryx\nworkflow", BLUE),
        (465, 310, 705, 505, "DataAI ETL\nQuality tool", "#7c3aed"),
        (840, 310, 1080, 505, "Customer\nSpark runtime", ORANGE),
        (1160, 310, 1360, 505, "Delta output\ntables", "#0f766e"),
    ]
    for x1, y1, x2, y2, text_value, color in boxes:
        draw.rounded_rectangle((x1, y1, x2, y2), 20, fill=color)
        draw.multiline_text(((x1 + x2) / 2, (y1 + y2) / 2), text_value, anchor="mm", align="center", fill=WHITE, font=font(25, True), spacing=10)
    for start, end in [((330, 407), (465, 407)), ((705, 407), (840, 407)), ((1080, 407), (1160, 407))]:
        draw.line((start, end), fill=NAVY, width=8)
        draw.polygon([(end[0], end[1]), (end[0] - 20, end[1] - 14), (end[0] - 20, end[1] + 14)], fill=NAVY)
    draw.rounded_rectangle((190, 635, 1250, 770), 16, fill=WHITE, outline="#c7d4e3", width=2)
    draw.text((720, 672), "Local argument-vector execution", anchor="mm", fill=NAVY, font=font(25, True))
    draw.text((720, 720), "spark-submit • shell=False • transient config • generic status only", anchor="mm", fill="#42566c", font=font(22))
    return image


def main() -> None:
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "screenshots").mkdir(parents=True, exist_ok=True)
    (ROOT / "yxi-source" / "configuration").mkdir(parents=True, exist_ok=True)

    icon_image = icon()
    icon_image.save(ROOT / "assets" / "dataai-alteryx-icon.png", optimize=True)
    icon_image.save(
        ROOT / "yxi-source" / "configuration" / "dataai-alteryx-icon.png",
        optimize=True,
    )
    icon_image.save(
        ROOT / "yxi-source" / "configuration" / "DataAiEtlQuality_1_0" / "dataai-alteryx-icon.png",
        optimize=True,
    )
    configuration_preview().save(
        ROOT / "screenshots" / "alteryx-configuration-preview.png", optimize=True
    )
    workflow_preview().save(
        ROOT / "screenshots" / "alteryx-workflow-preview.png", optimize=True
    )


if __name__ == "__main__":
    main()
