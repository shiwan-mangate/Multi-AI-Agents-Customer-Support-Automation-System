# platform_orchestration/dependency_container.py

from crm_agent.db.connection import SessionLocal
from shared.llm.llm_factory import get_llm
from platform_orchestration.repositories.workflow_repository import WorkflowRepository
from .builders.build_account import build_account
from .builders.build_escalation import build_escalation
from .builders.build_faq import build_faq
from .builders.build_proactive import build_proactive
from .builders.build_refund import build_refund
from .builders.build_triage import build_triage
from .builders.build_layer3 import build_layer3
from .builders.build_layer4 import build_layer4
from .builders.build_crm import build_crm
from .builders.build_layer0 import build_layer0
from .builders.build_layer1 import build_layer1
from .builders.build_outbound import build_outbound
import os
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from platform_orchestration.repositories.workflow_trace_repository import WorkflowTraceRepository
import logging
logger = logging.getLogger("dependency_container")

class DependencyContainer:
    def __init__(self):
        # =========================================================
        # 1. CORE CLIENTS & DATABASES (Must happen first!)
        # =========================================================
        self.db = SessionLocal()
        self.llm = get_llm()
        self.workflow_repository = WorkflowRepository(self.db)
        
        # Initialize Orchestrator State Connection Pool (Port 5432)
        main_db_uri = os.environ["PSYCOPG_DATABASE_URL"]

        self.pg_pool = ConnectionPool(
            conninfo=main_db_uri,
            min_size=1,
            max_size=5,
            timeout=30,
            max_idle=300,
            reconnect_timeout=10,
            kwargs={
        "autocommit": True,
        "connect_timeout": 10,
    },
        )
        logger.warning(self.pg_pool.get_stats())
    
        self.checkpointer = PostgresSaver(self.pg_pool)

        logger.warning("POOL ID = %s", id(self.pg_pool))
        logger.warning("CHECKPOINTER ID = %s", id(self.checkpointer))

        self.checkpointer.setup()  
        logger.warning("CHECKPOINTER CREATED")

  
        faq_db_uri = os.environ["FAQ_DATABASE_URL"]
        self.faq_vector_pool = ConnectionPool(conninfo=faq_db_uri)


        build_crm(self)       
        build_triage(self)   
        build_layer3(self)   
        build_outbound(self)  
        build_layer0(self)  
        build_layer1(self)  
        self.workflow_trace_repository = (
    WorkflowTraceRepository(self.db)
)
        
        build_account(self)
        build_escalation(self)
        build_faq(self)
        build_proactive(self)
        build_refund(self)
        build_layer4(self)

    
    def get_graph(self, agent_type: str):
        """Safely fetches a registered domain graph by agent type."""
        graphs = getattr(self, "specialist_graphs", {})
        return graphs.get(agent_type)

    def get_output_mapper(self, agent_type: str):
        """Safely fetches a registered output mapper by agent type."""
        mappers = getattr(self, "output_mappers", {})
        return mappers.get(agent_type)