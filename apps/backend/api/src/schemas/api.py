from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Self, TypedDict, TypeVar

from pydantic import BaseModel, model_validator

T = TypeVar("T")
NumVar = TypeVar("NumVar", int, float)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Base model for paginated responses.

    Attributes:
        total (int): The total number of items available.
        page (int): The current page number.
        limit (int): The number of items per page.
        total_pages (int): The total number of pages available.
        has_next (bool): Indicates if there is a next page.
        has_prev (bool): Indicates if there is a previous page.
        items (List[T]): The list of items on the current page.
    """

    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
    items: List[T]


class DtypesEnum(Enum):
    """
    Enum for supported data types in the spreadsheet.
    """

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DOUBLE = "double"
    BOOLEAN = "boolean"

    def to_jsonschema_type(self) -> str:
        """
        Map the DtypesEnum to JSON Schema types.

        Returns:
            str: The corresponding JSON Schema type.
        """
        mapping = {
            DtypesEnum.STRING: "string",
            DtypesEnum.INTEGER: "number",
            DtypesEnum.FLOAT: "number",
            DtypesEnum.DOUBLE: "number",
            DtypesEnum.BOOLEAN: "boolean",
        }
        return mapping[self]


class NumberConstraints(BaseModel, Generic[NumVar]):
    minimum: Optional[NumVar] = None
    maximum: Optional[NumVar] = None
    exclusive_minimum: bool = False
    exclusive_maximum: bool = False
    multiple_of: Optional[NumVar] = None

    # Reference here:
    # https://json-schema.org/understanding-json-schema/reference/numeric
    def to_jsonschema_constraints(self) -> Dict[str, Any]:
        constraints = {}
        if self.minimum is not None:
            constraints["minimum"] = self.minimum
            if self.exclusive_minimum:
                constraints["exclusiveMinimum"] = True

        if self.maximum is not None:
            constraints["maximum"] = self.maximum
            if self.exclusive_maximum:
                constraints["exclusiveMaximum"] = True

        if self.multiple_of is not None:
            constraints["multipleOf"] = self.multiple_of

        return constraints


class IntegerConstraints(NumberConstraints[int]):
    pass


class FloatConstraints(NumberConstraints[float]):
    pass


class StringConstraints(BaseModel):
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None

    # Reference here:
    # https://json-schema.org/understanding-json-schema/reference/string
    def to_jsonschema_constraints(self) -> Dict[str, Any]:
        constraints = {}
        if self.min_length is not None:
            constraints["minLength"] = self.min_length

        if self.max_length is not None:
            constraints["maxLength"] = self.max_length

        if self.pattern is not None:
            constraints["pattern"] = self.pattern

        return constraints


class SpreadsheetDtypesSchema(BaseModel):
    dtype: DtypesEnum
    unique: bool = False
    optional: bool = True
    primary_key: bool = False
    constraints: Optional[NumberConstraints | StringConstraints] = None

    @model_validator(mode="after")
    def validate_constraint(self) -> Self:
        match self.dtype:
            case DtypesEnum.INTEGER:
                if self.constraints and not isinstance(
                    self.constraints, IntegerConstraints
                ):
                    raise ValueError(
                        "Constraints for integer types must be of type IntegerConstraints"
                    )
            case DtypesEnum.FLOAT | DtypesEnum.DOUBLE:
                if self.constraints and not isinstance(
                    self.constraints, FloatConstraints
                ):
                    raise ValueError(
                        "Constraints for float/double types must be of type FloatConstraints"
                    )
            case DtypesEnum.STRING:
                if self.constraints and not isinstance(
                    self.constraints, StringConstraints
                ):
                    raise ValueError(
                        "Constraints for string types must be of type StringConstraints"
                    )
            case DtypesEnum.BOOLEAN:
                if self.constraints is not None:
                    raise ValueError("Boolean type does not support constraints")

        return self

    def to_jsonschema_property(self) -> Dict[str, Any]:
        type_mapping = {
            DtypesEnum.STRING: "string",
            DtypesEnum.INTEGER: "integer",
            DtypesEnum.FLOAT: "number",
            DtypesEnum.DOUBLE: "number",
            DtypesEnum.BOOLEAN: "boolean",
        }

        property_schema = {
            "type": type_mapping[self.dtype],
            "unique": self.unique,
            "optional": self.optional,
            "primary_key": self.primary_key,
        }

        if self.constraints:
            property_schema.update(self.constraints.to_jsonschema_constraints())

        return property_schema


ColumnName = str
ColumnDtypesSchema = Dict[ColumnName, SpreadsheetDtypesSchema]


class OpenTelemetryTraceHeaders(TypedDict, total=False):
    traceparent: Optional[str]
    tracestate: Optional[str]
    baggage: Optional[str]
