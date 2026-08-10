# Runtime Compatibility

| Component | Evaluation target | Status |
|---|---|---|
| Alteryx Designer | 2026.1 | Package target; external execution pending |
| Alteryx engine | AMP | Required by AYX Python SDK |
| Embedded Python | 3.13.11 | YXI dependency build target |
| AYX Python SDK | 2.5.3 | Bundled in candidate YXI |
| AYX Plugin CLI format | 1.3.2 | Source metadata and archive layout |
| Java | 17 | DataAI build/runtime target |
| Apache Spark | 3.5.0 | DataAI build baseline; customer-provided |
| Scala binary | 2.12 | DataAI build baseline |
| Hadoop | Spark-provided | Not bundled |
| Delta Lake | Customer runtime | Required for configured table outputs |

This table is not a certification claim. Alteryx Designer and Server were not
installed in the build environment, so the provider must execute all release
gates before changing `externalDesignerValidation` or `submissionReady`.

Python-based YXI files are tied to the embedded Python generation. Produce and
test separate editions for Designer 2024.1–2025.2 (Python 3.10) or older
Designer versions; do not advertise one binary as universally compatible.
