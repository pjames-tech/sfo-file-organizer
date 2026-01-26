"""
Smart File Organizer - Desktop GUI

A user-friendly graphical interface for the Smart File Organizer.
Designed for both technical and non-technical users.

Run with: python gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_SOURCE_DIR, FILE_CATEGORIES
from organizer import organize_files
from history import undo_last_session, get_history_summary, get_last_session


class ModernStyle:
    """Modern dark theme colors matching the web UI."""
    
    BG_PRIMARY = "#0d1117"
    BG_SECONDARY = "#161b22"
    BG_TERTIARY = "#21262d"
    TEXT_PRIMARY = "#f0f6fc"
    TEXT_SECONDARY = "#8b949e"
    ACCENT = "#58a6ff"
    ACCENT_HOVER = "#79b8ff"
    SUCCESS = "#3fb950"
    DANGER = "#f85149"
    WARNING = "#d29922"
    BORDER = "#30363d"


class SmartFileOrganizerGUI:
    """Main GUI application class."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Configure dark theme
        self.setup_theme()
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # State
        self.source_dir = tk.StringVar(value=DEFAULT_SOURCE_DIR)
        self.use_ai = tk.BooleanVar(value=False)
        self.is_running = False
        
        # Build UI
        self.create_widgets()
        
        # Start message processing
        self.process_messages()
    
    def setup_theme(self):
        """Configure the dark theme for ttk widgets."""
        style = ttk.Style()
        
        # Use clam theme as base (works well for customization)
        style.theme_use('clam')
        
        # Configure colors
        style.configure(".",
            background=ModernStyle.BG_PRIMARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            fieldbackground=ModernStyle.BG_TERTIARY,
            troughcolor=ModernStyle.BG_TERTIARY,
            bordercolor=ModernStyle.BORDER,
            lightcolor=ModernStyle.BG_TERTIARY,
            darkcolor=ModernStyle.BG_PRIMARY
        )
        
        # Frame styles
        style.configure("TFrame", background=ModernStyle.BG_PRIMARY)
        style.configure("Card.TFrame", background=ModernStyle.BG_SECONDARY)
        
        # Label styles
        style.configure("TLabel",
            background=ModernStyle.BG_PRIMARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            font=("Segoe UI", 10)
        )
        style.configure("Header.TLabel",
            font=("Segoe UI", 24, "bold"),
            foreground=ModernStyle.ACCENT
        )
        style.configure("Subtitle.TLabel",
            font=("Segoe UI", 11),
            foreground=ModernStyle.TEXT_SECONDARY
        )
        style.configure("Section.TLabel",
            font=("Segoe UI", 12, "bold"),
            foreground=ModernStyle.TEXT_PRIMARY
        )
        style.configure("Card.TLabel",
            background=ModernStyle.BG_SECONDARY
        )
        
        # Button styles
        style.configure("TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(20, 10)
        )
        style.configure("Primary.TButton",
            background=ModernStyle.ACCENT,
            foreground=ModernStyle.BG_PRIMARY
        )
        style.map("Primary.TButton",
            background=[("active", ModernStyle.ACCENT_HOVER), ("pressed", ModernStyle.ACCENT)],
            foreground=[("active", ModernStyle.BG_PRIMARY)]
        )
        style.configure("Success.TButton",
            background=ModernStyle.SUCCESS,
            foreground="white"
        )
        style.map("Success.TButton",
            background=[("active", "#4cc65c"), ("pressed", ModernStyle.SUCCESS)]
        )
        style.configure("Warning.TButton",
            background=ModernStyle.WARNING,
            foreground=ModernStyle.BG_PRIMARY
        )
        style.map("Warning.TButton",
            background=[("active", "#e0a82e"), ("pressed", ModernStyle.WARNING)]
        )
        style.configure("Danger.TButton",
            background=ModernStyle.DANGER,
            foreground="white"
        )
        style.map("Danger.TButton",
            background=[("active", "#ff6b63"), ("pressed", ModernStyle.DANGER)]
        )
        
        # Entry styles
        style.configure("TEntry",
            fieldbackground=ModernStyle.BG_TERTIARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            insertcolor=ModernStyle.TEXT_PRIMARY,
            padding=10
        )
        
        # Checkbutton styles
        style.configure("TCheckbutton",
            background=ModernStyle.BG_PRIMARY,
            foreground=ModernStyle.TEXT_PRIMARY
        )
        style.configure("Card.TCheckbutton",
            background=ModernStyle.BG_SECONDARY
        )
        
        # Progress bar
        style.configure("TProgressbar",
            troughcolor=ModernStyle.BG_TERTIARY,
            background=ModernStyle.SUCCESS,
            bordercolor=ModernStyle.BORDER,
            lightcolor=ModernStyle.SUCCESS,
            darkcolor=ModernStyle.SUCCESS
        )
        
        # Root window background
        self.root.configure(bg=ModernStyle.BG_PRIMARY)
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Folder selection card
        self.create_folder_section(main_frame)
        
        # Action buttons card
        self.create_actions_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Log section
        self.create_log_section(main_frame)
    
    def create_header(self, parent):
        """Create the header section."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title = ttk.Label(header_frame, text="📁 Smart File Organizer", style="Header.TLabel")
        title.pack()
        
        # Subtitle
        subtitle = ttk.Label(
            header_frame,
            text="Automatically organize your files into categorized folders",
            style="Subtitle.TLabel"
        )
        subtitle.pack()
    
    def create_folder_section(self, parent):
        """Create the folder selection section."""
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Section title
        ttk.Label(card, text="📂 Source Folder", style="Section.TLabel").pack(anchor=tk.W)
        ttk.Label(
            card,
            text="Select the folder you want to organize",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Folder input row
        input_frame = ttk.Frame(card, style="Card.TFrame")
        input_frame.pack(fill=tk.X)
        
        self.folder_entry = ttk.Entry(
            input_frame,
            textvariable=self.source_dir,
            font=("Segoe UI", 10)
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            input_frame,
            text="Browse...",
            command=self.browse_folder,
            style="Primary.TButton"
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Options frame
        options_frame = ttk.Frame(card, style="Card.TFrame")
        options_frame.pack(fill=tk.X, pady=(15, 0))
        
        # AI toggle
        ai_check = ttk.Checkbutton(
            options_frame,
            text="🤖 Use AI Classification (requires Ollama)",
            variable=self.use_ai,
            style="Card.TCheckbutton"
        )
        ai_check.pack(side=tk.LEFT)
    
    def create_actions_section(self, parent):
        """Create the action buttons section."""
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Section title
        ttk.Label(card, text="⚡ Actions", style="Section.TLabel").pack(anchor=tk.W)
        ttk.Label(
            card,
            text="Choose an action to perform",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons row
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)
        
        # Organize button
        self.organize_btn = ttk.Button(
            btn_frame,
            text="🚀 Organize Now",
            command=self.start_organize,
            style="Success.TButton"
        )
        self.organize_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Preview button
        self.preview_btn = ttk.Button(
            btn_frame,
            text="👁️ Preview Changes",
            command=self.start_preview,
            style="Primary.TButton"
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Undo button
        self.undo_btn = ttk.Button(
            btn_frame,
            text="↩️ Undo Last",
            command=self.start_undo,
            style="Warning.TButton"
        )
        self.undo_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # History button
        self.history_btn = ttk.Button(
            btn_frame,
            text="📜 History",
            command=self.show_history,
            style="TButton"
        )
        self.history_btn.pack(side=tk.LEFT)
    
    def create_progress_section(self, parent):
        """Create the progress bar section."""
        self.progress_frame = ttk.Frame(parent)
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Progress bar (hidden initially)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=400
        )
        
        # Status label
        self.status_label = ttk.Label(
            self.progress_frame,
            text="",
            style="Subtitle.TLabel"
        )
    
    def create_log_section(self, parent):
        """Create the log output section."""
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Section title with clear button
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill=tk.X)
        
        ttk.Label(header, text="📋 Activity Log", style="Section.TLabel").pack(side=tk.LEFT)
        
        clear_btn = ttk.Button(
            header,
            text="Clear",
            command=self.clear_log,
            style="TButton"
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # Log text area with scrollbar
        log_frame = ttk.Frame(card, style="Card.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            selectbackground=ModernStyle.ACCENT,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.log_text.tag_configure("info", foreground=ModernStyle.TEXT_PRIMARY)
        self.log_text.tag_configure("success", foreground=ModernStyle.SUCCESS)
        self.log_text.tag_configure("warning", foreground=ModernStyle.WARNING)
        self.log_text.tag_configure("error", foreground=ModernStyle.DANGER)
        self.log_text.tag_configure("header", foreground=ModernStyle.ACCENT, font=("Consolas", 9, "bold"))
        
        # Welcome message
        self.log("Welcome to Smart File Organizer!", "header")
        self.log(f"Default source folder: {DEFAULT_SOURCE_DIR}", "info")
        self.log("Select a folder and click 'Organize Now' to start.\n", "info")
    
    def browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            initialdir=self.source_dir.get(),
            title="Select folder to organize"
        )
        if folder:
            self.source_dir.set(folder)
            self.log(f"Selected folder: {folder}", "info")
    
    def log(self, message, tag="info"):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log output."""
        self.log_text.delete(1.0, tk.END)
    
    def set_running(self, running):
        """Set the running state and update UI accordingly."""
        self.is_running = running
        state = tk.DISABLED if running else tk.NORMAL
        
        self.organize_btn.configure(state=state)
        self.preview_btn.configure(state=state)
        self.undo_btn.configure(state=state)
        self.history_btn.configure(state=state)
        
        if running:
            self.progress_bar.pack(fill=tk.X)
            self.status_label.pack(anchor=tk.W, pady=(5, 0))
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.status_label.pack_forget()
    
    def start_organize(self):
        """Start the organization process."""
        source = self.source_dir.get()
        
        if not Path(source).exists():
            messagebox.showerror("Error", f"Folder not found: {source}")
            return
        
        self.log(f"\n{'='*50}", "header")
        self.log("Starting file organization...", "header")
        self.log(f"Source: {source}", "info")
        self.log(f"AI Mode: {'Enabled' if self.use_ai.get() else 'Disabled'}", "info")
        
        self.set_running(True)
        self.status_label.configure(text="Organizing files...")
        
        # Run in thread
        thread = threading.Thread(
            target=self._run_organize,
            args=(source, False),
            daemon=True
        )
        thread.start()
    
    def start_preview(self):
        """Start the preview (dry-run) process."""
        source = self.source_dir.get()
        
        if not Path(source).exists():
            messagebox.showerror("Error", f"Folder not found: {source}")
            return
        
        self.log(f"\n{'='*50}", "header")
        self.log("Previewing changes (dry run)...", "header")
        self.log(f"Source: {source}", "info")
        
        self.set_running(True)
        self.status_label.configure(text="Analyzing files...")
        
        # Run in thread
        thread = threading.Thread(
            target=self._run_organize,
            args=(source, True),
            daemon=True
        )
        thread.start()
    
    def _run_organize(self, source, dry_run):
        """Run organization in a separate thread."""
        try:
            stats = organize_files(
                source_dir=source,
                dest_dir=source,  # In-place organization
                dry_run=dry_run,
                use_ai=self.use_ai.get()
            )
            
            self.message_queue.put(("organize_complete", stats, dry_run))
            
        except Exception as e:
            self.message_queue.put(("error", str(e), None))
    
    def start_undo(self):
        """Start the undo process."""
        last_session = get_last_session()
        
        if not last_session:
            messagebox.showinfo("No History", "No organization sessions to undo.")
            return
        
        # Confirm undo
        files_count = len(last_session.get("movements", []))
        timestamp = last_session.get("timestamp", "Unknown")
        
        if not messagebox.askyesno(
            "Confirm Undo",
            f"Undo the last organization?\n\n"
            f"Session: {timestamp}\n"
            f"Files to restore: {files_count}"
        ):
            return
        
        self.log(f"\n{'='*50}", "header")
        self.log("Undoing last organization...", "header")
        
        self.set_running(True)
        self.status_label.configure(text="Restoring files...")
        
        # Run in thread
        thread = threading.Thread(target=self._run_undo, daemon=True)
        thread.start()
    
    def _run_undo(self):
        """Run undo in a separate thread."""
        try:
            stats = undo_last_session()
            self.message_queue.put(("undo_complete", stats, None))
        except Exception as e:
            self.message_queue.put(("error", str(e), None))
    
    def show_history(self):
        """Show the history dialog."""
        history = get_history_summary()
        
        if not history:
            messagebox.showinfo("History", "No organization history found.")
            return
        
        # Create history window
        history_win = tk.Toplevel(self.root)
        history_win.title("Organization History")
        history_win.geometry("600x400")
        history_win.configure(bg=ModernStyle.BG_PRIMARY)
        
        # Header
        ttk.Label(
            history_win,
            text="📜 Organization History",
            style="Header.TLabel"
        ).pack(pady=20)
        
        # History list
        list_frame = ttk.Frame(history_win)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        history_text = tk.Text(
            list_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        history_text.pack(fill=tk.BOTH, expand=True)
        
        # Populate history
        for i, session in enumerate(reversed(history)):
            status = "✅" if not session.get("undone") else "↩️ Undone"
            if session.get("dry_run"):
                status = "👁️ Preview"
            
            history_text.insert(
                tk.END,
                f"{status} {session['timestamp']}\n"
                f"   Source: {session['source']}\n"
                f"   Files: {session['files_moved']}\n\n"
            )
        
        history_text.configure(state=tk.DISABLED)
    
    def process_messages(self):
        """Process messages from worker threads."""
        try:
            while True:
                msg_type, data, extra = self.message_queue.get_nowait()
                
                if msg_type == "organize_complete":
                    self._handle_organize_complete(data, extra)
                elif msg_type == "undo_complete":
                    self._handle_undo_complete(data)
                elif msg_type == "error":
                    self._handle_error(data)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def _handle_organize_complete(self, stats, dry_run):
        """Handle organization completion."""
        self.set_running(False)
        
        mode = "Preview" if dry_run else "Organization"
        total = sum(stats.get("stats", {}).values()) if stats else 0
        
        self.log(f"\n{mode} complete!", "success")
        
        if stats and stats.get("stats"):
            self.log("Files by category:", "info")
            for category, count in stats["stats"].items():
                if count > 0:
                    self.log(f"  📁 {category}: {count} files", "success")
        
        self.log(f"Total: {total} files {'would be' if dry_run else ''} organized", "success")
        
        if not dry_run and total > 0:
            messagebox.showinfo(
                "Success",
                f"Organization complete!\n\n{total} files organized."
            )
    
    def _handle_undo_complete(self, stats):
        """Handle undo completion."""
        self.set_running(False)
        
        if stats.get("success"):
            self.log(f"Undo complete!", "success")
            self.log(f"  Files restored: {stats.get('restored', 0)}", "success")
            if stats.get("errors", 0) > 0:
                self.log(f"  Errors: {stats.get('errors', 0)}", "warning")
            
            messagebox.showinfo(
                "Undo Complete",
                f"Successfully restored {stats.get('restored', 0)} files."
            )
        else:
            self.log(f"Undo failed: {stats.get('message', 'Unknown error')}", "error")
    
    def _handle_error(self, error_msg):
        """Handle errors from worker threads."""
        self.set_running(False)
        self.log(f"Error: {error_msg}", "error")
        messagebox.showerror("Error", error_msg)


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Set icon if available
    try:
        # Windows uses ico files
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            root.iconbitmap(icon_path)
    except Exception:
        pass
    
    app = SmartFileOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
