import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from message_broker.api.rmq_service import publish_message

app = FastAPI()


class MessageRequest(BaseModel):
    user_alias: str
    message: str


@app.post("/")
async def read_message(request: MessageRequest):
    await publish_message(request)


if __name__ == "__main__":
    uvicorn.run(
        "message_broker.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
