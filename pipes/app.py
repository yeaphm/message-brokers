import json

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from pipes.filter import run_filter_chain_async
from pipes.filter_chain import filter_chain

app = FastAPI()


class MessageRequest(BaseModel):
    user_alias: str
    message: str


@app.post("/")
async def read_message(request: MessageRequest):
    """Handles incoming messages and processes them through the filter chain."""
    message = {"user_alias": request.user_alias, "message": request.message}
    message_json = json.dumps(message)

    print(f"Message received: {message}")

    # Run the filter chain in a background process
    await run_filter_chain_async(filter_chain, message_json)

    return {"status": "Message processing started"}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )
