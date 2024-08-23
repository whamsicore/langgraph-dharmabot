import os
import re

# Define file paths
current_file_path = 'src/dharmabot/scripts/test_chain.py'
utils_file_path = 'src/dharmabot/utils.py'

# Define the function to be moved
flatten_list_function = """
def flatten_list(items):
    result = []
    
    def _flatten(subitems):
        for item in subitems:
            if isinstance(item, str):
                result.append(item)
            else:
                _flatten(item)
    
    _flatten(items)
    return "\\n".join(result)
"""

# Read the current file
with open(current_file_path, 'r') as file:
    current_file_content = file.read()

# Add the function to utils.py
if not os.path.exists(utils_file_path):
    with open(utils_file_path, 'w') as file:
        file.write(flatten_list_function)
else:
    with open(utils_file_path, 'a') as file:
        file.write(flatten_list_function)

# Add the import statement to the current file
import_statement = 'from src.dharmabot.utils import flatten_list\n'
if import_statement not in current_file_content:
    current_file_content = import_statement + current_file_content

# Remove the flatten_list function from the current file
current_file_content = re.sub(r'def flatten_list\(.*?return "\\n".join\(result\)\n', '', current_file_content, flags=re.DOTALL)

# Write the updated content back to the current file
with open(current_file_path, 'w') as file:
    file.write(current_file_content)

print("Function moved and import statement added successfully.")