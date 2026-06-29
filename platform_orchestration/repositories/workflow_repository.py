import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

# Core Agent Imports across domains
from layer_2_triage.database.model.ticket_model import Ticket
from platform_orchestration.models.active_workflows_model import ActiveWorkflow

logger = logging.getLogger("workflow_repository")

class WorkflowRecord:
    def __init__(self, workflow_id: str, ticket_id: str, thread_id: str, agent_type: str, status: str):
        self.workflow_id = workflow_id
        self.ticket_id = ticket_id
        self.thread_id = thread_id
        self.agent_type = agent_type
        self.status = status

class WorkflowRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_active_workflow(self, workflow_id: str, ticket_id: str, thread_id: str, agent_type: str, status: str = "PENDING"):
        logger.info(f"💾 DB | Saving Workflow {workflow_id} for Ticket {ticket_id} ({agent_type}) with status: {status}")
        
        normalized_status = str(status).strip().upper()

        try:
            # 1. The bouncer is the 'tickets' table! It demands an 'issue_type'.
            # Native PostgreSQL ON CONFLICT DO NOTHING using SQLAlchemy
            seed_stmt = insert(Ticket).values(
                ticket_id=ticket_id,
                customer_id=1,
                issue_type='system_test',
                created_at=func.now()
            ).on_conflict_do_nothing(index_elements=['ticket_id'])
            
            self.session.execute(seed_stmt)

            # 2. Your active_workflows table (UPSERT Logic)
            insert_stmt = insert(ActiveWorkflow).values(
                workflow_id=workflow_id,
                ticket_id=ticket_id,
                thread_id=thread_id,
                agent_type=agent_type,
                status=normalized_status,
                created_at=func.now(),
                updated_at=func.now()
            )

            # Define the ON CONFLICT DO UPDATE part of the statement
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=['workflow_id'],
                set_={
                    'status': insert_stmt.excluded.status,
                    'updated_at': func.now()
                }
            )

            self.session.execute(upsert_stmt)
            self.session.commit()
            
            logger.info(f"✅ DB | Successfully updated workflow {workflow_id} states.")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Failed to save active workflow {workflow_id}. Database Reason: {e}")
            raise e

    def get(self, ticket_id: str) -> Optional[WorkflowRecord]:
        try:
            result = self.session.query(
                ActiveWorkflow.workflow_id,
                ActiveWorkflow.ticket_id,
                ActiveWorkflow.thread_id,
                ActiveWorkflow.agent_type,
                ActiveWorkflow.status
            ).filter(
                ActiveWorkflow.ticket_id == ticket_id,
                ActiveWorkflow.status.in_(['PENDING', 'PENDING_REVIEW', 'HUMAN_REVIEW_REQUIRED'])
            ).order_by(
                ActiveWorkflow.created_at.desc()
            ).first()

            if result:
                return WorkflowRecord(
                    workflow_id=result.workflow_id,
                    ticket_id=result.ticket_id,
                    thread_id=result.thread_id,
                    agent_type=result.agent_type,
                    status=result.status
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch active workflow for {ticket_id}: {e}")
            return None

    def mark_completed(self, ticket_id: str):
        logger.info(f"💾 DB | Marking active workflows for Ticket {ticket_id} as COMPLETED.")
        
        try:
            query = self.session.query(ActiveWorkflow).filter(
                ActiveWorkflow.ticket_id == ticket_id,
                ActiveWorkflow.status.in_(['PENDING', 'PENDING_REVIEW', 'HUMAN_REVIEW_REQUIRED'])
            )
            
            query.update({
                "status": "COMPLETED",
                "updated_at": func.now()
            }, synchronize_session=False)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Failed to mark workflow completed for {ticket_id}: {e}")
            raise e
        
    def get_all_pending(self, limit: int = 50) -> List[WorkflowRecord]:
        """Fetches the queue of workflows waiting for human manager review."""
        try:
            results = self.session.query(
                ActiveWorkflow.workflow_id,
                ActiveWorkflow.ticket_id,
                ActiveWorkflow.thread_id,
                ActiveWorkflow.agent_type,
                ActiveWorkflow.status
            ).filter(
                ActiveWorkflow.status.in_(['PENDING_REVIEW', 'HUMAN_REVIEW_REQUIRED', 'PENDING'])
            ).order_by(
                ActiveWorkflow.created_at.asc()
            ).limit(limit).all()

            return [
                WorkflowRecord(
                    workflow_id=row.workflow_id,
                    ticket_id=row.ticket_id,
                    thread_id=row.thread_id,
                    agent_type=row.agent_type,
                    status=row.status
                ) for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch pending workflows: {e}")
            return []