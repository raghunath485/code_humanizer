from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app_backend.career_engine import build_career_pack
from app_backend.concept_engine import ALL_CONCEPTS, build_concept_plan
from app_backend.converter_engine import SUPPORTED_LANGUAGES, convert_code
from app_backend.humanizer_engine import humanize
from app_backend.schemas import AssistantRequest, CodeRequest, ConversionRequest, HumanizeOptions


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("code-humanizer")

ROOT = Path(__file__).resolve().parent.parent
MAX_REQUEST_SIZE = 1024 * 1024

app = FastAPI(title="Code Humanizer V2", version="2.0.0", docs_url="/api/docs", redoc_url="/api/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    if request.headers.get("content-length") and int(request.headers["content-length"]) > MAX_REQUEST_SIZE:
        return JSONResponse({"error": "Request too large"}, status_code=413)

    try:
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response
    except Exception as error:  # pragma: no cover
        logger.exception("Unhandled request failure")
        return JSONResponse({"error": str(error), "status": "internal_error"}, status_code=500)


@app.get("/api/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": "2.0.0",
        "supported_conversion_languages": sorted(SUPPORTED_LANGUAGES),
        "available_concepts": ALL_CONCEPTS,
    }


@app.post("/api/humanize")
async def humanize_endpoint(request: CodeRequest) -> dict[str, object]:
    options = HumanizeOptions(
        add_summary_comment=bool(request.options.get("add_summary_comment", True)),
        rename_identifiers=bool(request.options.get("rename_identifiers", True)),
        normalize_spacing=bool(request.options.get("normalize_spacing", True)),
        language_hint=request.language_hint or str(request.options.get("language_hint", "auto")),
        target_profile=str(request.options.get("target_profile", "developer_friendly")),
        add_docstrings=bool(request.options.get("add_docstrings", True)),
        explain_complexity=bool(request.options.get("explain_complexity", True)),
        detect_dead_code=bool(request.options.get("detect_dead_code", True)),
        concept_preferences=request.concept_preferences,
        refactor_mode=request.refactor_mode,
    )
    return humanize(request.code, options)


@app.post("/api/convert")
async def convert_endpoint(request: ConversionRequest) -> dict[str, object]:
    concept_plan = build_concept_plan(request.concept_preferences)
    return convert_code(
        code=request.code,
        source_language=request.source_language,
        target_language=request.target_language,
        concept_plan=concept_plan,
        refactor_mode=request.refactor_mode,
    )


@app.post("/api/assistant")
async def assistant_endpoint(request: AssistantRequest) -> dict[str, object]:
    analysis = humanize(
        request.code,
        HumanizeOptions(language_hint=request.language_hint, target_profile="developer_friendly"),
    )
    career_pack = build_career_pack(
        request.code,
        request.language_hint,
        analysis.get("quality", {}),
        analysis.get("security", {}),
    )
    return {
        "analysis": analysis,
        "career_pack": career_pack,
    }


app.mount("/assets", StaticFiles(directory=ROOT), name="assets")


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/{file_path:path}")
async def static_file(file_path: str) -> FileResponse:
    path = (ROOT / file_path).resolve()
    if ROOT not in path.parents and path != ROOT:
        return FileResponse(ROOT / "index.html")
    if path.exists() and path.is_file():
        return FileResponse(path)
    return FileResponse(ROOT / "index.html")
