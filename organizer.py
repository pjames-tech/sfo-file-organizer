"""
Smart File Organizer
Automatically organizes files in a directory based on their types.

Features:
- Rule-based classification (keywords take priority)
- Extension-based fallback classification
- Structured logging with configurable levels
- Dry-run mode for safe previewing
- CLI with backward-compatible interactive mode
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Optional

from config import FILE_CATEGORIES, DEFAULT_SOURCE_DIR, DEFAULT_DEST_DIR
from logging_config import setup_logging, get_logger
from rules import classify_file, classify_by_rules
from ai_classifier import classify_with_ai, is_ai_available
from history import start_session, record_movement, save_session, undo_last_session, get_history_summary


def get_category(file_extension: str) -> str:
    """
    Determine the category of a file based on its extension.
    
    Args:
        file_extension: The file extension (e.g., '.pdf', '.jpg')
    
    Returns:
        The category name or 'Other' if not found.
    
    Note:
        This function is preserved for backward compatibility.
        For new code, use classify_file() from rules.py instead.
    """
    ext = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def organize_files(
    source_dir: Optional[str] = None,
    dest_dir: Optional[str] = None,
    dry_run: bool = False,
    use_ai: bool = False
) -> dict:
    """
    Organize files from source directory into categorized folders.
    
    Args:
        source_dir: Directory containing files to organize.
        dest_dir: Directory where organized folders will be created.
        dry_run: If True, only log actions without moving files.
        use_ai: If True, attempt AI classification (requires API setup).
    
    Returns:
        Dictionary with statistics about organized files:
        - moved: Number of files successfully moved
        - skipped: Number of directories skipped
        - errors: Number of errors encountered
    
    Raises:
        FileNotFoundError: If source directory does not exist.
        PermissionError: If lacking permissions to read source or write dest.
    """
    logger = get_logger()
    
    source = Path(source_dir or DEFAULT_SOURCE_DIR)
    destination = Path(dest_dir or DEFAULT_DEST_DIR)
    
    # Validate source directory
    if not source.exists():
        logger.error(f"Source directory not found: {source}")
        raise FileNotFoundError(f"Source directory not found: {source}")
    
    if not source.is_dir():
        logger.error(f"Source path is not a directory: {source}")
        raise NotADirectoryError(f"Source path is not a directory: {source}")
    
    # Check read permissions
    if not os.access(source, os.R_OK):
        logger.error(f"Permission denied: Cannot read from {source}")
        raise PermissionError(f"Permission denied: Cannot read from {source}")
    
    stats = {"moved": 0, "skipped": 0, "errors": 0}
    
    # Start a session for undo support
    session = start_session(str(source), str(destination), dry_run)
    
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Organizing files from: {source}")
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Destination: {destination}")
    
    for file_path in source.iterdir():
        if file_path.is_file():
            try:
                # Determine category using the classification chain
                category = None
                
                # 1. Try AI classification if enabled
                if use_ai and is_ai_available():
                    category = classify_with_ai(file_path.name, file_path.suffix, str(file_path))
                    if category:
                        logger.debug(f"AI classified {file_path.name} as {category}")
                
                # 2. Fall back to rule-based + extension classification
                if not category:
                    category = classify_file(file_path.name, file_path.suffix)
                    rule_match = classify_by_rules(file_path.name)
                    if rule_match:
                        logger.debug(f"Rule matched {file_path.name} -> {category}")
                    else:
                        logger.debug(f"Extension matched {file_path.name} -> {category}")
                
                category_dir = destination / category
                
                if not dry_run:
                    category_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = category_dir / file_path.name
                
                # Handle duplicate filenames
                if dest_path.exists() or (not dry_run and dest_path.exists()):
                    base = file_path.stem
                    ext = file_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = category_dir / f"{base}_{counter}{ext}"
                        counter += 1
                    logger.warning(f"Duplicate found, renaming to: {dest_path.name}")
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {file_path.name} -> {category}/")
                else:
                    # Record the movement before moving
                    original_path = str(file_path)
                    shutil.move(str(file_path), str(dest_path))
                    record_movement(session, original_path, str(dest_path))
                    logger.info(f"Moved: {file_path.name} -> {category}/")
                
                stats["moved"] += 1
                
            except PermissionError as e:
                logger.error(f"Permission denied for {file_path.name}: {e}")
                stats["errors"] += 1
            except OSError as e:
                logger.error(f"OS error moving {file_path.name}: {e}")
                stats["errors"] += 1
            except Exception as e:
                logger.error(f"Unexpected error moving {file_path.name}: {e}")
                stats["errors"] += 1
        else:
            logger.debug(f"Skipped directory: {file_path.name}")
            stats["skipped"] += 1
    
    # Save session for undo support
    save_session(session)
    
    return stats


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Smart File Organizer - Automatically organize files by type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python organizer.py                           # Interactive mode
  python organizer.py --source ~/Downloads      # Specify source
  python organizer.py --dry-run                 # Preview without moving
  python organizer.py --log-level DEBUG         # Verbose logging
        """
    )
    
    parser.add_argument(
        "--source", "-s",
        type=str,
        default=None,
        help=f"Source directory to organize (default: {DEFAULT_SOURCE_DIR})"
    )
    
    parser.add_argument(
        "--dest", "-d",
        type=str,
        default=None,
        help=f"Destination directory for organized files (default: {DEFAULT_DEST_DIR})"
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview changes without actually moving files"
    )
    
    parser.add_argument(
        "--in-place", "-i",
        action="store_true",
        help="Organize files within the source folder (creates subfolders in source)"
    )
    
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Enable AI-powered classification (requires API setup)"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--no-log-file",
        action="store_true",
        help="Disable logging to file"
    )
    
    parser.add_argument(
        "--ai-stats",
        action="store_true",
        help="Show AI learning statistics and exit"
    )
    
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the last organization operation"
    )
    
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show organization history and exit"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the file organizer.
    
    Returns:
        Exit code (0 for success, 1 for errors).
    """
    args = parse_args()
    
    # Setup logging
    log_file = None if args.no_log_file else "organizer.log"
    setup_logging(level=args.log_level, log_file=log_file)
    logger = get_logger()
    
    print("=" * 50)
    print("Smart File Organizer")
    print("=" * 50)
    
    # Handle --ai-stats flag
    if args.ai_stats:
        from ai_classifier import get_learning_stats
        stats = get_learning_stats()
        print("\nAI Learning Statistics:")
        print(f"  Total classifications: {stats['total_classifications']}")
        print(f"  Unique patterns learned: {stats['unique_patterns']}")
        print(f"  User corrections: {stats['corrections']}")
        print("=" * 50)
        return 0
    
    # Handle --undo flag
    if args.undo:
        print("\nUndoing last organization...")
        result = undo_last_session()
        if result["success"]:
            print(f"\n✅ Restored {result['restored']} files")
            if result["errors"] > 0:
                print(f"⚠️  {result['errors']} files could not be restored")
        else:
            print(f"\n❌ {result['message']}")
        print("=" * 50)
        return 0 if result.get("success", False) else 1
    
    # Handle --history flag
    if args.history:
        history = get_history_summary()
        if not history:
            print("\nNo organization history found.")
        else:
            print("\nOrganization History:")
            print("-" * 50)
            for i, session in enumerate(reversed(history), 1):
                status = "✓" if not session["undone"] else "↩ (undone)"
                dry = " [dry-run]" if session["dry_run"] else ""
                print(f"{i}. {session['timestamp'][:16]} - {session['files_moved']} files {status}{dry}")
            print("-" * 50)
        print("=" * 50)
        return 0
    
    # Use CLI args or fall back to interactive prompts (backward compatibility)
    source = args.source
    dest = args.dest
    
    # Handle --in-place flag (organize within source folder)
    if args.in_place:
        if source is None:
            source = DEFAULT_SOURCE_DIR
        dest = source  # Set destination to same as source
        print(f"[IN-PLACE MODE] Organizing within: {source}")
    
    if source is None and dest is None and not args.dry_run and not args.in_place:
        # Interactive mode - maintain backward compatibility
        source = input(f"Source directory [{DEFAULT_SOURCE_DIR}]: ").strip() or None
        dest = input(f"Destination directory [{DEFAULT_DEST_DIR}]: ").strip() or None
    
    if args.dry_run:
        print("\n[DRY RUN MODE] No files will be moved.\n")
    
    if args.use_ai:
        if is_ai_available():
            print("AI classification: ENABLED")
        else:
            logger.warning("AI classification requested but not available. Using rules only.")
            print("AI classification: NOT AVAILABLE (using rules only)")
    
    print("\nOrganizing files...")
    
    try:
        stats = organize_files(
            source_dir=source,
            dest_dir=dest,
            dry_run=args.dry_run,
            use_ai=args.use_ai
        )
        
        print("\n" + "=" * 50)
        print("Summary:")
        print(f"  Files {'to move' if args.dry_run else 'moved'}: {stats['moved']}")
        print(f"  Skipped (directories): {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        print("=" * 50)
        
        return 0 if stats["errors"] == 0 else 1
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please check that the source directory exists and try again.")
        return 1
    except PermissionError as e:
        print(f"\n❌ Error: {e}")
        print("Please check your permissions and try again.")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
