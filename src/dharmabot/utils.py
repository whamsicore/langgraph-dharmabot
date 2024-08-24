"""
This Python code defines a function `flatten_list` that takes a nested list of items as input and flattens it into a single list. The purpose of this function is to flatten a nested list structure into a single list of strings, which can be useful for processing hierarchical data structures into a format that can be more easily displayed or interacted with in a user interface like DharmaBot UI.
"""


def flatten_list(items):
    result = []
    
    def _flatten(subitems):
        for item in subitems:
            if isinstance(item, str):
                result.append(item)
            else:
                _flatten(item)
    
    _flatten(items)
    return "\n".join(result)
