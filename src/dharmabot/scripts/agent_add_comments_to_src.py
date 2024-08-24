"""
This Python file serves the purpose of analyzing other files within a specified directory by utilizing OpenAI API to determine their purpose. It adds a comment describing the purpose at the beginning of each file, based on the analysis conducted. This functionality aligns with the broader context of DharmaBot UI as it aims to enhance the understanding and organization of code files within a project by automatically adding descriptive comments.
"""

import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# System prompt describing DharmaBot UI
SYSTEM_PROMPT = """
DharmaBot UI is an agent chat-powered interface for directly interacting with a Neo4j graph database. 
Its current purpose is focused on displaying and interacting with graphs, with plans to add 
functionality for manipulating those graphs in the future. Please analyze the given file content 
and provide a brief comment (2-3 sentences) about its purpose in the context of DharmaBot UI.
"""

# Initialize ChatOpenAI
llm_openai = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=openai_api_key,
)

def get_file_purpose(file_content):
    """Use OpenAI API to get the file's purpose"""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Analyze this file content and describe its purpose:\n\n{file_content}")
    ]
    
    try:
        response = llm_openai.invoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"Error invoking OpenAI: {str(e)}")
        return "Unable to determine file purpose due to an error."

def add_comment_to_file(file_path, comment):
    """Add the comment to the beginning of the file"""
    with open(file_path, 'r') as file:
        content = file.read()
    
    file_extension = os.path.splitext(file_path)[1]
    
    if file_extension in ['.py', '.js', '.ts', '.tsx']:
        comment_block = f'"""\n{comment}\n"""\n\n'
    elif file_extension in ['.css', '.html']:
        comment_block = f'<!--\n{comment}\n-->\n\n'
    else:
        comment_block = f'# {comment}\n\n'
    
    with open(file_path, 'w') as file:
        file.write(comment_block + content)

def process_directory(directory):
    """Process all files in the given directory"""
    for root, dirs, files in os.walk(directory):
        if '.next' in dirs:
            dirs.remove('.next')  # Exclude .next directory
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip files that are likely to be binary or non-code files
            if file.endswith(('.pyc', '.pyo', '.so', '.o', '.a', '.lib', '.dll', '.exe')):
                continue
            
            print(f"Processing: {file_path}")
            
            try:
                with open(file_path, 'r') as f:
                    file_content = f.read()
                
                file_purpose = get_file_purpose(file_content)
                add_comment_to_file(file_path, file_purpose)
                print(f"Added comment to: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    src_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    process_directory(src_directory)
    print("Finished processing all files.")