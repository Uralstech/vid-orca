from typing import _TypedDictMeta as TypedDictMeta
from typing import Type

from pydantic import BaseModel, create_model

def model_from_typed_dict(typed_dict: TypedDictMeta) -> Type[BaseModel]:
    annotations = {}
    for name, field in typed_dict.__annotations__.items():
        if isinstance(field, TypedDictMeta):
            annotations[name] = (model_from_typed_dict(field), ...)
        else:
            default_value = getattr(typed_dict, name, ...)
            annotations[name] = (field, default_value)

    return create_model(typed_dict.__name__, **annotations)