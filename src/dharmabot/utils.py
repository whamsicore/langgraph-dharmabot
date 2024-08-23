
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
