# backend/app/utils/google_drive.py

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from backend.app.utils.google_auth import authenticate_google_drive
import io

def upload_file_to_drive(file_path: str, file_name: str):
    """
    Upload a file to Google Drive.
    """
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": file_name}
    media = MediaFileUpload(file_path, resumable=True)
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    return file.get("id")

def download_file_from_drive(file_id: str, output_path: str):
    """
    Download a file from Google Drive.
    """
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(output_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return output_path

def list_files_in_drive():
    """
    List files in Google Drive.
    """
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)

    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    return results.get("files", [])


def create_folder_in_drive(folder_name: str):
    """
    Create a folder in Google Drive and return its ID.
    """
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")