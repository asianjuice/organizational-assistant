# backend/app/routes/files.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.app.utils.google_drive import upload_file_to_drive, download_file_from_drive, list_files_in_drive, create_folder_in_drive
import os

# Create a router for file-related endpoints
router = APIRouter(prefix="/api/files", tags=["files"])

# Upload a file to Google Drive
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Upload the file to Google Drive
        file_id = upload_file_to_drive(file_path, file.filename)

        # Clean up the temporary file
        os.remove(file_path)

        return {"message": "File uploaded successfully", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Download a file from Google Drive
@router.get("/download/{file_id}")
async def download_file(file_id: str, output_path: str = "downloaded_file"):
    try:
        downloaded_path = download_file_from_drive(file_id, output_path)
        return {"message": "File downloaded successfully", "path": downloaded_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List files in Google Drive
@router.get("/list")
async def list_files():
    try:
        files = list_files_in_drive()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#file upload endpoint
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), folder_name: str = "Uncategorized"):
    """
    Upload a file to Google Drive and organize it in a folder.
    """
    try:
        # Create the folder if it doesn't exist
        folder_id = create_folder_in_drive(folder_name)

        # Save the file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Upload the file to the folder
        file_id = upload_file_to_drive(file_path, file.filename, folder_id)

        # Clean up the temporary file
        os.remove(file_path)

        return {"message": "File uploaded successfully", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))