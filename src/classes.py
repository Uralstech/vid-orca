from typing import Union, Literal, List
from pydantic import BaseModel

class Message(BaseModel):
    role: Union[Literal["system"], Literal["user"], Literal["assistant"]]
    content: str

class ChatCompletionsRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.8