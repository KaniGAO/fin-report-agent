"""API 端点：/api/analyze 与 /api/generate"""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..config import ALLOWED_DOCX, ALLOWED_EXCEL, MAX_FILE_SIZE, TMP_DIR
from ..core.filler import analyze, fill_docx
from ..schemas import AnalyzeResponse

router = APIRouter(prefix="/api")

# session_id -> {"docx": path, "excels": [paths], "fill_plan": {...}}
_SESSIONS: dict[str, dict] = {}


def _save_upload(f: UploadFile, dest_dir: Path, allowed: set[str]) -> Path:
    suffix = Path(f.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"不支持的文件类型: {f.filename}")
    dest = dest_dir / f"{uuid.uuid4().hex[:8]}_{Path(f.filename).name}"
    size = 0
    with dest.open("wb") as out:
        while chunk := f.file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                dest.unlink(missing_ok=True)
                raise HTTPException(400, f"文件过大（>20MB）: {f.filename}")
            out.write(chunk)
    return dest


@router.post("/analyze", response_model=AnalyzeResponse)
async def api_analyze(
    docx: UploadFile = File(...),
    excels: list[UploadFile] = File(...),
):
    if len(excels) > 3:
        raise HTTPException(400, "最多上传 3 个 Excel 文件")

    session_id = uuid.uuid4().hex[:12]
    session_dir = TMP_DIR / session_id
    session_dir.mkdir(parents=True)

    try:
        docx_path = _save_upload(docx, session_dir, ALLOWED_DOCX)
        excel_paths = [_save_upload(f, session_dir, ALLOWED_EXCEL) for f in excels]
        reports, fill_plan, warnings = analyze(docx_path, excel_paths)
    except HTTPException:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(422, f"文件解析失败: {e}")

    _SESSIONS[session_id] = {
        "docx": docx_path,
        "docx_name": Path(docx.filename or "template.docx").stem,
        "fill_plan": fill_plan,
    }
    return AnalyzeResponse(session_id=session_id, tables=reports, warnings=warnings)


@router.post("/generate/{session_id}")
async def api_generate(session_id: str):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或已过期，请重新上传分析")

    out_path = session["docx"].parent / f"{session['docx_name']}_已填写.docx"
    try:
        fill_docx(session["docx"], session["fill_plan"], out_path)
    except Exception as e:
        raise HTTPException(500, f"生成失败: {e}")

    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=out_path.name,
    )
