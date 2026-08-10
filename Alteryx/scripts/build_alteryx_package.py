"""Build the YXI, evaluation archive, and Marketplace submission ZIP."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
YXI_NAME = "DataAI_ETL_Alteryx_2026_1_Evaluation.yxi"
EVALUATION_NAME = "DataAI_ETL_Alteryx_Evaluation.zip"
SUBMISSION_NAME = "DataAIETLAlteryx.zip"
FIXED_TIME = (2026, 8, 9, 12, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive: Path, target: Path) -> None:
    with zipfile.ZipFile(archive) as source:
        target_resolved = target.resolve()
        for member in source.infolist():
            destination = (target / member.filename).resolve()
            if target_resolved not in destination.parents and destination != target_resolved:
                raise ValueError(f"Unsafe wheel path: {member.filename}")
        source.extractall(target)


def write_zip(source: Path, destination: Path, prefix: str = "") -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(source).as_posix()
            name = f"{prefix.rstrip('/')}/{relative}" if prefix else relative
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def copy_tree(source: Path, target: Path, ignore=None) -> None:
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignore)


def build_yxi(wheel_dir: Path) -> Path:
    source = ROOT / "yxi-source"
    ui_dist = source / "ui" / "DataAiEtlQuality" / "dist"
    if not (ui_dist / "index.html").is_file():
        raise FileNotFoundError(
            "UI dist/index.html is missing. Run npm ci and npm run build in "
            "yxi-source/ui/DataAiEtlQuality."
        )

    required_wheel = next(wheel_dir.glob("ayx_python_sdk-2.5.3-cp313-*.whl"), None)
    if required_wheel is None:
        raise FileNotFoundError("AYX Python SDK 2.5.3 cp313 wheel is missing.")

    runtime_jar = (
        source
        / "backends"
        / "ayx_plugins"
        / "runtime"
        / "dataai-spark-cli-0.1.0-SNAPSHOT.jar"
    )
    if not runtime_jar.is_file():
        raise FileNotFoundError(f"DataAI CLI JAR is missing: {runtime_jar}")

    destination = ROOT / "build" / YXI_NAME
    with tempfile.TemporaryDirectory(prefix="dataai-alteryx-yxi-") as temporary:
        staging = Path(temporary)
        shutil.copy2(source / "configuration" / "Config.xml", staging / "Config.xml")
        shutil.copy2(
            source / "configuration" / "dataai-alteryx-icon.png",
            staging / "dataai-alteryx-icon.png",
        )

        tool = staging / "DataAiEtlQuality_1_0"
        tool.mkdir()
        config_dir = source / "configuration" / "DataAiEtlQuality_1_0"
        for name in (
            "DataAiEtlQuality_1_0Config.xml",
            "manifest.json",
            "dataai-alteryx-icon.png",
        ):
            shutil.copy2(config_dir / name, tool / name)
        shutil.copy2(source / "main.pyz", tool / "main.pyz")

        for item in ui_dist.iterdir():
            if item.is_file() and item.suffix != ".gz":
                shutil.copy2(item, tool / item.name)

        site_packages = tool / "site-packages"
        site_packages.mkdir()
        wheels = sorted(wheel_dir.glob("*.whl"))
        if len(wheels) < 10:
            raise RuntimeError("The Python 3.13 Alteryx dependency wheel set is incomplete.")
        for wheel in wheels:
            safe_extract(wheel, site_packages)
        copy_tree(source / "backends" / "ayx_plugins", site_packages / "ayx_plugins")
        write_zip(staging, destination)
    return destination


def build_evaluation(yxi: Path) -> Path:
    destination = ROOT / "distribution" / EVALUATION_NAME
    with tempfile.TemporaryDirectory(prefix="dataai-alteryx-eval-") as temporary:
        staging = Path(temporary)
        (staging / "install").mkdir()
        shutil.copy2(yxi, staging / "install" / yxi.name)
        copy_tree(ROOT / "lib", staging / "lib")
        copy_tree(ROOT / "docs", staging / "docs")
        copy_tree(ROOT / "samples", staging / "samples")
        for name in (
            "README.md",
            "LICENSE.md",
            "COMMERCIAL_LICENSE_TEMPLATE.md",
            "THIRD_PARTY_NOTICES.md",
        ):
            shutil.copy2(ROOT / name, staging / name)
        write_zip(staging, destination, "DataAI_ETL_Alteryx_Evaluation")
    return destination


def write_checksums(yxi: Path, evaluation: Path) -> None:
    paths = [yxi, evaluation, *sorted((ROOT / "lib").glob("*.jar"))]
    lines = [f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in paths]
    (ROOT / "CHECKSUMS.sha256").write_bytes(
        ("\r\n".join(lines) + "\r\n").encode("utf-8")
    )


def build_submission(evaluation: Path) -> Path:
    destination = PROJECT_ROOT / SUBMISSION_NAME
    with tempfile.TemporaryDirectory(prefix="dataai-alteryx-submission-") as temporary:
        staging = Path(temporary) / "DataAIETLAlteryx"
        staging.mkdir(parents=True)
        for name in (
            "README.md",
            "LICENSE.md",
            "COMMERCIAL_LICENSE_TEMPLATE.md",
            "THIRD_PARTY_NOTICES.md",
            "manifest.json",
            "MARKETPLACE_SUBMISSION.md",
            "PROVIDER_CHECKLIST.md",
            "CHECKSUMS.sha256",
        ):
            shutil.copy2(ROOT / name, staging / name)
        for directory in ("assets", "docs", "listing", "samples", "screenshots", "scripts", "tests"):
            copy_tree(ROOT / directory, staging / directory)
        copy_tree(
            ROOT / "yxi-source",
            staging / "yxi-source",
            ignore=shutil.ignore_patterns("node_modules", "dist", "*.pyc", "__pycache__"),
        )
        (staging / "distribution").mkdir()
        shutil.copy2(evaluation, staging / "distribution" / evaluation.name)
        write_zip(staging.parent, destination)
    digest_file = destination.with_suffix(destination.suffix + ".sha256")
    digest_file.write_bytes(
        f"{sha256(destination)}  {destination.name}\r\n".encode("utf-8")
    )
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wheel-dir",
        type=Path,
        default=PROJECT_ROOT / ".tools" / "alteryx-cp313-wheels",
        help="Directory containing the complete AYX Python SDK cp313 wheel set.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    yxi = build_yxi(args.wheel_dir.resolve())
    evaluation = build_evaluation(yxi)
    write_checksums(yxi, evaluation)
    submission = build_submission(evaluation)
    print(f"YXI: {yxi}")
    print(f"Evaluation ZIP: {evaluation}")
    print(f"Submission ZIP: {submission}")


if __name__ == "__main__":
    main()
