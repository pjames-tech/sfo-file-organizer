"""
Configuration settings for Smart File Organizer.
"""

import os
from pathlib import Path

# Default directories (in-place organization by default)
DEFAULT_SOURCE_DIR = str(Path.home() / "Downloads")
DEFAULT_DEST_DIR = DEFAULT_SOURCE_DIR  # Same as source for in-place organizing

# File categories and their extensions
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml"],
    "Executables": [".exe", ".msi", ".bat", ".sh", ".app", ".dmg"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
}

# Logging settings
LOG_FILE = "organizer.log"
LOG_LEVEL = "INFO"
