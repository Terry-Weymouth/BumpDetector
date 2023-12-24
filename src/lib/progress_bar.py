def print_progress(n, n1, n2):
    part = (100.0 * (n - n1)) / (n2 - n1)
    left = 100.0 - part
    dots = int(left + 0.49)
    spaces = 100 - dots
    print("\r" + (" " * 110), end='')
    print("\r" + f"{left:6.2f}% left: |" + ("*" * dots) + (' ' * spaces) + '|', end='')


def clear_progress(message=''):
    print(f"\r{message}" + ' '*100)
