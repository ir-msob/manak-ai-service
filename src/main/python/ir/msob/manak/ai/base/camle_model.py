from pydantic import BaseModel


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    """Base model that outputs camelCase keys."""
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
