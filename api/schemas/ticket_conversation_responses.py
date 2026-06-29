from pydantic import BaseModel

class MessageItem(BaseModel):
    role: str
    content: str

class TicketMessagesResponse(BaseModel):
    ticket_id: str
    total_messages: int
    messages: list[MessageItem]