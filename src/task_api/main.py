
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response

from task_api.models import (
    MessageCreate,
    MessageUpdate,
    MessageResponse
)
from task_api import storage


app = FastAPI(
    title="Task API",
    description="API project setup and Messages API",
    version="1.0.0"
)


# Custom 404 error response
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "message_not_found",
                "message": "The requested message was not found."
            }
        }
    )


# Existing health endpoint
@app.get(
    "/health",
    response_model=dict,
    tags=["Health"],
    summary="Check API health"
)
def health_check():
    return {
        "status": "ok",
        "version": app.version
    }


# 1. Create a message
@app.post(
    "/api/v1/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    summary="Create a message",
    description="Create a new user or assistant message."
)
def create_message(message: MessageCreate):
    return storage.create_message(
        role=message.role,
        content=message.content
    )


# 2. List messages
@app.get(
    "/api/v1/messages",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
    tags=["Messages"],
    summary="List messages",
    description="List messages with pagination and optional role filtering."
)
def list_messages(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    role: Optional[Literal["user", "assistant"]] = None
):
    filtered_messages = storage.messages

    if role is not None:
        filtered_messages = [
            message for message in filtered_messages
            if message["role"] == role
        ]

    return filtered_messages[offset:offset + limit]


# 3. Retrieve one message
@app.get(
    "/api/v1/messages/{message_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Messages"],
    summary="Get a message",
    description="Retrieve one message using its ID."
)
def get_message(message_id: int):
    message = storage.get_message(message_id)

    if message is None:
        raise HTTPException(status_code=404)

    return message


# 4. Update a message
@app.patch(
    "/api/v1/messages/{message_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Messages"],
    summary="Update a message",
    description="Update the content of an existing message."
)
def update_message(message_id: int, update: MessageUpdate):
    message = storage.update_message(
        message_id,
        update.content
    )

    if message is None:
        raise HTTPException(status_code=404)

    return message


# 5. Delete a message
@app.delete(
    "/api/v1/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["Messages"],
    summary="Delete a message",
    description="Delete an existing message by its ID."
)
def delete_message(message_id: int):
    deleted = storage.delete_message(message_id)

    if not deleted:
        raise HTTPException(status_code=404)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
