from typing import Any


invalid_authentication_key: dict[str, Any] = {
    "description": "Invalid authentication key",
    "content": {
        "text/plain": {
            "schema": {
                "type": "string",
                "example": "Internal server error",
            }
        }
    },
}
