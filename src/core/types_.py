from typing import Annotated, Any
from pydantic_core import core_schema
from bson import ObjectId as _ObjectId

from pydantic.annotated_handlers import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(
        cls, v: Any, handler: core_schema.ValidatorFunctionWrapHandler
    ) -> _ObjectId:
        if isinstance(v, _ObjectId):
            return v

        s = handler(v)
        if _ObjectId.is_valid(s):
            return _ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        assert source_type is _ObjectId
        return core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema(min_length=24, max_length=24))


ObjectId = Annotated[_ObjectId, ObjectIdPydanticAnnotation]
