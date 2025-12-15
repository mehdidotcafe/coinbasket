import functools

from api.authentication.invalid_authentication_exception import (
    InvalidAuthenticationException,
)


def authentication(agent_key: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) >= 2 and args[1].agent_key == agent_key:
                return func(*args, **kwargs)
            else:
                raise InvalidAuthenticationException()

        return wrapper

    return decorator
