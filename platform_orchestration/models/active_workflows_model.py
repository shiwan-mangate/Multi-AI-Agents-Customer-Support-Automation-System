from sqlalchemy import Column, String, DateTime, ForeignKey, Index, text
from crm_agent.db.base import Base

class ActiveWorkflow(Base):
    __tablename__ = 'active_workflows'

    workflow_id = Column(String(100), primary_key=True)
    
    ticket_id = Column(
        String(100), 
        ForeignKey('tickets.ticket_id', name='active_workflows_ticket_id_fkey'), 
        nullable=False
    )
    
    agent_type = Column(String(100), nullable=False)
    
    status = Column(
        String(50), 
        nullable=False, 
        server_default=text("'PENDING'::character varying")
    )
    
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("now()")
    )
    
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=text("now()")
    )
    
    thread_id = Column(String(255), nullable=True)

    __table_args__ = (
        # Partial Unique Index: Guarantees only one 'PENDING' workflow per ticket
        Index(
            'idx_active_ticket', 
            'ticket_id', 
            unique=True, 
            postgresql_where=text("((status)::text = 'PENDING'::text)")
        ),
    )