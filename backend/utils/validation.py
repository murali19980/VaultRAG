MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

def validate_file_size(content: bytes) -> bool:
    return len(content) <= MAX_UPLOAD_SIZE