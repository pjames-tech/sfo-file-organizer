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

### Quick Start

```bash
python organizer.py --source ~/Downloads
```

This organizes files **in-place** - category folders (Images, Documents, etc.) are created directly inside your Downloads folder.

### CLI Mode

```bash
# Organize Downloads folder (in-place)
python organizer.py --source ~/Downloads

# Dry-run (preview without moving files)
python organizer.py --dry-run --source ~/Downloads

# With AI classification
python organizer.py --use-ai --source ~/Downloads

# Undo last organization
python organizer.py --undo

# View history
python organizer.py --history
```

### CLI Options

| Flag            | Short | Description                                     |
| --------------- | ----- | ----------------------------------------------- |
| `--source`      | `-s`  | Source directory to organize                    |
| `--dest`        | `-d`  | Destination directory (default: same as source) |
| `--dry-run`     | `-n`  | Preview changes without moving files            |
| `--in-place`    | `-i`  | Organize within source folder (default)         |
| `--use-ai`      |       | Enable AI classification (requires Ollama)      |
| `--undo`        |       | Undo the last organization                      |
| `--history`     |       | Show organization history                       |
| `--ai-stats`    |       | Show AI learning statistics                     |
| `--log-level`   | `-l`  | Set logging level (DEBUG, INFO, WARNING, ERROR) |
| `--no-log-file` |       | Disable logging to file                         |

### Examples

```bash
# Preview what would happen
python organizer.py --dry-run --source ./messy_folder

# Organize with AI and debug logging
python organizer.py --use-ai -s ~/Downloads -l DEBUG

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

## AI Classification (Ollama)

The organizer supports **local AI classification** using [Ollama](https://ollama.ai/) - free, private, no API key needed.

### AI Features

- **Content Analysis** - Reads text files to classify based on contents
- **Learning System** - Remembers patterns from your classifications
- **Multi-modal Vision** - Analyzes images using llava model
- **Smart Fallback** - Uses filename when content isn't available

### Setup

1. **Install Ollama**: Download from [ollama.ai/download](https://ollama.ai/download)

2. **Pull models**:

   ```bash
   ollama pull llama3.2      # Required: text classification
   ollama pull llava         # Optional: image analysis
   ```

3. **Install Python dependency**:

   ```bash
   pip install requests
   ```

4. **Run with AI**:

   ```bash
   python organizer.py --use-ai --source ~/Downloads --dry-run
   ```

5. **Check learning stats**:

   ```bash
   python organizer.py --ai-stats
   ```

### How AI Classification Works

1. **Learned Patterns** - Checks if filename matches previously learned patterns
2. **Vision Analysis** - For images, uses llava to "see" what the image contains
3. **Content Analysis** - For text files, reads contents to understand the file
4. **Filename AI** - Falls back to classifying by filename with LLM

## Roadmap

### Completed Features

- [x] **AI Classification** - Local AI with Ollama ✅
- [x] **Content Analysis** - Classify based on file contents ✅
- [x] **Learning System** - Adapts to your patterns ✅
- [x] **Multi-modal Vision** - Analyze images with llava ✅
- [x] **Undo Support** - Reverse organization with `--undo` ✅
- [x] **Custom Rules UI** - Web GUI for managing rules ✅

### Planned Features

- [ ] **Watch Mode** - Automatically organize new files as they appear
- [ ] **Cloud Storage** - Support for S3, Google Drive, Dropbox

## License

MIT License
