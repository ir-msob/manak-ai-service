from typing import Dict, Optional, Union

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class ToolParameter(ResponseModel):
    """
    Represents a parameter definition used to describe complex JSON structures.

    This model is inspired by JSON Schema and OpenAPI parameter structures,
    allowing it to represent any nested or hierarchical data definition that
    can be understood both by humans and AI systems.
    """

    type: str = Field(..., description=(
        "The data type of the parameter. Supported values: string, number, boolean, object, array."
        "Example:"
        "- 'string' → A single string value"
        "- 'array' → A list of values (defined by 'items')"
        "- 'object' → A structured value (defined by 'properties')"
    ))

    description: str = Field(..., description=(
        "A human-readable description of what this parameter represents."
        "Helps both developers and AI models understand the semantic meaning of the field."
    ))

    default_value: Optional[Union[str, int, float, bool, dict, list]] = Field(
        None, description="The default value to use when the parameter is not provided."
    )

    example: Optional[Union[str, int, float, bool, dict, list]] = Field(
        None, description="An example value illustrating how this parameter might look in real data."
    )

    required: bool = Field(
        False, description="Indicates whether this parameter is required in the context where it is used."
    )

    items: Optional['ToolParameter'] = Field(
        None, description=(
            "Describes the structure or type of each item in an array."
            "Used only when type = 'array'. Example:"
            "type = 'array', items = { type = 'string' } represents a list of strings."
        )
    )

    properties: Optional[Dict[str, 'ToolParameter']] = Field(
        default_factory=dict, description=(
            "Describes the properties of an object when type = 'object'."
            "Each key in this map represents a field name, and the corresponding value "
            "is another ToolParameter defining that field's structure."
            "Example:"
            "type = 'object', properties = {"
            "  'name': { type: 'string' },"
            "  'age': { type: 'number' }"
            "}"
        )
    )
