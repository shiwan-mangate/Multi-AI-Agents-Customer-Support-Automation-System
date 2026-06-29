from pydantic import BaseModel, Field

class InboundTicketRequest(BaseModel):
    """Standardized payload for inbound customer support tickets."""
    message: str = Field(..., description="Raw customer message")
    customer_id: int = Field(..., description="Unique customer identifier")
    name: str = Field(..., description="Customer full name")
    channel: str = Field(default="email", description="Inbound channel")


class ContinueConversationRequest(BaseModel):
    """
    Customer follow-up message on an existing ticket.
    """
    message: str = Field(
        ...,
        description="The follow-up message from the customer."
    )