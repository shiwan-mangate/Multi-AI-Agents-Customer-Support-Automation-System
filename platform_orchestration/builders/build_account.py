# platform_orchestration/builders/build_account.py

import logging

# Repositories
from layer_2_account_agent.repositories.account_repository import AccountRepository
from layer_2_account_agent.repositories.billing_repository import BillingRepository
from layer_2_account_agent.repositories.customer_repository import CustomerRepository
from layer_2_account_agent.repositories.security_audit_repository import SecurityAuditRepository

# Services
from layer_2_account_agent.services.abuse_guard import AbuseGuardService
from layer_2_account_agent.services.auth_provider import AuthProvider
from layer_2_account_agent.services.billing_provider import BillingProvider
from layer_2_account_agent.services.idempotency_service import IdempotencyService
from layer_2_account_agent.services.identity_service import IdentityService
from layer_2_account_agent.services.risk_engine import RiskEngineService
from layer_2_account_agent.services.subclassifier import SubclassifierService
from layer_2_account_agent.services.takeover_detector import TakeoverDetectorService
from layer_2_account_agent.services.verification_policy import VerificationPolicyService

# Orchestration Components
from layer_2_account_agent.account_graph import build_account_graph
from layer_2_account_agent.state_factory import AccountStateFactory
from layer_2_account_agent.mapper.final_responce import build_account_output
from platform_orchestration.adapters.account_input_adapter import AccountInputAdapter

logger = logging.getLogger(__name__)

def build_account(container):
    """Wires the Account Agent and its dependencies into the global container."""
    logger.info("Building Layer 2: Account Agent...")

    # 1. INITIALIZE REPOSITORIES (Sharing the master DB session)
    container.account_repo = AccountRepository(session=container.db)
    container.billing_repo = BillingRepository(session=container.db)
    container.customer_repo = CustomerRepository(session=container.db)
    container.security_repo = SecurityAuditRepository(session=container.db)

    # 2. INITIALIZE SERVICES (Injecting Repos and LLMs where required)
    container.abuse_guard = AbuseGuardService()
    container.auth_provider = AuthProvider(account_repo=container.account_repo)
    container.billing_provider = BillingProvider(account_repo=container.account_repo)
    container.idempotency_service = IdempotencyService(security_repo=container.security_repo)
    container.identity_service = IdentityService(
        customer_repo=container.customer_repo, 
        account_repo=container.account_repo
    )
    container.risk_engine = RiskEngineService()
    container.subclassifier = SubclassifierService(llm=container.llm)
    container.takeover_detector = TakeoverDetectorService()
    container.verification_policy = VerificationPolicyService()

    # 3. BUILD GRAPH (Passing the container so nodes can access services)
    container.account_graph = build_account_graph(container)

    # 4. ATTACH UTILITIES
    container.account_input_adapter = AccountInputAdapter()
    container.account_state_factory = AccountStateFactory()
    container.build_account_output = build_account_output

    # 5. REGISTRY
    if not hasattr(container, "specialist_graphs"):
        container.specialist_graphs = {}
    if not hasattr(container, "output_mappers"):
        container.output_mappers = {}

    container.specialist_graphs["account_agent"] = container.account_graph
    container.output_mappers["account_agent"] = build_account_output