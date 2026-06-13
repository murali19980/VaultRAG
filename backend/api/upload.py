from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
from backend.ingestion.indexer import run_ingestion
from backend.utils.file_utils import allowed_file

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...)
):
    """
    Accept multiple files, save them to a persistent uploads directory,
    and trigger the ingestion pipeline in the background.
    """
    saved_paths = []
    for file in files:
        if not file.filename:
            continue
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")
        
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        # Read content and save it
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        saved_paths.append(file_path)
    
    if not saved_paths:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Run ingestion in background to avoid blocking
    background_tasks.add_task(run_ingestion, input_files=saved_paths)
    return {
        "message": f"Uploaded {len(saved_paths)} file(s). Ingestion started in background.",
        "files": saved_paths
    }