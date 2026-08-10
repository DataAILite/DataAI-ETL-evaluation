#!/usr/bin/env python3
"""Generate one or all remaining DataAI ETL marketplace review packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image, ImageDraw, ImageFont


SCRIPT = Path(__file__).resolve()
REPOSITORY = SCRIPT.parents[2]
SPARK = REPOSITORY / "spark"
SPARK_ETL = REPOSITORY / "SparkETL"
VERSION = "0.1.0-SNAPSHOT"
MODULES = (
    "dataai-spark-api",
    "dataai-spark-quality",
    "dataai-spark-core",
    "dataai-spark-functions",
    "dataai-spark-cli",
)
ZIP_DATE = (2026, 8, 7, 0, 0, 0)
STATEMENT = (
    "DataAI ETL is proprietary, source-available evaluation software from "
    "Yanbor LLC, built with open-source technologies including Apache Spark."
)


CHANNELS = {
    "AWS": {
        "display": "AWS Marketplace",
        "archive": "DataAIETLAWS.zip",
        "offer_type": "Linux container product for Amazon EMR Serverless",
        "color": "#ff9900",
        "short": "Embed DataAI quality, analytics, market, mapping, and matrix functions in customer-controlled Amazon EMR Spark workloads.",
        "recommended": (
            "Use a Linux container delivery option built from an approved Amazon EMR Serverless "
            "Spark base image. DataAI JARs are added to the image while EMR remains the runtime."
        ),
        "gates": [
            "Replace the SNAPSHOT build with an immutable production release.",
            "Build and scan AMD64 and any claimed ARM64 images in AWS Marketplace-managed ECR.",
            "Validate the selected EMR release, Java, Spark, Scala, IAM, and job behavior.",
            "Select BYOL, contract, or supported pricing and complete seller review.",
            "Provide fully self-service usage instructions without external paid dependencies.",
        ],
        "steps": [
            "Register Yanbor LLC as an AWS Marketplace seller and complete tax and banking onboarding.",
            "Create a new container product and its AWS Marketplace-managed ECR repositories.",
            "Choose a supported EMR Serverless Spark base image matching the qualified DataAI runtime.",
            "Build the container with `--build-arg BASE_IMAGE=<approved-image>` and an immutable DataAI release.",
            "Scan the image, verify non-root/runtime behavior, and push it to the assigned Marketplace ECR repository.",
            "Create a container-image delivery option and supply complete EMR Serverless launch instructions.",
            "Enter the listing copy, support/privacy/terms URLs, pricing, regions, logo, and screenshots.",
            "Test subscription, image pull, EMR application creation, Spark job execution, upgrades, and cancellation in a buyer account.",
            "Submit for AWS review and address security or metadata findings before publishing.",
        ],
        "install": (
            "Build from an AWS-provided EMR Serverless Spark image, preserving its entrypoint and `hadoop` user. "
            "The Dockerfile copies DataAI JARs to `/opt/dataai/lib` and `/usr/lib/spark/jars`. Customers select "
            "the resulting Marketplace image when creating EMR Serverless Spark compute. No DataAI service runs."
        ),
        "references": [
            "https://docs.aws.amazon.com/marketplace/latest/userguide/container-based-products.html",
            "https://docs.aws.amazon.com/marketplace/latest/userguide/container-product-policies.html",
            "https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-custom-image.html",
        ],
    },
    "Microsoft": {
        "display": "Microsoft Marketplace",
        "archive": "DataAIETLMicrosoft.zip",
        "offer_type": "Azure Container / Kubernetes application review candidate",
        "color": "#00a4ef",
        "short": "Add DataAI Spark quality, analytics, market, mapping, and matrix libraries to customer-controlled Azure data pipelines.",
        "recommended": (
            "Use this kit for Partner Center review and offer-type selection. Azure Container offers require "
            "a Kubernetes application packaged as CNAB; a raw JAR or single container is not accepted."
        ),
        "gates": [
            "Select an accepted Azure offer type that does not misrepresent DataAI as SaaS.",
            "Replace SNAPSHOT artifacts with an immutable production release.",
            "Build a functional AKS application and CNAB if the Azure Container route is approved.",
            "Approve public-registry exposure of proprietary container layers before using that route.",
            "Complete Partner Center certification, pricing, privacy, and support requirements.",
        ],
        "steps": [
            "Enroll Yanbor LLC in Microsoft Marketplace through Partner Center.",
            "Review the library-only architecture with Microsoft and select Azure Container, Azure Application, VM, or a lead-generation path.",
            "If Azure Container is approved, design a functional customer-run AKS application; single containers are unsupported.",
            "Build the Linux AMD64 component image from `container/Dockerfile` using immutable DataAI artifacts.",
            "Create and validate a CNAB bundle, publish it to the primary-tenant ACR, and use a numeric `#.#.#` tag.",
            "Configure the offer, plan, technical assets, markets, pricing, listing copy, URLs, logos, and screenshots.",
            "Test the preview audience deployment, library availability, customer control, upgrades, and removal.",
            "Confirm that public Microsoft ACR distribution is compatible with DataAI licensing and IP policy.",
            "Submit for certification only after legal, security, and runtime approval.",
        ],
        "install": (
            "The included Dockerfile is a component-image candidate, not a finished CNAB. It stores DataAI JARs "
            "under `/opt/dataai/lib` and performs no hosted processing. A marketplace submission needs an approved "
            "Kubernetes application design or a different offer type selected with Microsoft."
        ),
        "references": [
            "https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-offer-setup",
            "https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-technical-assets-kubernetes",
            "https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-plan-technical-configuration-kubernetes",
        ],
    },
    "Oracle": {
        "display": "Oracle Cloud Marketplace",
        "archive": "DataAIETLOracle.zip",
        "offer_type": "OCI application container image or lead-generation listing",
        "color": "#c74634",
        "short": "Run DataAI Spark data quality, analytics, market, mapping, and matrix libraries in customer-controlled OCI pipelines.",
        "recommended": (
            "Start with an Oracle lead-generation listing for private JAR fulfillment, or use an OCI container "
            "image only after Oracle approves the library-delivery model and an immutable release."
        ),
        "gates": [
            "Complete OCI partner and Marketplace Publisher onboarding.",
            "Choose lead generation or a supported OCI application package type.",
            "Replace SNAPSHOT artifacts and validate OCI Data Flow compatibility.",
            "Build, scan, and upload the container artifact to OCI Publisher when using a container listing.",
            "Complete paid-listing eligibility, terms, support, and regional availability review.",
        ],
        "steps": [
            "Enroll Yanbor LLC in Oracle PartnerNetwork and complete Marketplace Publisher onboarding.",
            "Select a lead-generation listing for controlled private delivery or an OCI Application container listing.",
            "Replace all placeholders and provide Oracle-required support, related documents, terms, and system requirements.",
            "For a container listing, build and scan the Linux image from `container/Dockerfile` with immutable DataAI JARs.",
            "Push the image to OCI Container Registry, create a Publisher artifact, and attach it to a listing revision.",
            "Validate extraction or placement of JARs in customer-controlled Object Storage for OCI Data Flow jobs.",
            "Upload the listing icon, banner, screenshots, release notes, documentation, and pricing plan.",
            "Test launch and Spark execution in a separate OCI tenancy without Yanbor credentials or services.",
            "Submit the listing revision for Oracle review and publish only after approval.",
        ],
        "install": (
            "The container stores DataAI JARs in `/opt/dataai/lib`. For OCI Data Flow, the customer copies licensed "
            "artifacts to customer-controlled Object Storage and supplies their URIs as Spark job dependencies. "
            "No Yanbor-hosted runtime or customer-data transfer is required."
        ),
        "references": [
            "https://docs.oracle.com/en-us/iaas/Content/Marketplace/Tasks/creating-oci-application-listing.htm",
            "https://docs.oracle.com/en-us/iaas/Content/Marketplace/publishing_guidelines.htm",
            "https://docs.oracle.com/en-us/iaas/Content/Marketplace/become-oci-partner.htm",
        ],
    },
    "Google": {
        "display": "Google Cloud Marketplace",
        "archive": "DataAIETLGoogle.zip",
        "offer_type": "Container image product for customer-controlled Dataproc delivery",
        "color": "#4285f4",
        "short": "Embed DataAI Spark quality, analytics, market, mapping, and matrix functions in customer-controlled Google Cloud pipelines.",
        "recommended": (
            "Use a Google Cloud Marketplace container image as the licensed artifact carrier after partner "
            "approval, then place JARs in customer-controlled Cloud Storage for Dataproc jobs."
        ),
        "gates": [
            "Complete Google Cloud Marketplace partner onboarding and Producer Portal access.",
            "Replace SNAPSHOT artifacts with an immutable production release.",
            "Obtain the product service name and add the required OCI image annotation.",
            "Build, scan, stage, and validate the image in Google's required registry workflow.",
            "Test Dataproc compatibility, pricing, support, and private-offer behavior.",
        ],
        "steps": [
            "Enroll Yanbor LLC as a Google Cloud Marketplace partner and complete the Project Info process.",
            "Create the container image product in Producer Portal and obtain its service name.",
            "Replace `<SERVICE_NAME>` in the Dockerfile label and use immutable DataAI artifacts.",
            "Build and scan the image, then push approved tags to the staging `gcr.io` repository.",
            "Configure Google to copy the selected tags into `marketplace.gcr.io`.",
            "Enter listing copy, pricing, regions, support/privacy/terms URLs, icon, and screenshots.",
            "Test subscription and image access from a buyer project, then copy JARs into customer-controlled Cloud Storage.",
            "Execute representative Dataproc Spark jobs including matrix balancing and explicit output writes.",
            "Submit for partner-engineering review and publish only after approval.",
        ],
        "install": (
            "The container stores DataAI JARs in `/opt/dataai/lib`. Customers copy licensed artifacts into a "
            "governed Cloud Storage bucket and reference them with Dataproc `--jars` or cluster initialization. "
            "The image has no DataAI service, telemetry, or customer-data callback."
        ),
        "references": [
            "https://docs.cloud.google.com/marketplace/docs/partners/container",
            "https://docs.cloud.google.com/marketplace/docs/partners",
        ],
    },
    "Maven": {
        "display": "Maven Central",
        "archive": "DataAIETLMaven.zip",
        "offer_type": "Maven Central pre-publication component bundle",
        "color": "#c71a36",
        "short": "Consume DataAI Spark quality, analytics, market, mapping, and matrix libraries through standard Maven coordinates.",
        "recommended": (
            "Use this as a release-engineering review kit. Maven Central is public, immutable, and not a billing "
            "marketplace; publish only after Yanbor approves public distribution and completes all release gates."
        ),
        "gates": [
            "Verify a Yanbor-controlled groupId namespace; do not assume `com.dataai` is publishable.",
            "Replace SNAPSHOT with an immutable release consistently in POMs, bytecode metadata, and filenames.",
            "Complete POM URL, license, developer, SCM, and dependency metadata.",
            "Generate binary, source, and Javadoc JARs and sign every deployable file with a Yanbor PGP key.",
            "Validate the Central bundle without uploading, then obtain explicit publication approval.",
        ],
        "steps": [
            "Create a Central Publisher Portal account for Yanbor LLC and verify a controlled namespace.",
            "Decide whether permanent public source/binary availability is compatible with the DataAI license strategy.",
            "Create an immutable release branch/version; update all modules and runtime version reporting together.",
            "Complete required POM metadata and configure the Central Publishing Maven Plugin.",
            "Generate binary, source, and Javadoc JARs for each published module.",
            "Sign every POM and JAR with an approved Yanbor PGP key and distribute the public key.",
            "Run a clean build and consumer dependency-resolution test in an empty local repository.",
            "Create a Central bundle with upload disabled and review validation results.",
            "Publish only after explicit Yanbor approval; released components cannot be replaced in place.",
        ],
        "install": (
            "The current repository-layout directory contains development-review artifacts only. It is not a "
            "Central upload bundle because its version ends in SNAPSHOT and it has no Yanbor PGP signatures. "
            "Licensed production customers should continue using an authenticated private Maven repository."
        ),
        "references": [
            "https://central.sonatype.org/publish/requirements/",
            "https://central.sonatype.org/publish/publish-portal-maven/",
            "https://central.sonatype.org/register/namespace/",
        ],
    },
}


def write_text(path: Path, value: str) -> None:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))


def copy_text(source: Path, destination: Path) -> None:
    write_text(destination, source.read_text(encoding="utf-8-sig"))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")
    for name in names:
        candidate = Path("C:/Windows/Fonts") / name
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def render_readme(channel: str, cfg: dict) -> str:
    return f"""# DataAI ETL for {cfg['display']}

{STATEMENT}

This directory is the {cfg['display']} review, packaging, and controlled-evaluation kit for the DataAI Spark libraries. DataAI remains embedded software that runs inside customer-controlled compute. It is not a required hosted service.

## Recommended delivery model

{cfg['recommended']}

## Current status

The included `{VERSION}` artifacts are evaluation-development builds. This package is intentionally marked **not submission-ready** until the channel-specific release and partner gates in `PROVIDER_CHECKLIST.md` are complete. Nothing in this directory publishes, uploads, authenticates, or contacts {cfg['display']}.

## Contents

| Path | Purpose |
| --- | --- |
| `listing/` | Draft marketplace or repository metadata |
| `docs/` | Installation, release-gate, security, and function documentation |
| `lib/` | Verified DataAI evaluation artifacts |
| `assets/` | DataAI listing artwork |
| `screenshots/` | Fictional-data design previews |
| `distribution/` | Customer evaluation ZIP |
| `scripts/` | Deterministic generation and offline validation |
| `CHECKSUMS.sha256` | Package integrity manifest |

The repository-root `{cfg['archive']}` is the provider-review ZIP. Its sidecar is `{cfg['archive']}.sha256`.

## Start here

1. Read `MARKETPLACE_SUBMISSION.md`.
2. Complete `PROVIDER_CHECKLIST.md`.
3. Review `docs/INSTALLATION_AND_USAGE.md` and `docs/RELEASE_GATES.md`.
4. Replace all bracketed placeholders.
5. Generate and validate locally before any external submission.

## License

Evaluation use is governed by `LICENSE.md`. Production, continued use, redistribution, OEM, and managed-service use require separate written commercial terms from Yanbor LLC. The software is provided **AS IS**, and the customer is responsible for evaluating compatibility and suitability during the permitted evaluation period.
"""


def render_submission(channel: str, cfg: dict) -> str:
    steps = "\n".join(f"{index}. {step}" for index, step in enumerate(cfg["steps"], 1))
    refs = "\n".join(f"- `{url}`" for url in cfg["references"])
    return f"""# {cfg['display']} Submission Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

**Recommended offer type:** {cfg['offer_type']}

## Product boundary

{cfg['recommended']}

The raw DataAI JAR bundle is not assumed to be an accepted marketplace product type. The current SNAPSHOT build is for evaluation and reviewer preparation only. Do not submit it as a production release.

## Submission steps

{steps}

## Files supplied by this kit

- Listing copy: `listing/{channel.upper()}_LISTING.md`
- Provider gates: `PROVIDER_CHECKLIST.md`
- Customer installation: `docs/INSTALLATION_AND_USAGE.md`
- Release blockers: `docs/RELEASE_GATES.md`
- Function inventory: `docs/FUNCTION_CATALOG.md`
- Evaluation download: `distribution/DataAI_ETL_{channel}_Evaluation.zip`
- Integrity checks: `CHECKSUMS.sha256`

## External references

Marketplace requirements change. Recheck these official sources on the submission date:

{refs}
"""


def render_checklist(cfg: dict) -> str:
    gates = "\n".join(f"- [ ] {gate}" for gate in cfg["gates"])
    return f"""# {cfg['display']} Provider Checklist

## Channel-specific gates

{gates}

## Common legal and product gates

- [ ] Yanbor LLC publisher identity, tax, banking, and partner enrollment are approved.
- [ ] Evaluation and commercial terms have completed legal review.
- [ ] Public support, privacy, terms, documentation, and company URLs are live.
- [ ] All placeholders are replaced and listing claims match tested behavior.
- [ ] No listing describes DataAI as a hosted service.

## Artifact and security gates

- [ ] Full Maven `clean verify` passes with Java 17.
- [ ] Production version is immutable and does not end in `-SNAPSHOT`.
- [ ] SHA-256 checksums and any channel-required signatures pass.
- [ ] JARs contain no bundled Spark or Hadoop classes.
- [ ] Container or repository artifacts contain no credentials, keys, tokens, customer data, or signed agreements.
- [ ] Vulnerability, malware, dependency, and license reviews are current.
- [ ] Installation, upgrades, rollback, and revocation are tested in a separate buyer environment.

## Publication authorization

- [ ] Pricing and fulfillment match the signed DataAI commercial model.
- [ ] Yanbor LLC authorizes the exact final files and external submission.
"""


def render_listing(cfg: dict) -> str:
    gates = "\n".join(f"- {gate}" for gate in cfg["gates"])
    return f"""# {cfg['display']} Listing Copy

**Publisher:** Yanbor LLC, provider of the DataAI product.

## Name

DataAI ETL Spark Libraries

## Short description

{cfg['short']}

## Detailed description

DataAI ETL embeds reusable data quality, normalization, profiling, validation, analytics, time-series, business, market, map-readiness, matrix-balancing, recommendation, alert, data-dictionary, and deterministic narrative functions inside customer-controlled Apache Spark pipelines.

Customers control compute, identity, networking, input DataFrames, output formats, catalogs, storage, save modes, scheduling, orchestration, and security. DataAI returns DataFrames and bounded metadata records. It has no required Yanbor-hosted runtime, telemetry, remote license check, or customer-data callback.

{STATEMENT}

## Intended users

- Data engineering and ETL teams
- Data quality and governance teams
- Spark platform administrators
- Analytics engineering teams
- Regulated organizations requiring customer-controlled execution

## Requirements and current release gates

{gates}

## Evaluation and commercial terms

Evaluation use is governed by the linked DataAI evaluation license. Production, continued use, redistribution, OEM, and managed-service use require a separate written commercial agreement with Yanbor LLC. The software is provided **AS IS**.

## URLs to replace

- Documentation: `[PUBLIC DATAAI DOCUMENTATION URL]`
- Support: `[DATAAI SUPPORT URL]`
- Support email: `[DATAAI SUPPORT EMAIL]`
- Privacy: `[DATAAI PRIVACY URL]`
- Terms: `[DATAAI TERMS URL]`
- Company: `[YANBOR LLC COMPANY URL]`

The supplied screenshots are design previews generated from fictional data. Replace them with captures from the validated target platform when the marketplace requires actual-product screenshots.
"""


def render_install(cfg: dict) -> str:
    return f"""# Installation and Usage for {cfg['display']}

## Delivery model

{cfg['install']}

## Evaluation artifacts

Install these matching-version modules together:

- `dataai-spark-api-{VERSION}.jar`
- `dataai-spark-quality-{VERSION}.jar`
- `dataai-spark-core-{VERSION}.jar`
- `dataai-spark-functions-{VERSION}.jar`

The CLI JAR is optional. Spark and Hadoop are provided by the customer runtime and are not bundled by DataAI.

## Generic Spark usage

Add all required JARs to the Spark driver and executor classpaths using the target platform's supported library or `--jars` mechanism. Then call `DataAiPipeline` and the functions in `com.dataai.etl.spark.functions`. The complete inventory is in `FUNCTION_CATALOG.md`.

Customer code supplies `Dataset<Row>` inputs and decides whether returned DataFrames are written. DataAI performs no automatic persistence.

## Production

Do not deploy the included SNAPSHOT artifacts as production. After commercial licensing, use a Yanbor-authorized immutable release from the approved marketplace artifact, authenticated Maven repository, or customer artifact repository. Verify checksums and pin the exact version.

## Troubleshooting

- `UnsupportedClassVersionError`: select a Java 17-compatible runtime.
- Class not found: install API, quality, core, and functions at the same version.
- Scala linkage error: use a runtime compatible with Scala 2.12.
- Spark linkage error: validate against the documented Spark 3.5.x baseline.
- Permission failure: use customer-approved identity and storage permissions; DataAI does not bypass platform controls.
"""


def render_release_gates(cfg: dict) -> str:
    gates = "\n".join(f"{index}. {gate}" for index, gate in enumerate(cfg["gates"], 1))
    return f"""# Release Gates for {cfg['display']}

The generated package is complete for internal review and evaluation packaging, but it is not authorized for external marketplace publication.

{gates}

The `submissionReady` field in `manifest.json` must remain `false` until all gates are evidenced, the package is regenerated from immutable artifacts, and Yanbor LLC authorizes publication.
"""


def render_third_party() -> str:
    return """# Third-Party Notices

DataAI ETL compiles against Apache Spark 3.5.0 and transitive Hadoop APIs. Spark and Hadoop are Apache License 2.0 projects and remain provided dependencies; they are not bundled in DataAI library JARs.

The optional shaded DataAI CLI includes Jackson 2.15.3 components licensed under the Apache License 2.0. Maven, JUnit, and Pillow are build, test, or asset-generation tools and are not required DataAI services.

Marketplace names, Apache Spark, Hadoop, Jackson, Maven, Java, and other marks are the property of their respective owners. Mention does not imply endorsement, certification, or approval.
"""


def cloud_dockerfile(channel: str) -> str:
    if channel == "AWS":
        return f"""# Build only with a qualified Amazon EMR Serverless Spark base image.
ARG BASE_IMAGE
FROM ${{BASE_IMAGE}}
LABEL org.opencontainers.image.title="DataAI ETL Spark Libraries"
LABEL org.opencontainers.image.vendor="Yanbor LLC"
LABEL org.opencontainers.image.version="{VERSION}"
USER root
COPY lib/*.jar /opt/dataai/lib/
RUN mkdir -p /usr/lib/spark/jars && cp /opt/dataai/lib/*.jar /usr/lib/spark/jars/ && chmod -R a=rX /opt/dataai/lib /usr/lib/spark/jars
USER hadoop:hadoop
"""
    google_label = (
        'LABEL com.googleapis.cloudmarketplace.product.service.name="services/<SERVICE_NAME>"\n'
        if channel == "Google" else ""
    )
    return f"""ARG BASE_IMAGE=eclipse-temurin:17-jre
FROM ${{BASE_IMAGE}}
LABEL org.opencontainers.image.title="DataAI ETL Spark Libraries"
LABEL org.opencontainers.image.vendor="Yanbor LLC"
LABEL org.opencontainers.image.version="{VERSION}"
{google_label}RUN groupadd --system dataai && useradd --system --gid dataai --home-dir /nonexistent --shell /usr/sbin/nologin dataai
COPY lib/*.jar /opt/dataai/lib/
RUN chmod -R a=rX /opt/dataai/lib
USER dataai:dataai
CMD ["sh", "-c", "find /opt/dataai/lib -maxdepth 1 -type f -name '*.jar' -print"]
"""


def central_files(root: Path) -> None:
    settings = """<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0">
  <servers>
    <server>
      <id>central</id>
      <username>${env.CENTRAL_TOKEN_USERNAME}</username>
      <password>${env.CENTRAL_TOKEN_PASSWORD}</password>
    </server>
  </servers>
</settings>"""
    profile = """<!-- Merge only after immutable version, namespace, metadata, and signing gates pass. -->
<plugin>
  <groupId>org.sonatype.central</groupId>
  <artifactId>central-publishing-maven-plugin</artifactId>
  <version>0.9.0</version>
  <extensions>true</extensions>
  <configuration>
    <publishingServerId>central</publishingServerId>
    <autoPublish>false</autoPublish>
    <waitUntil>validated</waitUntil>
  </configuration>
</plugin>"""
    blocked = f"""MAVEN CENTRAL UPLOAD IS BLOCKED

Current version: {VERSION}

Reasons:
- Maven Central release versions cannot end in SNAPSHOT.
- The com.dataai namespace has not been verified in this package.
- POM publication metadata requires final legal and engineering review.
- Deployable POMs and JARs do not have Yanbor LLC PGP signatures.
- Public, permanent distribution has not been authorized.
"""
    write_text(root / "central" / "settings.xml.template", settings)
    write_text(root / "central" / "central-publishing-plugin.xml", profile)
    write_text(root / "central" / "MAVEN_CENTRAL_UPLOAD_BLOCKED.txt", blocked)


def copy_artifacts(channel: str, root: Path) -> None:
    if channel != "Maven":
        for module in MODULES:
            source = SPARK / module / "target" / f"{module}-{VERSION}.jar"
            if not source.is_file():
                raise FileNotFoundError(f"Build artifact is missing: {source}")
            shutil.copyfile(source, root / "lib" / source.name)
        return

    parent_source = SPARK_ETL / "poms" / "dataai-etl-spark-parent.pom"
    copy_text(parent_source, root / "poms" / "dataai-etl-spark-parent.pom")
    parent_target = root / "repository-layout" / "com" / "dataai" / "dataai-etl-spark-parent" / VERSION
    copy_text(parent_source, parent_target / f"dataai-etl-spark-parent-{VERSION}.pom")
    for module in MODULES:
        pom_source = SPARK_ETL / "poms" / f"{module}.pom"
        copy_text(pom_source, root / "poms" / f"{module}.pom")
        target = root / "repository-layout" / "com" / "dataai" / module / VERSION
        copy_text(pom_source, target / f"{module}-{VERSION}.pom")
        for classifier in ("", "-sources", "-javadoc"):
            name = f"{module}-{VERSION}{classifier}.jar"
            source = SPARK_ETL / "lib" / name
            if not source.is_file():
                raise FileNotFoundError(f"Maven review artifact is missing: {source}")
            destination = root / "lib" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            target.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target / name)


def create_media(channel: str, cfg: dict, root: Path) -> None:
    image = Image.new("RGB", (512, 512), "#071426")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((44, 44, 468, 468), 72, fill="#102a43", outline=cfg["color"], width=8)
    draw.text((256, 92), "DataAI", font=font(56, True), fill="white", anchor="mm")
    for index in range(4):
        x = 100 + index * 86
        draw.rounded_rectangle((x, 180, x + 54, 330), 16, fill=cfg["color"] if index % 2 == 0 else "#52e0a7")
    draw.text((256, 390), "ETL", font=font(70, True), fill="white", anchor="mm")
    draw.text((256, 448), channel.upper(), font=font(24, True), fill="#b9d7ef", anchor="mm")
    image.save(root / "assets" / f"dataai-{channel.lower()}-icon.png", optimize=True)
    image.resize((130, 130), Image.Resampling.LANCZOS).save(
        root / "assets" / f"dataai-{channel.lower()}-icon-130.png", optimize=True
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<rect width="512" height="512" rx="72" fill="#071426"/><rect x="44" y="44" width="424" height="424" rx="72" fill="#102a43" stroke="{cfg['color']}" stroke-width="8"/>
<text x="256" y="112" text-anchor="middle" fill="white" font-family="Segoe UI,Arial" font-size="56" font-weight="700">DataAI</text>
<rect x="100" y="180" width="54" height="150" rx="16" fill="{cfg['color']}"/><rect x="186" y="180" width="54" height="150" rx="16" fill="#52e0a7"/><rect x="272" y="180" width="54" height="150" rx="16" fill="{cfg['color']}"/><rect x="358" y="180" width="54" height="150" rx="16" fill="#52e0a7"/>
<text x="256" y="414" text-anchor="middle" fill="white" font-family="Segoe UI,Arial" font-size="70" font-weight="700">ETL</text><text x="256" y="466" text-anchor="middle" fill="#b9d7ef" font-family="Segoe UI,Arial" font-size="24" font-weight="700">{channel.upper()}</text></svg>"""
    write_text(root / "assets" / f"dataai-{channel.lower()}-icon.svg", svg)

    for name, heading in (("pipeline", "Customer-controlled Spark pipeline"), ("functions", "Portable DataAI function coverage")):
        canvas = Image.new("RGB", (1600, 900), "#071426")
        layer = ImageDraw.Draw(canvas)
        layer.rectangle((0, 0, 1600, 100), fill="#0d2238")
        layer.text((55, 30), "DataAI ETL", font=font(36, True), fill="white")
        layer.text((1545, 35), cfg["display"], font=font(23, True), fill=cfg["color"], anchor="ra")
        layer.text((55, 145), heading, font=font(44, True), fill="white")
        labels = (
            ("Input DataFrames", "Customer-selected data"),
            ("DataAI libraries", "Quality · analytics · matrix"),
            ("Output DataFrames", "Customer-selected writes"),
        ) if name == "pipeline" else (
            ("Quality", "Normalize · profile · validate"),
            ("Analytics", "Time · market · business"),
            ("Advanced", "Map · matrix · insights"),
        )
        for index, (title, subtitle) in enumerate(labels):
            left = 55 + index * 505
            layer.rounded_rectangle((left, 275, left + 445, 650), 30, fill="#102a43", outline=cfg["color"], width=3)
            layer.text((left + 32, 325), title, font=font(30, True), fill="white")
            layer.text((left + 32, 390), subtitle, font=font(21), fill="#b9d7ef")
            layer.rounded_rectangle((left + 32, 500, left + 375, 555), 18, fill=cfg["color"])
        layer.text((55, 855), "Design preview · fictional content · replace with validated target-platform captures", font=font(18), fill="#7fa7c4")
        canvas.save(root / "screenshots" / f"{channel.lower()}-{name}.png", optimize=True)


def zip_add(archive: zipfile.ZipFile, source: Path, destination: PurePosixPath) -> None:
    info = zipfile.ZipInfo(destination.as_posix(), date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, source.read_bytes())


def create_evaluation_zip(channel: str, root: Path) -> None:
    selected = [root / "README.md", root / "LICENSE.md", root / "THIRD_PARTY_NOTICES.md", root / "manifest.json"]
    for name in ("docs", "lib"):
        selected.extend(path for path in (root / name).rglob("*") if path.is_file())
    if channel != "Maven":
        selected.extend(path for path in (root / "container").rglob("*") if path.is_file())
    selected = sorted(set(selected), key=lambda path: path.relative_to(root).as_posix())
    checksum_lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}" for path in selected]
    evaluation_checksums = root / "distribution" / "EVALUATION_CHECKSUMS.sha256"
    write_text(evaluation_checksums, "\n".join(checksum_lines))
    package = root / "distribution" / f"DataAI_ETL_{channel}_Evaluation.zip"
    prefix = PurePosixPath(f"DataAI_ETL_{channel}_Evaluation")
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in selected:
            zip_add(archive, path, prefix / path.relative_to(root).as_posix())
        zip_add(archive, evaluation_checksums, prefix / "CHECKSUMS.sha256")


def create_checksums(root: Path) -> None:
    files = sorted(
        (path for path in root.rglob("*") if path.is_file() and path.name != "CHECKSUMS.sha256" and "__pycache__" not in path.parts),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    write_text(root / "CHECKSUMS.sha256", "\n".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}" for path in files
    ))


def create_provider_zip(channel: str, cfg: dict, root: Path) -> None:
    package = REPOSITORY / cfg["archive"]
    if package.exists():
        package.unlink()
    files = sorted(
        (path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            zip_add(archive, path, PurePosixPath(channel) / path.relative_to(root).as_posix())
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    write_text(REPOSITORY / f"{cfg['archive']}.sha256", f"{digest}  {cfg['archive']}")


def generate(channel: str) -> None:
    cfg = CHANNELS[channel]
    root = REPOSITORY / channel
    for name in ("scripts", "listing", "docs", "lib", "assets", "screenshots", "distribution"):
        (root / name).mkdir(parents=True, exist_ok=True)
    copy_text(REPOSITORY / "LICENSE.md", root / "LICENSE.md")
    copy_text(REPOSITORY / "COMMERCIAL_LICENSE_TEMPLATE.md", root / "COMMERCIAL_LICENSE_TEMPLATE.md")
    copy_text(REPOSITORY / "docs" / "FUNCTION_CATALOG.md", root / "docs" / "FUNCTION_CATALOG.md")
    write_text(root / "README.md", render_readme(channel, cfg))
    write_text(root / "MARKETPLACE_SUBMISSION.md", render_submission(channel, cfg))
    write_text(root / "PROVIDER_CHECKLIST.md", render_checklist(cfg))
    write_text(root / "listing" / f"{channel.upper()}_LISTING.md", render_listing(cfg))
    write_text(root / "docs" / "INSTALLATION_AND_USAGE.md", render_install(cfg))
    write_text(root / "docs" / "RELEASE_GATES.md", render_release_gates(cfg))
    write_text(root / "THIRD_PARTY_NOTICES.md", render_third_party())
    manifest = {
        "name": f"DataAI ETL Spark Libraries for {cfg['display']}",
        "provider": "Yanbor LLC",
        "providerDescription": "provider of the DataAI product",
        "packageVersion": VERSION,
        "packageStatus": "evaluation-development",
        "submissionReady": False,
        "channel": channel,
        "offerType": cfg["offer_type"],
        "runtime": {"java": "17", "spark": "3.5.0", "scalaBinary": "2.12"},
        "dataHandling": {"hostedService": False, "telemetry": False, "remoteLicenseCheck": False, "automaticWrites": False},
        "releaseGates": cfg["gates"],
    }
    write_text(root / "manifest.json", json.dumps(manifest, indent=2))
    copy_artifacts(channel, root)
    if channel == "Maven":
        central_files(root)
    else:
        (root / "container").mkdir(parents=True, exist_ok=True)
        write_text(root / "container" / "Dockerfile", cloud_dockerfile(channel))
        write_text(root / "container" / "README.md", cfg["install"])
    create_media(channel, cfg, root)
    if SCRIPT.resolve() != (root / "scripts" / SCRIPT.name).resolve():
        shutil.copyfile(SCRIPT, root / "scripts" / SCRIPT.name)
    validator_source = SCRIPT.with_name("validate_marketplace_package.py")
    if validator_source.is_file() and validator_source.resolve() != (root / "scripts" / validator_source.name).resolve():
        shutil.copyfile(validator_source, root / "scripts" / validator_source.name)
    create_evaluation_zip(channel, root)
    create_checksums(root)
    create_provider_zip(channel, cfg, root)
    print(f"Generated {channel} marketplace review package.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", choices=tuple(CHANNELS) + ("all",), nargs="?", default=SCRIPT.parents[1].name)
    args = parser.parse_args()
    channels = CHANNELS if args.channel == "all" else (args.channel,)
    for channel in channels:
        generate(channel)


if __name__ == "__main__":
    main()
