def cast_to_bool(value: str) -> bool:
    true_vals = {'true', 'yes', '1', 'si', 'sí', 'sure', 'obvio', 'claro'}
    if value is None:
        return False
    return value.lower() in true_vals