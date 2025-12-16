import functools

from api.authentication.invalid_authentication_exception import (
    InvalidAuthenticationException,
)


def authentication(app_key: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            first_key = next(iter(kwargs))
            if kwargs[first_key].app_key == app_key:
                return func(*args, **kwargs)
            else:
                raise InvalidAuthenticationException()

        return wrapper

    return decorator
