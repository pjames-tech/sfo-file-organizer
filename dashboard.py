"""
Smart File Organizer - Web Dashboard

A comprehensive web-based dashboard for managing the Smart File Organizer.
Includes file organization, rules management, history, and settings.

Run with: python dashboard.py
Then open: http://localhost:8080
"""

import http.server
import socketserver
import json
import webbrowser
import threading
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import DEFAULT_SOURCE_DIR, FILE_CATEGORIES
from organizer import organize_files
from history import (
    undo_last_session, 
    get_history_summary, 
    get_last_session,
    load_history,
    clear_history
)

# Custom rules file
RULES_FILE = Path(__file__).parent / "custom_rules.json"
SETTINGS_FILE = Path(__file__).parent / "dashboard_settings.json"


def load_custom_rules() -> dict:
    """Load custom rules from JSON file."""
    if RULES_FILE.exists():
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"keyword_rules": {}, "extension_overrides": {}}


def save_custom_rules(rules: dict) -> None:
    """Save custom rules to JSON file."""
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)


def load_settings() -> dict:
    """Load dashboard settings."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "source_dir": DEFAULT_SOURCE_DIR,
        "use_ai": False,
        "log_level": "INFO"
    }


def save_settings(settings: dict) -> None:
    """Save dashboard settings."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_stats() -> dict:
    """Get organization statistics."""
    history = load_history()
    sessions = history.get("sessions", [])
    
    total_files = sum(len(s.get("movements", [])) for s in sessions if not s.get("dry_run"))
    total_sessions = len([s for s in sessions if not s.get("dry_run")])
    undone_sessions = len([s for s in sessions if s.get("undone")])
    
    # Category breakdown from last session
    category_counts = {}
    if sessions:
        last_session = sessions[-1]
        for movement in last_session.get("movements", []):
            dest = Path(movement.get("to", ""))
            if dest.parent.name in FILE_CATEGORIES or dest.parent.name == "Other":
                cat = dest.parent.name
                category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "total_files_organized": total_files,
        "total_sessions": total_sessions,
        "undone_sessions": undone_sessions,
        "categories_used": len(FILE_CATEGORIES),
        "last_session_categories": category_counts
    }


# Organization job tracking
current_job = {
    "id": None,
    "status": "idle",
    "progress": 0,
    "message": "",
    "result": None
}


def run_organize_job(source_dir: str, dry_run: bool, use_ai: bool):
    """Run organization in background."""
    global current_job
    
    try:
        current_job["status"] = "running"
        current_job["message"] = "Starting organization..."
        
        result = organize_files(
            source_dir=source_dir,
            dest_dir=source_dir,
            dry_run=dry_run,
            use_ai=use_ai
        )
        
        current_job["status"] = "complete"
        current_job["result"] = result
        current_job["message"] = "Organization complete!"
        
    except Exception as e:
        current_job["status"] = "error"
        current_job["message"] = str(e)
        current_job["result"] = None


# HTML template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart File Organizer - Dashboard</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-hover: #79b8ff;
            --success: #3fb950;
            --danger: #f85149;
            --warning: #d29922;
            --border: #30363d;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .nav {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 0 2rem;
            display: flex;
            align-items: center;
            height: 60px;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-brand {
            font-size: 1.25rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), var(--success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-right: 2rem;
        }
        
        .nav-tabs {
            display: flex;
            gap: 0.5rem;
        }
        
        .nav-tab {
            padding: 0.75rem 1.25rem;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.2s;
            border: none;
            background: none;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: var(--bg-tertiary);
        }
        
        .nav-tab.active {
            color: var(--accent);
            background: var(--bg-primary);
            border-bottom: 2px solid var(--accent);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .page {
            display: none;
        }
        
        .page.active {
            display: block;
        }
        
        .page-header {
            margin-bottom: 2rem;
        }
        
        .page-header h1 {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            color: var(--text-secondary);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            text-align: center;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        input[type="text"], select {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-size: 1rem;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.2);
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: var(--accent);
            color: var(--bg-primary);
        }
        
        .btn-primary:hover {
            background: var(--accent-hover);
        }
        
        .btn-success {
            background: var(--success);
            color: white;
        }
        
        .btn-success:hover {
            background: #4cc65c;
        }
        
        .btn-warning {
            background: var(--warning);
            color: var(--bg-primary);
        }
        
        .btn-warning:hover {
            background: #e0a82e;
        }
        
        .btn-danger {
            background: transparent;
            color: var(--danger);
            border: 1px solid var(--danger);
        }
        
        .btn-danger:hover {
            background: var(--danger);
            color: white;
        }
        
        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover {
            background: var(--border);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-group {
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
        }
        
        .progress-container {
            display: none;
            margin: 1.5rem 0;
        }
        
        .progress-container.visible {
            display: block;
        }
        
        .progress-bar {
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--success));
            width: 0%;
            transition: width 0.3s;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .progress-text {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .results-panel {
            display: none;
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        
        .results-panel.visible {
            display: block;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .result-item {
            background: var(--bg-secondary);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .result-count {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--success);
        }
        
        .result-category {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        /* Rules table */
        .rules-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .rules-table th {
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        
        .rules-table td {
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
        }
        
        .rules-table tr:hover {
            background: var(--bg-tertiary);
        }
        
        .category-tag {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .category-Images { background: #3fb95020; color: #3fb950; }
        .category-Documents { background: #58a6ff20; color: #58a6ff; }
        .category-Videos { background: #f8514920; color: #f85149; }
        .category-Audio { background: #d2992220; color: #d29922; }
        .category-Archives { background: #a371f720; color: #a371f7; }
        .category-Code { background: #79c0ff20; color: #79c0ff; }
        .category-Executables { background: #ff7b7220; color: #ff7b72; }
        .category-Fonts { background: #ffa65720; color: #ffa657; }
        .category-Other { background: #8b949e20; color: #8b949e; }
        
        /* History */
        .history-item {
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .history-info {
            flex: 1;
        }
        
        .history-timestamp {
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        
        .history-details {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .history-status {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-left: 1rem;
        }
        
        .history-status.completed {
            background: #3fb95020;
            color: var(--success);
        }
        
        .history-status.undone {
            background: #d2992220;
            color: var(--warning);
        }
        
        .history-status.preview {
            background: #58a6ff20;
            color: var(--accent);
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            background: var(--success);
            color: white;
            font-weight: 500;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s;
            z-index: 1000;
        }
        
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .toast.error {
            background: var(--danger);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: var(--accent);
        }
        
        .filter-bar {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .filter-bar input {
            flex: 1;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
        }
        
        .form-row .form-group {
            flex: 1;
        }
        
        /* Quick actions */
        .quick-actions {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .quick-action {
            flex: 1;
            min-width: 150px;
            background: var(--bg-tertiary);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        
        .quick-action:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }
        
        .quick-action-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .quick-action-label {
            font-weight: 500;
        }
        
        .quick-action-desc {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-brand">📁 Smart File Organizer</div>
        <div class="nav-tabs">
            <button class="nav-tab active" data-page="dashboard">📊 Dashboard</button>
            <button class="nav-tab" data-page="organize">🚀 Organize</button>
            <button class="nav-tab" data-page="rules">📋 Rules</button>
            <button class="nav-tab" data-page="history">📜 History</button>
            <button class="nav-tab" data-page="settings">⚙️ Settings</button>
        </div>
    </nav>
    
    <div class="container">
        <!-- Dashboard Page -->
        <div class="page active" id="page-dashboard">
            <div class="page-header">
                <h1>📊 Dashboard</h1>
                <p>Overview of your file organization activity</p>
            </div>
            
            <div class="stats-grid" id="stats-grid">
                <!-- Stats loaded dynamically -->
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">⚡ Quick Actions</h3>
                </div>
                <div class="quick-actions">
                    <div class="quick-action" onclick="switchPage('organize'); startOrganize();">
                        <div class="quick-action-icon">🚀</div>
                        <div class="quick-action-label">Organize Now</div>
                        <div class="quick-action-desc">Organize your files instantly</div>
                    </div>
                    <div class="quick-action" onclick="switchPage('organize'); startPreview();">
                        <div class="quick-action-icon">👁️</div>
                        <div class="quick-action-label">Preview Changes</div>
                        <div class="quick-action-desc">See what will happen</div>
                    </div>
                    <div class="quick-action" onclick="undoLast();">
                        <div class="quick-action-icon">↩️</div>
                        <div class="quick-action-label">Undo Last</div>
                        <div class="quick-action-desc">Restore previous state</div>
                    </div>
                    <div class="quick-action" onclick="switchPage('rules');">
                        <div class="quick-action-icon">📋</div>
                        <div class="quick-action-label">Manage Rules</div>
                        <div class="quick-action-desc">Customize classification</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Organize Page -->
        <div class="page" id="page-organize">
            <div class="page-header">
                <h1>🚀 Organize Files</h1>
                <p>Select a folder and organize your files</p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📂 Source Folder</h3>
                </div>
                
                <div class="form-group">
                    <label>Folder path to organize</label>
                    <input type="text" id="source-dir" placeholder="Enter folder path (e.g., C:\\Users\\Downloads)">
                </div>
                
                <div class="checkbox-group">
                    <input type="checkbox" id="use-ai">
                    <label for="use-ai" style="margin: 0;">🤖 Use AI Classification (requires Ollama)</label>
                </div>
                
                <div class="btn-group">
                    <button class="btn btn-success" id="btn-organize" onclick="startOrganize()">
                        🚀 Organize Now
                    </button>
                    <button class="btn btn-primary" id="btn-preview" onclick="startPreview()">
                        👁️ Preview Changes
                    </button>
                </div>
                
                <div class="progress-container" id="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill"></div>
                    </div>
                    <div class="progress-text" id="progress-text">Processing...</div>
                </div>
                
                <div class="results-panel" id="results-panel">
                    <h4 style="margin-bottom: 0.5rem;">✅ Results</h4>
                    <div id="results-summary"></div>
                    <div class="results-grid" id="results-grid"></div>
                </div>
            </div>
        </div>
        
        <!-- Rules Page -->
        <div class="page" id="page-rules">
            <div class="page-header">
                <h1>📋 Classification Rules</h1>
                <p>Manage custom keyword rules for file classification</p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">➕ Add New Rule</h3>
                </div>
                <form id="add-rule-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Keyword (in filename)</label>
                            <input type="text" id="rule-keyword" placeholder="e.g., invoice, screenshot" required>
                        </div>
                        <div class="form-group">
                            <label>Category</label>
                            <select id="rule-category" required>
                                <option value="Images">📷 Images</option>
                                <option value="Documents">📄 Documents</option>
                                <option value="Videos">🎬 Videos</option>
                                <option value="Audio">🎵 Audio</option>
                                <option value="Archives">📦 Archives</option>
                                <option value="Code">💻 Code</option>
                                <option value="Executables">⚙️ Executables</option>
                                <option value="Fonts">🔤 Fonts</option>
                                <option value="Other">📁 Other</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Add Rule</button>
                </form>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📋 Current Rules</h3>
                    <span id="rule-count" style="color: var(--text-secondary);">0 rules</span>
                </div>
                
                <div class="filter-bar">
                    <input type="text" id="rule-search" placeholder="🔍 Search rules...">
                    <select id="rule-filter">
                        <option value="">All Categories</option>
                        <option value="Images">Images</option>
                        <option value="Documents">Documents</option>
                        <option value="Videos">Videos</option>
                        <option value="Audio">Audio</option>
                        <option value="Archives">Archives</option>
                        <option value="Code">Code</option>
                        <option value="Executables">Executables</option>
                        <option value="Fonts">Fonts</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                
                <div id="rules-container"></div>
                
                <div class="btn-group" style="margin-top: 1rem;">
                    <button class="btn btn-secondary" onclick="exportRules()">📤 Export</button>
                    <button class="btn btn-secondary" onclick="document.getElementById('import-file').click()">📥 Import</button>
                    <input type="file" id="import-file" accept=".json" style="display: none;" onchange="importRules(event)">
                    <button class="btn btn-danger" onclick="clearAllRules()">🗑️ Clear All</button>
                </div>
            </div>
        </div>
        
        <!-- History Page -->
        <div class="page" id="page-history">
            <div class="page-header">
                <h1>📜 Organization History</h1>
                <p>View and manage past organization sessions</p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Recent Sessions</h3>
                    <button class="btn btn-danger" onclick="clearHistory()">🗑️ Clear History</button>
                </div>
                
                <div id="history-container"></div>
            </div>
        </div>
        
        <!-- Settings Page -->
        <div class="page" id="page-settings">
            <div class="page-header">
                <h1>⚙️ Settings</h1>
                <p>Configure your file organizer preferences</p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📂 Default Directories</h3>
                </div>
                <div class="form-group">
                    <label>Default Source Folder</label>
                    <input type="text" id="settings-source" placeholder="Default folder to organize">
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">🤖 AI Settings</h3>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="settings-ai">
                    <label for="settings-ai" style="margin: 0;">Enable AI classification by default</label>
                </div>
                <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 0.9rem;">
                    Requires Ollama with llama3.2 model installed
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📁 File Categories</h3>
                </div>
                <div id="categories-list"></div>
            </div>
            
            <button class="btn btn-success" onclick="saveSettings()">💾 Save Settings</button>
        </div>
    </div>
    
    <div class="toast" id="toast">Success!</div>
    
    <script>
        // State
        let rules = {};
        let settings = {};
        let history = [];
        
        // Navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => switchPage(tab.dataset.page));
        });
        
        function switchPage(page) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            
            document.querySelector(`[data-page="${page}"]`).classList.add('active');
            document.getElementById(`page-${page}`).classList.add('active');
            
            // Refresh page data
            if (page === 'dashboard') loadStats();
            if (page === 'rules') loadRules();
            if (page === 'history') loadHistory();
            if (page === 'settings') loadSettingsPage();
        }
        
        // Toast notifications
        function showToast(message, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.toggle('error', isError);
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
        
        // Stats
        async function loadStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            document.getElementById('stats-grid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${stats.total_files_organized}</div>
                    <div class="stat-label">Files Organized</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.total_sessions}</div>
                    <div class="stat-label">Total Sessions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.categories_used}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Object.keys(rules.keyword_rules || {}).length}</div>
                    <div class="stat-label">Custom Rules</div>
                </div>
            `;
        }
        
        // Organization
        async function startOrganize() {
            const sourceDir = document.getElementById('source-dir').value;
            if (!sourceDir) {
                showToast('Please enter a folder path', true);
                return;
            }
            
            runOrganization(sourceDir, false);
        }
        
        async function startPreview() {
            const sourceDir = document.getElementById('source-dir').value;
            if (!sourceDir) {
                showToast('Please enter a folder path', true);
                return;
            }
            
            runOrganization(sourceDir, true);
        }
        
        async function runOrganization(sourceDir, dryRun) {
            const useAi = document.getElementById('use-ai').checked;
            
            // Show progress
            document.getElementById('progress-container').classList.add('visible');
            document.getElementById('results-panel').classList.remove('visible');
            document.getElementById('btn-organize').disabled = true;
            document.getElementById('btn-preview').disabled = true;
            
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            
            progressFill.style.width = '30%';
            progressText.textContent = dryRun ? 'Analyzing files...' : 'Organizing files...';
            
            try {
                const response = await fetch('/api/organize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ source_dir: sourceDir, dry_run: dryRun, use_ai: useAi })
                });
                
                progressFill.style.width = '70%';
                
                const result = await response.json();
                
                progressFill.style.width = '100%';
                
                setTimeout(() => {
                    document.getElementById('progress-container').classList.remove('visible');
                    document.getElementById('btn-organize').disabled = false;
                    document.getElementById('btn-preview').disabled = false;
                    
                    if (result.success) {
                        showResults(result, dryRun);
                        showToast(dryRun ? 'Preview complete!' : 'Organization complete!');
                    } else {
                        showToast(result.error || 'An error occurred', true);
                    }
                }, 500);
                
            } catch (error) {
                document.getElementById('progress-container').classList.remove('visible');
                document.getElementById('btn-organize').disabled = false;
                document.getElementById('btn-preview').disabled = false;
                showToast('Error: ' + error.message, true);
            }
        }
        
        function showResults(result, dryRun) {
            const panel = document.getElementById('results-panel');
            const summary = document.getElementById('results-summary');
            const grid = document.getElementById('results-grid');
            
            const stats = result.stats || {};
            const total = Object.values(stats).reduce((a, b) => a + b, 0);
            
            summary.innerHTML = `<p style="color: var(--text-secondary);">${total} files ${dryRun ? 'would be' : 'were'} organized</p>`;
            
            grid.innerHTML = Object.entries(stats)
                .filter(([_, count]) => count > 0)
                .map(([category, count]) => `
                    <div class="result-item">
                        <div class="result-count">${count}</div>
                        <div class="result-category">${category}</div>
                    </div>
                `).join('');
            
            panel.classList.add('visible');
        }
        
        async function undoLast() {
            if (!confirm('Undo the last organization? Files will be restored to their original locations.')) {
                return;
            }
            
            try {
                const response = await fetch('/api/undo', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    showToast(`Restored ${result.restored} files`);
                    loadHistory();
                    loadStats();
                } else {
                    showToast(result.message || 'Nothing to undo', true);
                }
            } catch (error) {
                showToast('Error: ' + error.message, true);
            }
        }
        
        // Rules
        async function loadRules() {
            const response = await fetch('/api/rules');
            rules = await response.json();
            renderRules();
        }
        
        function renderRules() {
            const container = document.getElementById('rules-container');
            const searchTerm = document.getElementById('rule-search').value.toLowerCase();
            const filterCat = document.getElementById('rule-filter').value;
            
            const filteredRules = Object.entries(rules.keyword_rules || {})
                .filter(([keyword, category]) => {
                    const matchesSearch = keyword.toLowerCase().includes(searchTerm);
                    const matchesCategory = !filterCat || category === filterCat;
                    return matchesSearch && matchesCategory;
                });
            
            if (filteredRules.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No rules found. Add your first rule above!</p>
                    </div>
                `;
                document.getElementById('rule-count').textContent = '0 rules';
                return;
            }
            
            document.getElementById('rule-count').textContent = `${filteredRules.length} rules`;
            
            container.innerHTML = `
                <table class="rules-table">
                    <thead>
                        <tr>
                            <th>Keyword</th>
                            <th>Category</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredRules.map(([keyword, category]) => `
                            <tr>
                                <td><code>${keyword}</code></td>
                                <td><span class="category-tag category-${category}">${category}</span></td>
                                <td><button class="btn btn-danger" onclick="deleteRule('${keyword}')">Delete</button></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        document.getElementById('add-rule-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const keyword = document.getElementById('rule-keyword').value.toLowerCase().trim();
            const category = document.getElementById('rule-category').value;
            
            rules.keyword_rules = rules.keyword_rules || {};
            rules.keyword_rules[keyword] = category;
            
            await saveRules();
            document.getElementById('rule-keyword').value = '';
            showToast('Rule added!');
        });
        
        async function deleteRule(keyword) {
            if (confirm(`Delete rule for "${keyword}"?`)) {
                delete rules.keyword_rules[keyword];
                await saveRules();
                showToast('Rule deleted');
            }
        }
        
        async function saveRules() {
            await fetch('/api/rules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(rules)
            });
            renderRules();
        }
        
        function exportRules() {
            const blob = new Blob([JSON.stringify(rules, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'custom_rules.json';
            a.click();
            showToast('Rules exported!');
        }
        
        function importRules(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = async (e) => {
                    try {
                        const imported = JSON.parse(e.target.result);
                        rules = { ...rules, ...imported };
                        await saveRules();
                        showToast('Rules imported!');
                    } catch (err) {
                        showToast('Invalid JSON file', true);
                    }
                };
                reader.readAsText(file);
            }
        }
        
        async function clearAllRules() {
            if (confirm('Delete ALL custom rules? This cannot be undone.')) {
                rules = { keyword_rules: {}, extension_overrides: {} };
                await saveRules();
                showToast('All rules cleared');
            }
        }
        
        document.getElementById('rule-search').addEventListener('input', renderRules);
        document.getElementById('rule-filter').addEventListener('change', renderRules);
        
        // History
        async function loadHistory() {
            const response = await fetch('/api/history');
            history = await response.json();
            renderHistory();
        }
        
        function renderHistory() {
            const container = document.getElementById('history-container');
            
            if (history.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📜</div>
                        <p>No organization history yet</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = history.slice().reverse().map(session => {
                let statusClass = 'completed';
                let statusText = '✅ Completed';
                
                if (session.undone) {
                    statusClass = 'undone';
                    statusText = '↩️ Undone';
                } else if (session.dry_run) {
                    statusClass = 'preview';
                    statusText = '👁️ Preview';
                }
                
                return `
                    <div class="history-item">
                        <div class="history-info">
                            <div class="history-timestamp">${new Date(session.timestamp).toLocaleString()}</div>
                            <div class="history-details">
                                📂 ${session.source} • ${session.files_moved} files
                            </div>
                        </div>
                        <span class="history-status ${statusClass}">${statusText}</span>
                    </div>
                `;
            }).join('');
        }
        
        async function clearHistory() {
            if (confirm('Clear all history? This cannot be undone.')) {
                await fetch('/api/history', { method: 'DELETE' });
                loadHistory();
                loadStats();
                showToast('History cleared');
            }
        }
        
        // Settings
        async function loadSettingsPage() {
            const response = await fetch('/api/settings');
            settings = await response.json();
            
            document.getElementById('settings-source').value = settings.source_dir || '';
            document.getElementById('settings-ai').checked = settings.use_ai || false;
            
            // Also set the organize page source
            if (!document.getElementById('source-dir').value) {
                document.getElementById('source-dir').value = settings.source_dir || '';
            }
            
            // Show categories
            const categoriesHtml = Object.entries({
                'Images': '📷',
                'Documents': '📄',
                'Videos': '🎬',
                'Audio': '🎵',
                'Archives': '📦',
                'Code': '💻',
                'Executables': '⚙️',
                'Fonts': '🔤'
            }).map(([cat, icon]) => `
                <span class="category-tag category-${cat}" style="margin: 0.25rem;">${icon} ${cat}</span>
            `).join('');
            
            document.getElementById('categories-list').innerHTML = `
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">${categoriesHtml}</div>
            `;
        }
        
        async function saveSettings() {
            settings = {
                source_dir: document.getElementById('settings-source').value,
                use_ai: document.getElementById('settings-ai').checked
            };
            
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            
            showToast('Settings saved!');
        }
        
        // Initialize
        async function init() {
            await loadRules();
            await loadStats();
            
            // Load settings and apply to organize page
            const settingsResponse = await fetch('/api/settings');
            settings = await settingsResponse.json();
            document.getElementById('source-dir').value = settings.source_dir || '';
            document.getElementById('use-ai').checked = settings.use_ai || false;
        }
        
        init();
    </script>
</body>
</html>
"""


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for the dashboard."""
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        
        elif parsed.path == '/api/rules':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            rules = load_custom_rules()
            self.wfile.write(json.dumps(rules).encode())
        
        elif parsed.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = get_stats()
            self.wfile.write(json.dumps(stats).encode())
        
        elif parsed.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            history = get_history_summary()
            self.wfile.write(json.dumps(history).encode())
        
        elif parsed.path == '/api/settings':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            settings = load_settings()
            self.wfile.write(json.dumps(settings).encode())
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(post_data.decode()) if post_data else {}
        except json.JSONDecodeError:
            data = {}
        
        if self.path == '/api/rules':
            save_custom_rules(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": true}')
        
        elif self.path == '/api/organize':
            source_dir = data.get('source_dir', '')
            dry_run = data.get('dry_run', False)
            use_ai = data.get('use_ai', False)
            
            try:
                if not source_dir or not Path(source_dir).exists():
                    raise ValueError(f"Folder not found: {source_dir}")
                
                result = organize_files(
                    source_dir=source_dir,
                    dest_dir=source_dir,
                    dry_run=dry_run,
                    use_ai=use_ai
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "stats": result.get("stats", {}) if result else {}
                }).encode())
                
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": str(e)
                }).encode())
        
        elif self.path == '/api/undo':
            try:
                result = undo_last_session()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": str(e)
                }).encode())
        
        elif self.path == '/api/settings':
            save_settings(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": true}')
        
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        if self.path == '/api/history':
            clear_history()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": true}')
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Suppress logging
        pass


def main():
    PORT = 8080
    
    print("=" * 50)
    print("Smart File Organizer - Web Dashboard")
    print("=" * 50)
    print(f"\n🌐 Starting server at http://localhost:{PORT}")
    print("📊 Full-featured dashboard for organizing files")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}')
    
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")


if __name__ == "__main__":
    main()
