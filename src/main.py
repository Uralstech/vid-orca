from llama_cpp import Llama, ChatCompletion, ChatCompletionChunk
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from fastapi import FastAPI
from uvicorn import run

from typing import Type, Union, Iterator
from os import cpu_count

from model_from_typed_dict import model_from_typed_dict
from classes import Request

app = FastAPI(title="Vid Orca", version="1.1.0")
llama = Llama(model_path="../models/model.bin", n_ctx=2048, n_batch=8, n_threads=int(cpu_count() / 2) or 1)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

response_model: Type[BaseModel] = model_from_typed_dict(ChatCompletion)

@app.post("/api/chat", response_model=response_model)
async def chat(request: Request) -> Union[ChatCompletion, EventSourceResponse]:
    completion_or_chunks: Union[ChatCompletion, Iterator[ChatCompletionChunk]] = llama.create_chat_completion(**request.dict(), max_tokens=1024)
    completion: ChatCompletion = completion_or_chunks
    return completion

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8080)