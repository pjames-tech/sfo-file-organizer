"""
Rule-based file classification engine for Smart File Organizer.

Provides keyword-based classification that takes priority over extension-based logic.
"""

from typing import Optional
from config import FILE_CATEGORIES

# Keyword rules: maps keywords (in filename) to categories
# These take priority over extension-based classification
KEYWORD_RULES: dict[str, str] = {
    # Document-related keywords
    "invoice": "Documents",
    "receipt": "Documents",
    "contract": "Documents",
    "report": "Documents",
    "resume": "Documents",
    "cv": "Documents",
    "letter": "Documents",
    "statement": "Documents",
    
    # Image-related keywords
    "screenshot": "Images",
    "photo": "Images",
    "wallpaper": "Images",
    "banner": "Images",
    "logo": "Images",
    "icon": "Images",
    
    # Video-related keywords
    "video": "Videos",
    "movie": "Videos",
    "clip": "Videos",
    "recording": "Videos",
    "tutorial": "Videos",
    
    # Audio-related keywords
    "song": "Audio",
    "music": "Audio",
    "podcast": "Audio",
    "audiobook": "Audio",
    
    # Archive-related keywords
    "backup": "Archives",
    "archive": "Archives",
    
    # Code-related keywords
    "script": "Code",
    "source": "Code",
    "config": "Code",
}


def classify_by_rules(filename: str) -> Optional[str]:
    """
    Classify a file based on keyword rules in the filename.
    
    This function checks if any known keywords appear in the filename
    (case-insensitive) and returns the corresponding category.
    
    Args:
        filename: The name of the file (with or without extension).
    
    Returns:
        Category name if a keyword match is found, None otherwise.
    
    Example:
        >>> classify_by_rules("invoice_2024.pdf")
        'Documents'
        >>> classify_by_rules("random_file.txt")
        None
    """
    filename_lower = filename.lower()
    
    for keyword, category in KEYWORD_RULES.items():
        if keyword in filename_lower:
            return category
    
    return None


def classify_by_extension(file_extension: str) -> str:
    """
    Classify a file based on its extension.
    
    Args:
        file_extension: The file extension (e.g., '.pdf', '.jpg').
    
    Returns:
        Category name or 'Other' if extension is not recognized.
    """
    ext = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def classify_file(filename: str, file_extension: str) -> str:
    """
    Classify a file using rules first, then fall back to extension.
    
    This is the main classification function that should be used.
    It first attempts keyword-based classification, and if no match
    is found, falls back to extension-based classification.
    
    Args:
        filename: The name of the file.
        file_extension: The file extension (e.g., '.pdf').
    
    Returns:
        The determined category for the file.
    
    Example:
        >>> classify_file("invoice.jpg", ".jpg")
        'Documents'  # Keyword 'invoice' takes priority
        >>> classify_file("vacation.jpg", ".jpg")
        'Images'  # No keyword match, uses extension
    """
    # Try keyword-based classification first
    category = classify_by_rules(filename)
    if category:
        return category
    
    # Fall back to extension-based classification
    return classify_by_extension(file_extension)
