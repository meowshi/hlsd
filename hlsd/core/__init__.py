from typing import Any, Callable


def todo(msg: str, func: Callable[..., Any] | None = None):
    print(msg)

    if func:
        func()

    exit(1)
