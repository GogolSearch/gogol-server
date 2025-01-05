def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {'true', 't', 'yes', 'y', '1'}:
        return True
    elif value.lower() in {'false', 'f', 'no', 'n', '0'}:
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}")