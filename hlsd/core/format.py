SUFFIXES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
PRECISION = 2
KB = 1024.


def size(bytes: float):
    i = 0
    while bytes >= KB and i < len(SUFFIXES)-1:
        bytes /= KB
        i += 1

    f = ('%.2f' % bytes).rstrip('0').rstrip('.')
    return f'{f} {SUFFIXES[i]}'
