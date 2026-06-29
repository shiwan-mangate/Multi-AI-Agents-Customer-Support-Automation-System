from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class SystemStatusResponse(BaseModel):
    status: str
    database: str
    crm: str
    analytics: str
    proactive: str
class WorkflowSummaryItem(BaseModel):
    workflow_id: str
    ticket_id: str
    agent_type: str
    status: str
    created_at: datetime | None = None
    
class ActiveWorkflowsResponse(BaseModel):
    total: int
    workflows: List[WorkflowSummaryItem]

class WorkflowDetailResponse(BaseModel):
    workflow_id: str
    ticket_id: str
    agent_type: str
    status: str
    thread_id: str
    created_at: datetime | None = None