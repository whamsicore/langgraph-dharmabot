"""
This file appears to contain Python functions related to handling and processing Python code blocks within text messages. The `extract_python_code` function extracts Python code snippets from text, while the `check` function checks for the presence and correctness of a single Python code block in the last answer of the conversation, providing appropriate error messages if needed. This file seems to be part of the DharmaBot UI's functionality to assist users in interacting with Python code snippets.
"""

import re
from dharmabot.state import AgentState


def extract_python_code(text):
    pattern = r'```python\s*(.*?)\s*(```|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


error_parsing = """Make sure your response contains a code block in the following format:

```python
...
```

When trying to parse out that code block, got this error: {error}"""


def check(state: AgentState):
    last_answer = state['messages'][-1]
    try:
        code_blocks = extract_python_code(last_answer.content)
    except Exception as e:
        return {"messages": [{"role": "user", "content": error_parsing.format(error=str(e))}]}
    if len(code_blocks) == 0:
        return {"messages": [{"role": "user", "content": error_parsing.format(error="Did not find a code block!")}]}
    if len(code_blocks) > 1:
        return {"messages": [{"role": "user", "content": error_parsing.format(error="Found multiple code blocks!")}]}
    return {"code": f"```python\n{code_blocks[0][0]}\n```"}
