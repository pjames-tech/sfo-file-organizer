"""
AI-based file classification module for Smart File Organizer.

Features:
- Local AI classification using Ollama
- Content analysis for text-based files
- Multi-modal vision for images
- Learning from user patterns

Setup:
    1. Install Ollama: https://ollama.ai/download
    2. Pull models: 
       ollama pull llama3.2      # For text classification
       ollama pull llava         # For image analysis (optional)
    3. Run with: python organizer.py --use-ai --source ~/Downloads
"""

import logging
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger("smart_file_organizer")

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"
OLLAMA_VISION_MODEL = "llava"  # For image analysis

# Learning data file
LEARNING_DATA_FILE = Path(__file__).parent / "learning_data.json"

# Valid categories for classification
VALID_CATEGORIES = [
    "Images", "Documents", "Videos", "Audio", 
    "Archives", "Code", "Executables", "Fonts", "Other"
]

# File extensions that support content reading
TEXT_EXTENSIONS = {".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv", ".log"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

CLASSIFICATION_PROMPT = """Classify this file into exactly ONE category based on its filename.

Categories:
- Images: photos, graphics, screenshots, icons, wallpapers, logos, banners (jpg, png, gif, svg, webp, ico, bmp)
- Documents: PDFs, Word docs, spreadsheets, presentations, text files, invoices, receipts, contracts, reports (pdf, doc, docx, txt, xls, xlsx, ppt)
- Videos: movies, clips, recordings, tutorials, screen recordings (mp4, mkv, avi, mov, webm)
- Audio: music, songs, podcasts, voice memos, sound effects (mp3, wav, flac, m4a, ogg)
- Archives: zip files, compressed files, backups, tarballs (zip, rar, 7z, tar, gz)
- Code: source code, scripts, config files, markup (py, js, html, css, json, xml, java, cpp)
- Executables: programs, installers, apps, batch files (exe, msi, dmg, app, bat, sh)
- Fonts: font files (ttf, otf, woff, woff2)
- Other: anything that doesn't fit above

Examples:
- "vacation_photo.jpg" → Images
- "invoice_2024.pdf" → Documents
- "react_app.zip" → Archives (it's compressed)
- "background_music.mp3" → Audio
- "setup.exe" → Executables
- "WhatsApp Image 2024.jpeg" → Images
- "VID-20240101-WA0001.mp4" → Videos
- "resume_john_doe.docx" → Documents
- "script.py" → Code

IMPORTANT: Respond with ONLY the category name, nothing else. No explanations.

Filename: {filename}
Category:"""

CONTENT_CLASSIFICATION_PROMPT = """Classify this file based on its filename AND contents.

Categories:
- Images: photos, graphics, screenshots
- Documents: text documents, reports, invoices, receipts, contracts
- Videos: video files, recordings
- Audio: music, podcasts, sound files
- Archives: compressed/zip files, backups
- Code: source code, scripts, config files
- Executables: programs, installers
- Fonts: font files
- Other: anything else

Filename: {filename}

File Contents (first 500 chars):
{content}

Based on the filename and contents, what category does this belong to?
Respond with ONLY the category name, nothing else.

Category:"""

IMAGE_CLASSIFICATION_PROMPT = """Analyze this image and classify it.

If it shows:
- A photo, artwork, graphic, screenshot, icon, or design → respond "Images"
- A scanned document, receipt, invoice, text-heavy image → respond "Documents"
- Something else → respond "Other"

Respond with ONLY one word: Images, Documents, or Other."""


# ============================================================================
# LEARNING SYSTEM
# ============================================================================

def load_learning_data() -> dict:
    """Load learning data from JSON file."""
    if LEARNING_DATA_FILE.exists():
        try:
            with open(LEARNING_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load learning data: {e}")
    return {"patterns": {}, "corrections": [], "stats": {"total": 0, "correct": 0}}


def save_learning_data(data: dict) -> None:
    """Save learning data to JSON file."""
    try:
        with open(LEARNING_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save learning data: {e}")


def learn_pattern(filename: str, category: str) -> None:
    """
    Learn from a classification to improve future predictions.
    
    Args:
        filename: The filename that was classified.
        category: The category it was classified as.
    """
    data = load_learning_data()
    
    # Extract keywords from filename
    keywords = extract_keywords(filename)
    
    for keyword in keywords:
        if keyword not in data["patterns"]:
            data["patterns"][keyword] = {}
        if category not in data["patterns"][keyword]:
            data["patterns"][keyword][category] = 0
        data["patterns"][keyword][category] += 1
    
    data["stats"]["total"] += 1
    save_learning_data(data)
    logger.debug(f"Learned pattern: {filename} -> {category}")


def get_learned_category(filename: str) -> Optional[str]:
    """
    Get category based on learned patterns.
    
    Args:
        filename: The filename to classify.
    
    Returns:
        Category if a strong pattern exists, None otherwise.
    """
    data = load_learning_data()
    keywords = extract_keywords(filename)
    
    category_scores = {}
    
    for keyword in keywords:
        if keyword in data["patterns"]:
            for cat, count in data["patterns"][keyword].items():
                if cat not in category_scores:
                    category_scores[cat] = 0
                category_scores[cat] += count
    
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] >= 3:  # Minimum confidence threshold
            logger.debug(f"Learned pattern matched: {filename} -> {best_category}")
            return best_category
    
    return None


def extract_keywords(filename: str) -> list:
    """Extract meaningful keywords from a filename."""
    import re
    # Remove extension and split by common separators
    name = Path(filename).stem.lower()
    keywords = re.split(r'[-_\s.]+', name)
    # Filter out short words and numbers
    return [k for k in keywords if len(k) >= 3 and not k.isdigit()]


def record_correction(filename: str, ai_category: str, correct_category: str) -> None:
    """
    Record when user corrects an AI classification.
    
    Args:
        filename: The misclassified filename.
        ai_category: What AI predicted.
        correct_category: What user specified.
    """
    data = load_learning_data()
    data["corrections"].append({
        "filename": filename,
        "predicted": ai_category,
        "correct": correct_category,
        "timestamp": datetime.now().isoformat()
    })
    save_learning_data(data)
    
    # Also learn the correct pattern
    learn_pattern(filename, correct_category)


# ============================================================================
# CONTENT ANALYSIS
# ============================================================================

def read_file_content(file_path: str, max_chars: int = 500) -> Optional[str]:
    """
    Read the beginning of a text file for content analysis.
    
    Args:
        file_path: Path to the file.
        max_chars: Maximum characters to read.
    
    Returns:
        File content string or None if unreadable.
    """
    path = Path(file_path)
    
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return None
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
            return content.strip() if content else None
    except Exception as e:
        logger.debug(f"Could not read file content: {e}")
        return None


def classify_with_content(filename: str, file_path: str) -> Optional[str]:
    """
    Classify a file by analyzing its contents.
    
    Args:
        filename: The name of the file.
        file_path: Full path to the file.
    
    Returns:
        Category name or None if content analysis fails.
    """
    content = read_file_content(file_path)
    
    if not content:
        return None
    
    if not REQUESTS_AVAILABLE or not is_ai_available():
        return None
    
    try:
        prompt = CONTENT_CLASSIFICATION_PROMPT.format(
            filename=filename,
            content=content[:500]
        )
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 20}
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            category = result.get("response", "").strip()
            
            for valid_cat in VALID_CATEGORIES:
                if valid_cat.lower() in category.lower():
                    logger.info(f"Content analysis classified '{filename}' as '{valid_cat}'")
                    return valid_cat
        
        return None
        
    except Exception as e:
        logger.debug(f"Content analysis failed: {e}")
        return None


# ============================================================================
# MULTI-MODAL VISION
# ============================================================================

def is_vision_available() -> bool:
    """Check if vision model (llava) is available."""
    if not REQUESTS_AVAILABLE:
        return False
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            return OLLAMA_VISION_MODEL in model_names
        return False
    except Exception:
        return False


def classify_image_with_vision(file_path: str) -> Optional[str]:
    """
    Classify an image using vision model.
    
    Args:
        file_path: Path to the image file.
    
    Returns:
        Category name or None if vision analysis fails.
    """
    path = Path(file_path)
    
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        return None
    
    if not is_vision_available():
        logger.debug("Vision model not available. Install with: ollama pull llava")
        return None
    
    try:
        import base64
        
        # Read and encode image
        with open(path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": OLLAMA_VISION_MODEL,
                "messages": [{
                    "role": "user",
                    "content": IMAGE_CLASSIFICATION_PROMPT,
                    "images": [image_data]
                }],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 20}
            },
            timeout=30  # Vision takes longer
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("message", {})
            category = message.get("content", "").strip()
            
            for valid_cat in VALID_CATEGORIES:
                if valid_cat.lower() in category.lower():
                    logger.info(f"Vision classified '{path.name}' as '{valid_cat}'")
                    return valid_cat
        
        return None
        
    except Exception as e:
        logger.debug(f"Vision analysis failed: {e}")
        return None


# ============================================================================
# MAIN CLASSIFICATION
# ============================================================================

def classify_with_ai(
    filename: str,
    file_extension: str,
    file_path: Optional[str] = None
) -> Optional[str]:
    """
    Classify a file using AI with multiple strategies.
    
    Classification priority:
    1. Learned patterns from user history
    2. Multi-modal vision (for images)
    3. Content analysis (for text files)
    4. Filename-based AI classification
    
    Args:
        filename: The name of the file to classify.
        file_extension: The file extension (e.g., '.pdf').
        file_path: Optional full path to the file for content/vision analysis.
    
    Returns:
        Category name if AI classification succeeds, None otherwise.
    """
    # 1. Check learned patterns first
    learned = get_learned_category(filename)
    if learned:
        return learned
    
    # 2. Try vision for images
    if file_path and file_extension.lower() in IMAGE_EXTENSIONS:
        vision_result = classify_image_with_vision(file_path)
        if vision_result:
            learn_pattern(filename, vision_result)
            return vision_result
    
    # 3. Try content analysis for text files
    if file_path and file_extension.lower() in TEXT_EXTENSIONS:
        content_result = classify_with_content(filename, file_path)
        if content_result:
            learn_pattern(filename, content_result)
            return content_result
    
    # 4. Fall back to filename-based classification
    if not REQUESTS_AVAILABLE:
        logger.warning("requests library not installed. Install with: pip install requests")
        return None
    
    if not is_ai_available():
        return None
    
    try:
        prompt = CLASSIFICATION_PROMPT.format(filename=filename)
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 20}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            category = result.get("response", "").strip()
            
            for valid_cat in VALID_CATEGORIES:
                if valid_cat.lower() in category.lower():
                    logger.debug(f"AI classified '{filename}' as '{valid_cat}'")
                    learn_pattern(filename, valid_cat)
                    return valid_cat
            
            logger.warning(f"AI returned invalid category '{category}' for '{filename}'")
            return None
        else:
            logger.warning(f"Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        logger.warning("Cannot connect to Ollama. Is it running? Start with: ollama serve")
        return None
    except requests.exceptions.Timeout:
        logger.warning("Ollama request timed out")
        return None
    except Exception as e:
        logger.error(f"AI classification error: {e}")
        return None


def is_ai_available() -> bool:
    """
    Check if Ollama is available and running.
    
    Returns:
        True if Ollama is accessible, False otherwise.
    """
    if not REQUESTS_AVAILABLE:
        return False
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            if OLLAMA_MODEL in model_names or f"{OLLAMA_MODEL}:latest" in [m.get("name", "") for m in models]:
                return True
            else:
                logger.warning(f"Model '{OLLAMA_MODEL}' not found. Pull it with: ollama pull {OLLAMA_MODEL}")
                return False
        return False
    except Exception:
        return False


def get_ai_confidence(filename: str) -> float:
    """
    Get the confidence score for AI classification.
    
    Args:
        filename: The name of the file.
    
    Returns:
        Confidence score between 0.0 and 1.0.
    """
    # Check if we have learned patterns
    data = load_learning_data()
    keywords = extract_keywords(filename)
    
    max_count = 0
    for keyword in keywords:
        if keyword in data["patterns"]:
            for count in data["patterns"][keyword].values():
                max_count = max(max_count, count)
    
    if max_count >= 10:
        return 0.95
    elif max_count >= 5:
        return 0.85
    elif max_count >= 3:
        return 0.75
    elif is_ai_available():
        return 0.7
    return 0.0


def set_model(model_name: str) -> None:
    """
    Change the Ollama model used for classification.
    
    Args:
        model_name: Name of the model (e.g., 'llama3.2', 'mistral', 'gemma2')
    """
    global OLLAMA_MODEL
    OLLAMA_MODEL = model_name
    logger.info(f"AI model set to: {model_name}")


def get_learning_stats() -> dict:
    """Get statistics about learned patterns."""
    data = load_learning_data()
    return {
        "total_classifications": data["stats"]["total"],
        "unique_patterns": len(data["patterns"]),
        "corrections": len(data["corrections"])
    }
