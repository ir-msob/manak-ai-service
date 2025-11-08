from __future__ import annotations
from typing import Dict, List, Optional, Union
from pydantic import Field
from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel

class ToolParameter(ResponseModel):
    """
    Represents a parameter definition used to describe complex JSON structures.

    This model is inspired by JSON Schema and OpenAPI parameter structures,
    allowing it to represent any nested or hierarchical data definition that
    can be understood both by humans and AI systems.
    """

    class ToolParameterType(str):
        STRING = "STRING"
        NUMBER = "NUMBER"
        BOOLEAN = "BOOLEAN"
        OBJECT = "OBJECT"
        ARRAY = "ARRAY"

    type: str = Field(
        ...,
        description=(
            "The data type of the parameter. Supported values: STRING, NUMBER, BOOLEAN, OBJECT, ARRAY.\n"
            "Example:\n"
            "- 'STRING' → A single string value\n"
            "- 'ARRAY' → A list of values (defined by 'items')\n"
            "- 'OBJECT' → A structured value (defined by 'properties')"
        ),
    )

    description: str = Field(
        ...,
        description="A human-readable description of what this parameter represents.",
    )

    default_value: Optional[Union[str, int, float, bool, dict, list]] = Field(
        default=None,
        description="The default value to use when the parameter is not provided.",
    )

    example: Optional[Union[str, int, float, bool, dict, list]] = Field(
        default=None,
        description=(
            "A example value that illustrate how this parameter might appear in actual data.\n"
            "Example:\n"
            "- 'John Doe'\n"
            "- 2\n"
            "- ['application/json', 'text/plain']"
        ),
    )

    required: bool = Field(
        default=False,
        description="Indicates whether this parameter is required in the context where it is used.",
    )

    items: Optional[ToolParameter] = Field(
        default=None,
        description=(
            "Describes the structure or type of each item in an array.\n"
            "Used only when type = 'ARRAY'.\n"
            "Example:\n"
            "type = 'ARRAY', items = { type = 'STRING' } → list of strings."
        ),
    )

    properties: Optional[Dict[str, ToolParameter]] = Field(
        default_factory=dict,
        description=(
            "Describes the properties of an object when type = 'OBJECT'.\n"
            "Each key represents a field name and maps to a ToolParameter describing it."
        ),
    )

    minimum: Optional[Union[int, float]] = Field(
        default=None,
        description=(
            "The minimum numeric value allowed for NUMBER type parameters.\n"
            "Example: type = 'NUMBER', minimum = 0"
        ),
    )

    maximum: Optional[Union[int, float]] = Field(
        default=None,
        description=(
            "The maximum numeric value allowed for NUMBER type parameters.\n"
            "Example: type = 'NUMBER', maximum = 100"
        ),
    )

    min_length: Optional[int] = Field(
        default=None,
        description=(
            "The minimum length of the value for STRING type parameters.\n"
            "Example: type = 'STRING', minLength = 3"
        ),
    )

    max_length: Optional[int] = Field(
        default=None,
        description=(
            "The maximum length of the value for STRING type parameters.\n"
            "Example: type = 'STRING', maxLength = 255"
        ),
    )

    pattern: Optional[str] = Field(
        default=None,
        description=(
            "A regular expression pattern the STRING value must match.\n"
            "Example: pattern = '^[A-Za-z0-9_-]+$'"
        ),
    )

    enum_values: Optional[List[Union[str, int, float, bool]]] = Field(
        default_factory=list,
        description=(
            "A list of allowed constant values for the parameter (similar to an enum).\n"
            "Example: enumValues = ['ASC', 'DESC']"
        ),
    )

    nullable: bool = Field(
        default=False,
        description="Indicates whether the parameter value can be null.",
    )


ToolParameter.model_rebuild()  # Required for self-referencing fields