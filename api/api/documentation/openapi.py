from typing import Any
from apispec import APISpec
from pydantic import BaseModel, RootModel


def openapi(
    spec: APISpec,
    schemas: list[type[BaseModel | RootModel[Any]]],
    path: str,
    operations: dict[str, Any] | None,
):
    def decorator(cls: Any):
        for schema in schemas:
            spec.components.schema(
                schema.__name__,
                component=schema.schema(ref_template="#/components/schemas/{model}"),
            )

        spec.path(
            path=path,
            operations=operations,
        )
        return cls

    return decorator
