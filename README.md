# Smart File Organizer

A Python utility that automatically organizes files into categorized folders based on their file types, with support for rule-based classification, structured logging, and extensible AI integration.

## Features

- 📁 **Smart Classification** - Rule-based (keywords) + extension-based fallback
- ⚙️ **Customizable Categories** - Easy to add custom file categories and rules
- 🔄 **Duplicate Handling** - Automatic renaming for duplicate filenames
- 📊 **Statistics** - Summary report after organization
- 🧪 **Dry-Run Mode** - Preview changes without moving files
- 📝 **Structured Logging** - Console and file logging with configurable levels
- 🤖 **AI-Ready** - Placeholder for future AI-powered classification

## Architecture

```text
smart-file-organizer/
├── organizer.py        # Main CLI and orchestration
├── config.py           # Configuration and file categories
├── rules.py            # Rule-based classification engine
├── ai_classifier.py    # AI classification stub (future)
├── logging_config.py   # Logging configuration
├── requirements.txt    # Dependencies
└── tests/              # Unit tests
    ├── test_rules.py
    └── test_organizer.py
```

### Classification Priority

1. **AI Classification** (if enabled and available)
2. **Keyword Rules** - Matches keywords in filenames (e.g., "invoice" → Documents)
3. **Extension Fallback** - Uses file extension to determine category

## Installation

```bash
git clone https://github.com/yourusername/smart-file-organizer.git
cd smart-file-organizer
pip install -r requirements.txt
```

## Usage

### Interactive Mode (Default)

```bash
python organizer.py
```

You'll be prompted for source and destination directories.

### CLI Mode

```bash
# Basic usage with defaults
python organizer.py --source ~/Downloads --dest ~/Downloads/Organized

# Dry-run (preview without moving files)
python organizer.py --dry-run --source ~/Downloads

# Verbose logging
python organizer.py --log-level DEBUG --source ~/Downloads

# All options
python organizer.py --source ~/Downloads --dest ~/Organized --dry-run --log-level INFO
```

### CLI Options

| Flag            | Short | Description                                     |
| --------------- | ----- | ----------------------------------------------- |
| `--source`      | `-s`  | Source directory to organize                    |
| `--dest`        | `-d`  | Destination directory                           |
| `--dry-run`     | `-n`  | Preview changes without moving files            |
| `--log-level`   | `-l`  | Set logging level (DEBUG, INFO, WARNING, ERROR) |
| `--use-ai`      |       | Enable AI classification (requires setup)       |
| `--no-log-file` |       | Disable logging to file                         |

### Examples

```bash
# Preview what would happen
python organizer.py --dry-run --source ./messy_folder

# Organize with debug logging
python organizer.py -s ~/Downloads -d ~/Sorted -l DEBUG

# Quick organize current downloads
python organizer.py --source ~/Downloads
```

## Configuration

### File Categories (`config.py`)

```python
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ...],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ...],
    "Videos": [".mp4", ".mkv", ".avi", ...],
    # Add custom categories here
}
```

### Keyword Rules (`rules.py`)

```python
KEYWORD_RULES = {
    "invoice": "Documents",    # Files with "invoice" go to Documents
    "screenshot": "Images",    # Files with "screenshot" go to Images
    # Add custom rules here
}
```

## Testing

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_rules.py -v
```

## Roadmap

### Planned Features

- [ ] **AI Classification** - Integrate OpenAI/Gemini for smart categorization
- [ ] **Watch Mode** - Automatically organize new files as they appear
- [ ] **Undo Support** - Reverse the last organization operation
- [ ] **Custom Rules UI** - GUI for managing classification rules
- [ ] **Cloud Storage** - Support for S3, Google Drive, Dropbox

### AI Integration (Coming Soon)

The `ai_classifier.py` module provides a placeholder for AI-powered classification:

```python
# Future usage (not yet implemented)
python organizer.py --use-ai --source ~/Downloads
```

Planned AI features:

- **Content Analysis** - Classify based on file contents, not just names
- **Learning** - Adapt to user's organization patterns
- **Multi-modal** - Analyze images, documents, and other file types

## License

MIT License
