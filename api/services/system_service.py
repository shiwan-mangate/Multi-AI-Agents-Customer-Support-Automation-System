import logging
from sqlalchemy import text
from fastapi import HTTPException, status
from platform_orchestration.dependency_container import DependencyContainer

from api.schemas.system_responses import (
    SystemStatusResponse,
    ActiveWorkflowsResponse,
    WorkflowSummaryItem,
    WorkflowDetailResponse
)

logger = logging.getLogger("api_system_service")

class SystemService:
    def __init__(self, container: DependencyContainer):
        self.container = container

    def get_system_status(self, request_id: str = "unknown") -> SystemStatusResponse:
        """Pings the database and evaluates component health."""
        logger.info(f"[{request_id}] Checking global system health")
        
        db_status = "disconnected"
        system_state = "degraded"

        try:
           
            try:
                self.container.db.rollback() 
            except Exception:
                pass
            
            self.container.db.execute(text("SELECT 1"))
            db_status = "connected"
            system_state = "healthy"
        except Exception as e:
            logger.error(f"[{request_id}] Database health check failed: {e}", exc_info=True)

        return SystemStatusResponse(
            status=system_state,
            database=db_status,
            crm="active" if db_status == "connected" else "inactive",
            analytics="active" if db_status == "connected" else "inactive",
            proactive="active" if db_status == "connected" else "inactive"
        )

    def get_active_workflows(self, limit: int = 100, request_id: str = "unknown") -> ActiveWorkflowsResponse:
        """Fetches all non-terminal workflows currently in the orchestration layer."""
        try:
            self.container.db.rollback()
        except Exception:
            pass
        logger.info(f"[{request_id}] Fetching active workflows list (limit: {limit})")
        
        try:
           
            query = text("""
                SELECT workflow_id, ticket_id, agent_type, status, created_at
                FROM active_workflows 
                WHERE status NOT IN ('COMPLETED', 'FAILED', 'DEAD')
                ORDER BY created_at DESC 
                LIMIT :limit;
            """)
            results = self.container.db.execute(query, {"limit": limit}).mappings().all()

            items = [
                WorkflowSummaryItem(
                    workflow_id=row["workflow_id"],
                    ticket_id=row["ticket_id"],
                    agent_type=row["agent_type"],
                    status=row["status"],
                    created_at=row["created_at"]
                ) for row in results
            ]

            return ActiveWorkflowsResponse(
                total=len(items),
                workflows=items
            )
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch active workflows: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error retrieving active orchestrator workflows."
            )

    def get_workflow_details(self, ticket_id: str, request_id: str = "unknown") -> WorkflowDetailResponse:
        """Fetches the exact LangGraph execution pointer (thread_id) for a ticket."""
        logger.info(f"[{request_id}] Fetching workflow details for {ticket_id}")
        
        try:
            
            query = text("""
                SELECT workflow_id, ticket_id, agent_type, status, thread_id, created_at 
                FROM active_workflows 
                WHERE ticket_id = :ticket_id
                LIMIT 1;
            """)
            result = self.container.db.execute(query, {"ticket_id": ticket_id}).mappings().first()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No active or historical workflow found for ticket {ticket_id}."
                )

            return WorkflowDetailResponse(
                workflow_id=result["workflow_id"],
                ticket_id=result["ticket_id"],
                agent_type=result["agent_type"],
                status=result["status"],
                thread_id=result["thread_id"],
                created_at=result["created_at"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch workflow details for {ticket_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error retrieving workflow details."
            )
        