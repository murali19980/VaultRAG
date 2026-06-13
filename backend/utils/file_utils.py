import os

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".xlsx", ".csv", ".md"}

def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def save_upload_file(upload_file, destination: str) -> str:
    with open(destination, "wb") as f:
        f.write(upload_file.file.read())
    return destination