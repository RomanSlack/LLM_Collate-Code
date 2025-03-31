# Collate Code

A simple Python script that collects code from specified file paths on Windows 10. It copies each file’s content, labels it by programming language, and saves everything into a single JSON file – perfect for feeding into a Large Language Model (LLM).

## How It Works
1. You provide a list of file paths in the script.
2. The script reads each file and identifies its language from the file extension.
3. All code snippets are compiled into a single JSON file called `aggregated_files.json`.

## Getting Started
1. Clone or download this repository.
2. Update the `file_paths` list with the files you want to aggregate.
3. Run the script: `python collate_code.py`
4. Open `aggregated_files.json` to see your collated data.

## Customization
- Extend the `extension_map` dictionary to add mappings for more programming languages or file types.
- Swap out the JSON output for plain text or any other format you prefer.  

## License
This project is licensed under the [MIT License](LICENSE). Feel free to use it and adapt it to suit your needs. Enjoy collating your code!
