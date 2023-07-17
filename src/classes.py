from pydantic import BaseModel
from typing import Union, Literal, List

class Message(BaseModel):
    role: Union[Literal["system"], Literal["user"], Literal["assistant"]]
    content: str

class Request(BaseModel):
    messages: List[Message]
    temperature: float = 0.8