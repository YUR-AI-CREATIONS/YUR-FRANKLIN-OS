"""
FILE UPLOAD API
Handles chunked file uploads up to 500MB
Stores files and makes them available for analysis
"""

import os
import uuid
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/upload", tags=["file-upload"])

# Upload directory
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max file size: 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {
    # Code
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.c', '.cpp', '.h',
    '.cs', '.rb', '.php', '.swift', '.kt', '.scala', '.r', '.sql', '.sh', '.bash',
    # Config
    '.json', '.yaml', '.yml', '.toml', '.ini', '.env', '.cfg', '.conf',
    # Docs
    '.md', '.txt', '.rst', '.html', '.css', '.xml', '.csv',
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',
    # Video
    '.mp4', '.webm', '.mov', '.avi',
    # Archives
    '.zip', '.tar', '.gz', '.rar',
    # Other
    '.pdf', '.dockerfile', '.gitignore', '.dockerignore',
}


class UploadedFile(BaseModel):
    file_id: str
    filename: str
    size: int
    content_type: str
    extension: str
    upload_path: str
    checksum: str
    uploaded_at: str


class UploadResponse(BaseModel):
    success: bool
    files: List[UploadedFile]
    total_size: int
    message: str


# In-memory store for uploaded files (per session)
uploaded_files_store = {}


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


@router.post("/files", response_model=UploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None)
):
    """
    Upload multiple files (up to 500MB each).
    Files are stored and available for analysis.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Create session directory
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded = []
    total_size = 0
    errors = []
    
    for file in files:
        try:
            # Check extension
            ext = get_file_extension(file.filename)
            if ext not in ALLOWED_EXTENSIONS and ext != '':
                errors.append(f"{file.filename}: Extension {ext} not allowed")
                continue
            
            # Generate file ID
            file_id = str(uuid.uuid4())[:8]
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Check size
            if file_size > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: Exceeds 500MB limit")
                continue
            
            # Save file
            file_path = session_dir / f"{file_id}_{file.filename}"
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Calculate checksum
            checksum = hashlib.sha256(content).hexdigest()
            
            # Create record
            file_record = UploadedFile(
                file_id=file_id,
                filename=file.filename,
                size=file_size,
                content_type=file.content_type or "application/octet-stream",
                extension=ext,
                upload_path=str(file_path),
                checksum=checksum,
                uploaded_at=datetime.now(timezone.utc).isoformat()
            )
            
            uploaded.append(file_record)
            total_size += file_size
            
            # Store in memory
            if session_id not in uploaded_files_store:
                uploaded_files_store[session_id] = []
            uploaded_files_store[session_id].append(file_record.dict())
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    message = f"Uploaded {len(uploaded)} file(s)"
    if errors:
        message += f". Errors: {'; '.join(errors)}"
    
    return UploadResponse(
        success=len(uploaded) > 0,
        files=uploaded,
        total_size=total_size,
        message=message
    )


@router.get("/files/{session_id}")
async def list_uploaded_files(session_id: str):
    """List all files uploaded in a session"""
    if session_id not in uploaded_files_store:
        return {"files": [], "count": 0}
    
    files = uploaded_files_store[session_id]
    return {
        "session_id": session_id,
        "files": files,
        "count": len(files),
        "total_size": sum(f["size"] for f in files)
    }


@router.get("/file/{session_id}/{file_id}")
async def get_file_content(session_id: str, file_id: str):
    """Get content of an uploaded file"""
    if session_id not in uploaded_files_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_record = None
    for f in uploaded_files_store[session_id]:
        if f["file_id"] == file_id:
            file_record = f
            break
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path(file_record["upload_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Read content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "file_id": file_id,
            "filename": file_record["filename"],
            "content": content,
            "size": file_record["size"],
            "content_type": "text"
        }
    except UnicodeDecodeError:
        # Binary file
        return {
            "file_id": file_id,
            "filename": file_record["filename"],
            "content": None,
            "size": file_record["size"],
            "content_type": "binary",
            "message": "Binary file - content not displayed"
        }


@router.delete("/files/{session_id}")
async def delete_session_files(session_id: str):
    """Delete all files in a session"""
    session_dir = UPLOAD_DIR / session_id
    
    if session_dir.exists():
        shutil.rmtree(session_dir)
    
    if session_id in uploaded_files_store:
        del uploaded_files_store[session_id]
    
    return {"success": True, "message": f"Session {session_id} deleted"}


@router.get("/health")
async def upload_health():
    """Check upload service health"""
    return {
        "status": "healthy",
        "upload_dir": str(UPLOAD_DIR),
        "exists": UPLOAD_DIR.exists(),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "allowed_extensions": len(ALLOWED_EXTENSIONS)
    }
