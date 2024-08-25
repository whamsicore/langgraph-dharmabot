"""
This script generates a tree structure of a project directory and writes it to a Markdown file. It iterates through the project directory, excluding specified folders and files, and creates a hierarchical representation of the project's structure. In the context of DharmaBot UI, this script could be used to visualize and analyze the directory structures of projects stored in a graph database, providing a clear overview of the relationships between files and folders.
"""

import os

def should_ignore(path):
    ignore_list = [
        'node_modules',
        '__pycache__',
        '.git',
        '.vscode',
        '.DS_Store',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '*.so',
        '*.dylib',
        '*.egg-info',
        '*.egg',
        'dist',
        'build',
        'venv',
        '.next',
        'myenv',
    ]
    return any(ignored in path for ignored in ignore_list)

def generate_tree(startpath, output_file):
    # Ensure the directory exists before creating the file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("# Project Structure\n\n")
        f.write("```\n")
        for root, dirs, files in os.walk(startpath):
            if should_ignore(root):
                continue
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                if not should_ignore(file):
                    f.write(f"{subindent}{file}\n")
        f.write("```\n")

# Assuming this script is run from the project root
project_root = os.getcwd()
output_file = os.path.join(project_root, 'outputs', 'project_structure.md')

generate_tree(project_root, output_file)
print(f"Project structure has been written to {output_file}")