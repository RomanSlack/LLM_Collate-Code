from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import os
import json

# -----------------------
# FLASK SETUP
# -----------------------
app = Flask(__name__)

# This is where we store user-defined profiles (e.g., "default", "project_x").
# Each profile has a list of file paths to be aggregated.
PROFILES_FILE = "profiles.json"

# Basic extension-to-language mapping
EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".html": "HTML",
    ".css": "CSS",
    ".cs": "C#"
    # ...add more as needed
}

# If profiles.json doesn't exist, create a default structure
if not os.path.exists(PROFILES_FILE):
    # You can seed some default file paths here if you like
    default_paths = [
        r"/home/roman-slack/SimuVerseFramework_MK1/main.py",
        r"/home/roman-slack/SimuExoV1/Assets/Scripts/AgentBrain.cs",
        r"/home/roman-slack/SimuExoV1/Assets/Scripts/AgentTools.cs",
        r"/home/roman-slack/SimuExoV1/Assets/Scripts/WorldManager.cs",
    ]
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump({"default": default_paths}, f, indent=2)

def load_profiles():
    """Load profiles from the JSON file."""
    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(profiles):
    """Save profiles to the JSON file."""
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

# -----------------------
# HELPER: AGGREGATE FILES
# -----------------------
def aggregate_files(file_paths):
    """Read each file or directory, detect language, and return a combined JSON-like string."""
    aggregated_data = []
    
    for path in file_paths:
        # Check if path is a directory
        if os.path.isdir(path):
            # Process directory recursively
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Skip hidden files and directories
                    if os.path.basename(file_path).startswith('.'):
                        continue
                    process_file(file_path, aggregated_data)
        else:
            # Process single file
            process_file(path, aggregated_data)

    # Create a string that starts with "Current code below:" then the JSON
    combined = "Current code below:\n" + json.dumps(aggregated_data, indent=2)
    return combined

def process_file(path, aggregated_data):
    """Process a single file and add it to the aggregated data."""
    _, ext = os.path.splitext(path)
    language = EXTENSION_MAP.get(ext.lower(), "Unknown")
    
    # Skip binary files and other non-text formats
    binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', '.zip', 
                         '.tar', '.gz', '.exe', '.dll', '.so', '.pyc', '.class'}
    if ext.lower() in binary_extensions:
        aggregated_data.append({
            "filename": os.path.basename(path),
            "language": "Binary",
            "content": f"[Binary file: {os.path.basename(path)}]",
            "full_path": path
        })
        return

    try:
        # Try to read as text
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        aggregated_data.append({
            "filename": os.path.basename(path),
            "language": language,
            "content": content,
            "full_path": path
        })
    except UnicodeDecodeError:
        # Handle case where the file is binary but doesn't have a recognized extension
        aggregated_data.append({
            "filename": os.path.basename(path),
            "language": "Binary",
            "content": f"[Binary file: {os.path.basename(path)}]",
            "full_path": path
        })
    except Exception as e:
        # Handle other errors
        aggregated_data.append({
            "filename": os.path.basename(path),
            "language": "Error",
            "content": f"Could not read file: {e}",
            "full_path": path
        })

# -----------------------
# ROUTES
# -----------------------
@app.route("/", methods=["GET", "POST"])
def index():
    profiles = load_profiles()
    # If there's no explicit selected profile in the query, pick "default" if it exists
    selected_profile = request.args.get("profile", "default" if "default" in profiles else None)
    
    # Pass the os module to the template for path operations
    template_context = {
        "profiles": profiles,
        "selected_profile": selected_profile,
        "os": os
    }

    # Construct a minimal HTML using render_template_string
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CodeCollate | Your Code Aggregator</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap">
        <style>
            :root {
                --primary: #4CAF50;
                --primary-light: #81C784;
                --primary-dark: #388E3C;
                --secondary: #FFC107;
                --gray-light: #f5f5f5;
                --gray: #e0e0e0;
                --dark: #333;
                --white: #ffffff;
                --sidebar-width: 300px;
                --header-height: 64px;
                --shadow: 0 2px 5px rgba(0,0,0,0.1);
                --radius: 8px;
                --animation: 0.3s ease;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                color: var(--dark);
                background-color: var(--gray-light);
                min-height: 100vh;
            }
            
            header {
                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                color: var(--white);
                height: var(--header-height);
                padding: 0 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: var(--shadow);
                z-index: 10;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
            }
            
            .logo {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }
            
            .logo-main {
                display: flex;
                align-items: center;
                font-weight: 700;
                font-size: 1.4rem;
            }
            
            .logo-main i {
                margin-right: 10px;
                font-size: 1.8rem;
            }
            
            .logo-sub {
                font-size: 0.8rem;
                opacity: 0.9;
                margin-top: -5px;
                display: flex;
                align-items: center;
            }
            
            .logo-sub a {
                color: var(--white);
                text-decoration: none;
                margin-left: 10px;
                display: flex;
                align-items: center;
            }
            
            .logo-sub a:hover {
                text-decoration: underline;
            }
            
            .logo-sub a i {
                margin-right: 4px;
            }
            
            .container {
                display: flex;
                margin-top: var(--header-height);
                height: calc(100vh - var(--header-height));
            }
            
            .sidebar {
                width: var(--sidebar-width);
                background-color: var(--white);
                box-shadow: 2px 0 5px rgba(0,0,0,0.05);
                padding: 20px;
                overflow-y: auto;
                transition: transform var(--animation);
                height: 100%;
            }
            
            .main {
                flex: 1;
                padding: 25px;
                overflow-y: auto;
                position: relative;
            }
            
            .panel {
                background-color: var(--white);
                border-radius: var(--radius);
                box-shadow: var(--shadow);
                padding: 20px;
                margin-bottom: 20px;
            }
            
            .panel h3 {
                color: var(--primary-dark);
                margin-bottom: 15px;
                font-weight: 600;
                display: flex;
                align-items: center;
            }
            
            .panel h3 i {
                margin-right: 8px;
            }
            
            .profile-list ul {
                list-style-type: none;
                margin-top: 15px;
            }
            
            .profile-list li {
                padding: 10px 15px;
                margin-bottom: 5px;
                border-radius: var(--radius);
                transition: background-color var(--animation);
                cursor: pointer;
                border-left: 3px solid transparent;
            }
            
            .profile-list li:hover {
                background-color: var(--gray-light);
                border-left-color: var(--primary-light);
            }
            
            .profile-list li.active {
                background-color: var(--gray-light);
                border-left-color: var(--primary);
                font-weight: 500;
            }
            
            .profile-list a {
                text-decoration: none;
                color: var(--dark);
                display: block;
            }
            
            .form-control {
                margin-bottom: 15px;
            }
            
            .form-control label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                font-size: 0.9rem;
            }
            
            input[type="text"] {
                width: 100%;
                padding: 10px;
                border: 1px solid var(--gray);
                border-radius: var(--radius);
                font-size: 0.9rem;
                outline: none;
                transition: border var(--animation);
            }
            
            input[type="text"]:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
            }
            
            button {
                background-color: var(--primary);
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: var(--radius);
                cursor: pointer;
                font-weight: 500;
                transition: background-color var(--animation);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            button:hover {
                background-color: var(--primary-dark);
            }
            
            button i {
                margin-right: 6px;
            }
            
            button.secondary {
                background-color: var(--secondary);
                color: var(--dark);
            }
            
            button.secondary:hover {
                background-color: #FFB300;
            }
            
            .file-list {
                margin: 15px 0;
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid var(--gray);
                border-radius: var(--radius);
            }
            
            .file-item {
                padding: 10px 15px;
                border-bottom: 1px solid var(--gray);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .file-item:last-child {
                border-bottom: none;
            }
            
            .file-path {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                flex: 1;
            }
            
            .file-actions {
                display: flex;
                align-items: center;
            }
            
            .file-actions button {
                background: none;
                color: var(--dark);
                padding: 5px;
                margin-left: 5px;
                border-radius: 50%;
                height: 30px;
                width: 30px;
            }
            
            .file-actions button:hover {
                background-color: var(--gray);
            }
            
            .file-actions button i {
                margin-right: 0;
            }
            
            textarea {
                width: 100%;
                height: calc(100vh - 350px);
                min-height: 300px;
                padding: 15px;
                border: 1px solid var(--gray);
                border-radius: var(--radius);
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.9rem;
                line-height: 1.5;
                resize: vertical;
                outline: none;
                transition: border var(--animation);
            }
            
            textarea:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
            }
            
            .actions-bar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin: 20px 0;
            }
            
            .main-title {
                margin-bottom: 20px;
                border-bottom: 1px solid var(--gray);
                padding-bottom: 15px;
            }
            
            .empty-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 50px 0;
                text-align: center;
                color: #888;
            }
            
            .empty-state i {
                font-size: 3rem;
                margin-bottom: 20px;
                color: var(--gray);
            }
            
            /* Notifications */
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: var(--white);
                padding: 15px 20px;
                border-radius: var(--radius);
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                transform: translateX(120%);
                transition: transform 0.3s ease;
                z-index: 1000;
            }
            
            .notification.success {
                border-left: 4px solid var(--primary);
            }
            
            .notification.error {
                border-left: 4px solid #F44336;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification i {
                margin-right: 10px;
                font-size: 1.2rem;
            }
            
            .notification.success i {
                color: var(--primary);
            }
            
            .notification.error i {
                color: #F44336;
            }
            
            .notification-message {
                font-weight: 500;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .container {
                    flex-direction: column;
                }
                
                .sidebar {
                    width: 100%;
                    max-height: 300px;
                }
                
                .main {
                    height: calc(100vh - var(--header-height) - 300px);
                }
            }
            
            /* Loading indicator */
            .loader {
                border: 4px solid var(--gray-light);
                border-top: 4px solid var(--primary);
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
                display: none;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* File type icons */
            .file-icon {
                width: 20px;
                height: 20px;
                margin-right: 10px;
                text-align: center;
            }
            
            .tab-container {
                margin-bottom: 20px;
            }
            
            .tabs {
                display: flex;
                border-bottom: 1px solid var(--gray);
            }
            
            .tab {
                padding: 10px 20px;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                transition: all var(--animation);
            }
            
            .tab.active {
                border-bottom-color: var(--primary);
                color: var(--primary-dark);
                font-weight: 500;
            }
            
            .tab-content {
                padding: 20px 0;
            }
            
            .tab-pane {
                display: none;
            }
            
            .tab-pane.active {
                display: block;
            }
            
            /* Custom color for language labels */
            .language-label {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 0.7rem;
                background-color: #E3F2FD;
                color: #1976D2;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">
                <div class="logo-main">
                    <i class="fas fa-code"></i>
                    <span>CodeCollate</span>
                </div>
                <div class="logo-sub">
                    <span>Created by Roman Slack</span>
                    <a href="https://github.com/RomanSlack/LLM_Collate-Code" target="_blank" title="View on GitHub">
                        <i class="fab fa-github"></i> GitHub
                    </a>
                </div>
            </div>
            <div>
                <span>Your Code Aggregator</span>
            </div>
        </header>

        <div class="container">
            <!-- SIDEBAR -->
            <div class="sidebar">
                <div class="panel profile-list">
                    <h3><i class="fas fa-layer-group"></i> Profiles</h3>
                    <ul>
                        {% for p in profiles %}
                        <li class="{{ 'active' if p == selected_profile else '' }}">
                            <a href="{{ url_for('index', profile=p) }}">
                                <i class="fas fa-folder{{ '-open' if p == selected_profile else '' }}"></i>
                                {{ p }}
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                </div>

                <div class="panel">
                    <h3><i class="fas fa-plus-circle"></i> Add New Profile</h3>
                    <form action="{{ url_for('add_profile') }}" method="POST">
                        <div class="form-control">
                            <label for="profile_name">Profile Name</label>
                            <input type="text" id="profile_name" name="profile_name" placeholder="e.g., Project X" required>
                        </div>
                        <button type="submit"><i class="fas fa-save"></i> Create Profile</button>
                    </form>
                </div>

                {% if selected_profile %}
                <div class="panel">
                    <h3><i class="fas fa-file-code"></i> Add File or Folder to Profile</h3>
                    <form action="{{ url_for('add_path') }}" method="POST">
                        <input type="hidden" name="profile" value="{{ selected_profile }}">
                        <div class="form-control">
                            <label for="file_path">File or Folder Path</label>
                            <input type="text" id="file_path" name="file_path" placeholder="/path/to/file.py or /path/to/folder" required>
                            <small style="display: block; margin-top: 5px; color: #666;">
                                <i class="fas fa-info-circle"></i> For folders, all files will be processed recursively.
                            </small>
                        </div>
                        <button type="submit"><i class="fas fa-plus"></i> Add Path</button>
                    </form>
                </div>
                {% endif %}
            </div>

            <!-- MAIN CONTENT -->
            <div class="main">
                {% if selected_profile %}
                    <div class="main-title">
                        <h2><i class="fas fa-folder-open"></i> {{ selected_profile }} Profile</h2>
                    </div>
                    
                    <div class="tab-container">
                        <div class="tabs">
                            <div class="tab active" data-tab="files">Files</div>
                            <div class="tab" data-tab="output">Output</div>
                        </div>
                        
                        <div class="tab-content">
                            <div class="tab-pane active" id="files-tab">
                                <div class="panel">
                                    <h3><i class="fas fa-list"></i> Files in this Profile</h3>
                                    
                                    {% if profiles[selected_profile]|length > 0 %}
                                        <div class="file-list">
                                            {% for path in profiles[selected_profile] %}
                                                <div class="file-item">
                                                    <div class="file-icon">
                                                        {% if os.path.isdir(path) %}
                                                            <i class="fas fa-folder" style="color: #FFC107;"></i>
                                                        {% else %}
                                                            {% set ext = path.split('.')[-1] %}
                                                            {% if ext == 'py' %}
                                                                <i class="fab fa-python" style="color: #3776AB;"></i>
                                                            {% elif ext == 'js' %}
                                                                <i class="fab fa-js" style="color: #F7DF1E;"></i>
                                                            {% elif ext == 'html' %}
                                                                <i class="fab fa-html5" style="color: #E34F26;"></i>
                                                            {% elif ext == 'css' %}
                                                                <i class="fab fa-css3-alt" style="color: #1572B6;"></i>
                                                            {% elif ext == 'java' %}
                                                                <i class="fab fa-java" style="color: #007396;"></i>
                                                            {% elif ext == 'cs' %}
                                                                <i class="fas fa-code" style="color: #68217A;"></i>
                                                            {% else %}
                                                                <i class="fas fa-file-code"></i>
                                                            {% endif %}
                                                        {% endif %}
                                                    </div>
                                                    <div class="file-path" title="{{ path }}">
                                                        {{ path }}
                                                        {% if os.path.isdir(path) %}
                                                            <span class="language-label" style="background-color: #FFF3CD; color: #856404;">Folder</span>
                                                        {% endif %}
                                                    </div>
                                                    <div class="file-actions">
                                                        <button type="button" class="remove-file" data-path="{{ path }}" data-profile="{{ selected_profile }}" title="Remove file">
                                                            <i class="fas fa-times"></i>
                                                        </button>
                                                    </div>
                                                </div>
                                            {% endfor %}
                                        </div>
                                        
                                        <div class="actions-bar">
                                            <button id="generateBtn" class="secondary">
                                                <i class="fas fa-sync-alt"></i> Generate & Copy to Clipboard
                                            </button>
                                            <div id="generateLoader" class="loader"></div>
                                        </div>
                                    {% else %}
                                        <div class="empty-state">
                                            <i class="fas fa-folder-open"></i>
                                            <p>No files added to this profile yet.</p>
                                            <p>Add your first file using the form in the sidebar.</p>
                                        </div>
                                    {% endif %}
                                </div>
                            </div>
                            
                            <div class="tab-pane" id="output-tab">
                                <div class="panel">
                                    <h3><i class="fas fa-clipboard"></i> Generated Output</h3>
                                    <textarea id="outputArea" placeholder="Generated content will appear here...
Click 'Generate & Copy to Clipboard' on the Files tab to generate output."></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                {% else %}
                    <div class="panel">
                        <div class="empty-state">
                            <i class="fas fa-exclamation-circle"></i>
                            <h3>No profile selected</h3>
                            <p>Please create or select a profile from the sidebar to get started.</p>
                        </div>
                    </div>
                {% endif %}
            </div>
        </div>

        <!-- Notification component -->
        <div class="notification success" id="notification">
            <i class="fas fa-check-circle"></i>
            <span class="notification-message">Notification message</span>
        </div>

        <script>
            document.addEventListener("DOMContentLoaded", () => {
                // Tab switching
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => {
                    tab.addEventListener('click', () => {
                        // Remove active class from all tabs
                        tabs.forEach(t => t.classList.remove('active'));
                        // Add active class to clicked tab
                        tab.classList.add('active');
                        
                        // Hide all tab panes
                        document.querySelectorAll('.tab-pane').forEach(pane => {
                            pane.classList.remove('active');
                        });
                        
                        // Show the corresponding tab pane
                        const tabName = tab.getAttribute('data-tab');
                        document.getElementById(tabName + '-tab').classList.add('active');
                    });
                });

                // Generate and copy button
                const generateBtn = document.getElementById("generateBtn");
                const outputArea = document.getElementById("outputArea");
                const generateLoader = document.getElementById("generateLoader");

                if (generateBtn) {
                    generateBtn.addEventListener("click", () => {
                        // Show loader
                        generateLoader.style.display = "block";
                        generateBtn.disabled = true;
                        
                        fetch("{{ url_for('generate') }}", {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify({ profile: "{{ selected_profile }}" })
                        })
                        .then(response => response.json())
                        .then(data => {
                            // Hide loader
                            generateLoader.style.display = "none";
                            generateBtn.disabled = false;
                            
                            // Update textarea
                            outputArea.value = data.aggregated;
                            
                            // Switch to output tab
                            document.querySelector('.tab[data-tab="output"]').click();
                            
                            // Copy to clipboard
                            navigator.clipboard.writeText(data.aggregated)
                                .then(() => {
                                    showNotification("Success! Content copied to clipboard.", "success");
                                })
                                .catch(err => {
                                    showNotification("Failed to copy to clipboard: " + err, "error");
                                });
                        })
                        .catch(err => {
                            // Hide loader
                            generateLoader.style.display = "none";
                            generateBtn.disabled = false;
                            showNotification("Error generating content: " + err, "error");
                        });
                    });
                }
                
                // Remove file functionality
                const removeButtons = document.querySelectorAll('.remove-file');
                removeButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        const filePath = button.getAttribute('data-path');
                        const profile = button.getAttribute('data-profile');
                        if (confirm("Are you sure you want to remove this path from the profile?")) {
                            fetch("{{ url_for('remove_path') }}", {
                                method: "POST",
                                headers: {"Content-Type": "application/json"},
                                body: JSON.stringify({ profile: profile, path: filePath })
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Remove the element from the DOM
                                    button.closest('.file-item').remove();
                                    showNotification("Path removed successfully.", "success");
                                    
                                    // If no files left, show empty state
                                    if (document.querySelectorAll('.file-item').length === 0) {
                                        const fileList = document.querySelector('.file-list');
                                        if (fileList) {
                                            fileList.insertAdjacentHTML('afterend', `
                                                <div class="empty-state">
                                                    <i class="fas fa-folder-open"></i>
                                                    <p>No files added to this profile yet.</p>
                                                    <p>Add your first file using the form in the sidebar.</p>
                                                </div>
                                            `);
                                            fileList.remove();
                                            document.querySelector('.actions-bar')?.remove();
                                        }
                                    }
                                } else {
                                    showNotification(data.message || "Failed to remove path.", "error");
                                }
                            })
                            .catch(err => {
                                showNotification("Error: " + err, "error");
                            });
                        }
                    });
                });
                
                // Notification system
                function showNotification(message, type = "success") {
                    const notification = document.getElementById("notification");
                    const messageEl = notification.querySelector(".notification-message");
                    const icon = notification.querySelector("i");
                    
                    // Set type and message
                    notification.className = "notification " + type;
                    messageEl.textContent = message;
                    
                    // Set icon
                    if (type === "success") {
                        icon.className = "fas fa-check-circle";
                    } else {
                        icon.className = "fas fa-exclamation-circle";
                    }
                    
                    // Show notification
                    notification.classList.add("show");
                    
                    // Auto hide after 3 seconds
                    setTimeout(() => {
                        notification.classList.remove("show");
                    }, 3000);
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(template, **template_context)

@app.route("/add_profile", methods=["POST"])
def add_profile():
    """Add a new empty profile."""
    profile_name = request.form.get("profile_name", "").strip()
    if not profile_name:
        return redirect(url_for("index"))

    profiles = load_profiles()
    if profile_name not in profiles:
        profiles[profile_name] = []
        save_profiles(profiles)
    return redirect(url_for("index", profile=profile_name))

@app.route("/add_path", methods=["POST"])
def add_path():
    """Add a new file path to the specified profile."""
    profile = request.form.get("profile", "").strip()
    file_path = request.form.get("file_path", "").strip()
    if not profile or not file_path:
        return redirect(url_for("index"))

    profiles = load_profiles()
    if profile not in profiles:
        profiles[profile] = []
    # Add the path if it's not already in the profile
    if file_path not in profiles[profile]:
        profiles[profile].append(file_path)
    save_profiles(profiles)
    return redirect(url_for("index", profile=profile))

@app.route("/remove_path", methods=["POST"])
def remove_path():
    """Remove a file or folder path from the specified profile."""
    data = request.get_json()
    profile = data.get("profile")
    path = data.get("path")
    
    if not profile or not path:
        return jsonify({"success": False, "message": "Missing profile or path"}), 400
    
    profiles = load_profiles()
    if profile in profiles and path in profiles[profile]:
        profiles[profile].remove(path)
        save_profiles(profiles)
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Path not found in profile"}), 404

@app.route("/generate", methods=["POST"])
def generate():
    """Generate the aggregated code for the given profile and return JSON."""
    data = request.get_json()
    profile = data.get("profile")
    profiles = load_profiles()
    paths = profiles.get(profile, []) if profile in profiles else []

    # Aggregate files
    content = aggregate_files(paths)

    # Also write out the 'aggregated_files.json' for reference, if desired
    # We keep the same "Current code below:\n" + JSON structure here
    output_filename = "aggregated_files.json"
    with open(output_filename, "w", encoding="utf-8") as out_file:
        out_file.write(content)

    return jsonify({"aggregated": content})

# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)