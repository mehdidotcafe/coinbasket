from typing import Any


invalid_authentication_credential: dict[str, Any] = {
    "description": "Invalid authentication credential",
    "content": {
        "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}
    },
}
