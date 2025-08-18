def match_color(number: int) -> str:
    if number < 15:
        return 'is-info'
    elif number < 30:
        return 'is-link'
    elif number < 45:
        return 'is-primary'
    elif number < 60:
        return 'is-success'
    elif number < 75:
        return 'is-warning'
    else:
        return 'is-danger'