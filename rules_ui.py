"""
Rules Manager - Web UI for managing custom classification rules.

Provides a simple web interface to:
- View all current keyword rules
- Add new rules
- Edit existing rules
- Delete rules
- Export/Import rules

Run with: python rules_ui.py
Then open: http://localhost:8080
"""

import http.server
import socketserver
import json
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Import rules from the main module
RULES_FILE = Path(__file__).parent / "custom_rules.json"

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


# HTML template for the UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart File Organizer - Rules Manager</title>
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
            padding: 2rem;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--accent), var(--success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: var(--text-secondary);
        }
        
        .section {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        h2 {
            font-size: 1.25rem;
            color: var(--text-primary);
        }
        
        .badge {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .form-row {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .form-group {
            flex: 1;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        input, select {
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
        
        button {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .btn-primary {
            background: var(--accent);
            color: var(--bg-primary);
        }
        
        .btn-primary:hover {
            background: var(--accent-hover);
        }
        
        .btn-danger {
            background: transparent;
            color: var(--danger);
            border: 1px solid var(--danger);
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
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
        
        .actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
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
        }
        
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background: var(--bg-tertiary);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent);
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .filter-bar {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .search-input {
            flex: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📁 Rules Manager</h1>
            <p class="subtitle">Smart File Organizer - Custom Classification Rules</p>
        </header>
        
        <div class="stats" id="stats">
            <!-- Stats loaded dynamically -->
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>➕ Add New Rule</h2>
            </div>
            <form id="addRuleForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="keyword">Keyword (in filename)</label>
                        <input type="text" id="keyword" placeholder="e.g., invoice, screenshot" required>
                    </div>
                    <div class="form-group">
                        <label for="category">Category</label>
                        <select id="category" required>
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
                <button type="submit" class="btn-primary">Add Rule</button>
            </form>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>📋 Current Rules</h2>
                <span class="badge" id="ruleCount">0 rules</span>
            </div>
            
            <div class="filter-bar">
                <input type="text" class="search-input" id="searchInput" placeholder="🔍 Search rules...">
                <select id="filterCategory">
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
            
            <div id="rulesContainer">
                <!-- Rules loaded dynamically -->
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                <h2>⚡ Quick Actions</h2>
            </div>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <button class="btn-secondary" onclick="exportRules()">📤 Export Rules</button>
                <button class="btn-secondary" onclick="document.getElementById('importFile').click()">📥 Import Rules</button>
                <input type="file" id="importFile" accept=".json" style="display: none;" onchange="importRules(event)">
                <button class="btn-danger" onclick="clearAllRules()">🗑️ Clear All</button>
            </div>
        </div>
    </div>
    
    <div class="toast" id="toast">Rule saved successfully!</div>
    
    <script>
        let rules = {};
        
        async function loadRules() {
            const response = await fetch('/api/rules');
            rules = await response.json();
            renderRules();
            updateStats();
        }
        
        function renderRules() {
            const container = document.getElementById('rulesContainer');
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const filterCat = document.getElementById('filterCategory').value;
            
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
                document.getElementById('ruleCount').textContent = '0 rules';
                return;
            }
            
            document.getElementById('ruleCount').textContent = `${filteredRules.length} rules`;
            
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
                                <td class="actions">
                                    <button class="btn-danger" onclick="deleteRule('${keyword}')">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        function updateStats() {
            const rulesCount = Object.keys(rules.keyword_rules || {}).length;
            const categories = [...new Set(Object.values(rules.keyword_rules || {}))];
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${rulesCount}</div>
                    <div class="stat-label">Total Rules</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${categories.length}</div>
                    <div class="stat-label">Categories Used</div>
                </div>
            `;
        }
        
        document.getElementById('addRuleForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const keyword = document.getElementById('keyword').value.toLowerCase().trim();
            const category = document.getElementById('category').value;
            
            rules.keyword_rules = rules.keyword_rules || {};
            rules.keyword_rules[keyword] = category;
            
            await saveRules();
            document.getElementById('keyword').value = '';
            showToast('Rule added successfully!');
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
            updateStats();
        }
        
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
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
                        alert('Invalid JSON file');
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
        
        // Filter listeners
        document.getElementById('searchInput').addEventListener('input', renderRules);
        document.getElementById('filterCategory').addEventListener('change', renderRules);
        
        // Load rules on page load
        loadRules();
    </script>
</body>
</html>
"""


class RulesHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for the rules manager UI."""
    
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
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/rules':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            rules = json.loads(post_data.decode())
            save_custom_rules(rules)
            
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
    print("Smart File Organizer - Rules Manager")
    print("=" * 50)
    print(f"\n🌐 Starting server at http://localhost:{PORT}")
    print("📝 Manage your custom classification rules")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}')
    
    with socketserver.TCPServer(("", PORT), RulesHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")


if __name__ == "__main__":
    main()
