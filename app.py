import os
import json

# List of file paths you want to aggregate
file_paths = [
    r"C:\Users\roman\Documents\SimuVerseFramework_MK1\main.py",
    r"C:\Users\roman\OneDrive\Documents\Unity Projects\SimuVerse3D\SimuExoV1\Assets\Scripts\AgentBrain.cs",
    r"C:\Users\roman\OneDrive\Documents\Unity Projects\SimuVerse3D\SimuExoV1\Assets\Scripts\AgentTools.cs",
    r"C:\Users\roman\OneDrive\Documents\Unity Projects\SimuVerse3D\SimuExoV1\Assets\Scripts\WorldManager.cs",
    # Add more paths as needed
]

# Map extensions to language names
extension_map = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".html": "HTML",
    ".css": "CSS",
    # ...add other mappings as desired
}

# Container for all file details
aggregated_data = []

for path in file_paths:
    # Extract file extension
    _, ext = os.path.splitext(path)
    # Match extension to language, or use 'Unknown'
    language = extension_map.get(ext.lower(), "Unknown")

    try:
        with open(path, encoding="utf-8") as file:
            content = file.read()
        aggregated_data.append({
            "filename": os.path.basename(path),
            "language": language,
            "content": content
        })
    except Exception as e:
        print(f"Error reading {path}: {e}")

# Write the text header plus the aggregated data to a JSON-like file
output_filename = "aggregated_files.json"
with open(output_filename, "w", encoding="utf-8") as out_file:
    # Write the plain text at the top
    out_file.write("Current code below\n")
    # Write the actual JSON data
    json.dump(aggregated_data, out_file, indent=2)

print(f"Aggregated file data (with header text) saved to {output_filename}")