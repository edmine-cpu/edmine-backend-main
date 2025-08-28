from typing import Dict, Any

PENDING_REQUESTS: Dict[str, Dict[str, Any]] = {}
EMAIL_VERIFICATION_CODES: Dict[str, str] = {}
MAX_FILES_COUNT = 10
ALLOWED_FILE_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml',
    'application/pdf', 'image/bmp', 'image/gif'
}
TEMP_FILES_DIR = 'static/tmp_files'
BID_FILES_DIR = 'static/bid_files'
DELETE_TOKEN_LENGTH = 32
