from llama_cpp import Llama, ChatCompletion, ChatCompletionChunk
from sse_starlette.sse import EventSourceResponse
from typing import Any, Type, Union, Iterator
from pydantic import BaseModel
from fastapi import FastAPI
from os import cpu_count
from uvicorn import run

from model_from_typed_dict import model_from_typed_dict
from classes import ChatCompletionsRequest
from middleware import UMiddleware

# CONSTANTS

USE_FIREBASE_ADMIN_AUTH: bool = True # Change this to `False` if you are not using Firebase Admin for authentication
MODEL_PATH: str = "../models/llama-2-7b.ggmlv3.q4_K_S.bin" # If needed, change this to the path to your LLaMA model binary.

APP_VERSION: str = "1.2.1"
APP_NAME: str = "Vid Orca"

# APP INITIALIZATION

firebase_app: Any = None
if USE_FIREBASE_ADMIN_AUTH:
    from firebase_admin import initialize_app as initialize_firebase_app
    firebase_app = initialize_firebase_app()

app: FastAPI = FastAPI(title=APP_NAME, version=APP_VERSION)
llama: Llama = Llama(model_path=MODEL_PATH, n_ctx=4096, n_batch=1024, n_threads=cpu_count())
app.add_middleware(UMiddleware, use_firebase_admin_auth=USE_FIREBASE_ADMIN_AUTH, firebase_app=firebase_app)

response_model: Type[BaseModel] = model_from_typed_dict(ChatCompletion)

# APP FUNCTIONS

@app.post("/api/chat", response_model=response_model)
async def chat(request: ChatCompletionsRequest) -> Union[ChatCompletion, EventSourceResponse]:
    print("Chat-completion request received!")

    completion_or_chunks: Union[ChatCompletion, Iterator[ChatCompletionChunk]] = llama.create_chat_completion(**request.dict(), max_tokens=4096)
    completion: ChatCompletion = completion_or_chunks

    print("Sending completion!")
    return completion

# APP RUN

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8080)