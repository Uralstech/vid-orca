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

# Set USE_FIREBASE_ADMIN_AUTH to `False` if you do not want Firebase Admin SDK authentication.
USE_FIREBASE_ADMIN_AUTH: bool = True
# Set MODEL_PATH to the path to your model file.
MODEL_PATH: str = "../models/llama-2-13b-chat.gguf.q3_K_S.bin"

APP_VERSION: str = "1.2.10"
APP_NAME: str = "Vid Orca LLaMA-2 13b" # You can change the name to suite your needs and/or model name.

# APP INITIALIZATION

firebase_app: Any = None
if USE_FIREBASE_ADMIN_AUTH:
    from firebase_admin import initialize_app as initialize_firebase_app
    firebase_app = initialize_firebase_app()

app: FastAPI = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(UMiddleware, use_firebase_admin_auth=USE_FIREBASE_ADMIN_AUTH, firebase_app=firebase_app)

# Remove n_gpu_layers=43 if you are using Cloud Run.
llama: Llama = Llama(model_path=MODEL_PATH, n_ctx=4096, n_batch=4096, n_gpu_layers=43, n_threads=cpu_count())
response_model: Type[BaseModel] = model_from_typed_dict(ChatCompletion)

# APP FUNCTIONS

@app.post("/api/chat", response_model=response_model)
async def chat(request: ChatCompletionsRequest) -> Union[ChatCompletion, EventSourceResponse]:
    print("Chat-completion request received!")

    completion_or_chunks: Union[ChatCompletion, Iterator[ChatCompletionChunk]] = llama.create_chat_completion(**request.model_dump(), max_tokens=4096)
    completion: ChatCompletion = completion_or_chunks

    print("Sending completion!")
    return completion

# APP RUN

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8080)