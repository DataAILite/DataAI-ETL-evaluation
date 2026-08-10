"""DataAI ETL Alteryx tool package."""

try:
    from .data_ai_etl_quality import DataAiEtlQuality
except ModuleNotFoundError as exc:
    # Offline command/configuration unit tests do not require the proprietary
    # AYX Python SDK. Designer packages the SDK before loading this module.
    if not (exc.name or "").startswith(("ayx_python_sdk", "pyarrow")):
        raise
    __all__: list[str] = []
else:
    __all__ = ["DataAiEtlQuality"]
