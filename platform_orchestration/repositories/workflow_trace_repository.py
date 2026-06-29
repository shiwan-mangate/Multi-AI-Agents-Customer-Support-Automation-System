# repositories/workflow_trace_repository.py

from sqlalchemy import select

from platform_orchestration.models.workflow_trace_model import WorkflowTrace


class WorkflowTraceRepository:

    def __init__(self, session):
        self.session = session

    def create(
        self,
        ticket_id: str,
        stage: str,
        status: str,
        details: str | None = None
    ):
        row = WorkflowTrace(
            ticket_id=ticket_id,
            stage=stage,
            status=status,
            details=details
        )

        self.session.add(row)

    def get_ticket_trace(
        self,
        ticket_id: str
    ):
        stmt = (
            select(WorkflowTrace)
            .where(
                WorkflowTrace.ticket_id == ticket_id
            )
            .order_by(
                WorkflowTrace.created_at.asc()
            )
        )

        return list(
            self.session.scalars(stmt).all()
        )