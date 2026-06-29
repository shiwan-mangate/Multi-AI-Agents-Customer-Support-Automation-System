# platform_orchestration/builders/build_faq.py

import os
import logging

from layer_2_faq.services.query_rewriter import QueryRewriterService
from layer_2_faq.services.vector_store import VectorStoreService
from layer_2_faq.services.reranker import RerankerService
from layer_2_faq.services.answer_generator import AnswerGeneratorService
from layer_2_faq.services.verifier import VerifyAnswerService

# Orchestration Components
from layer_2_faq.graphs.faq_graph import build_faq_graph 
from layer_2_faq.graphs.state_factory import FAQStateFactory
from layer_2_faq.ingestion.mapper.faq_final_responce import build_faq_output
from platform_orchestration.adapters.faq_input_adapter import FAQInputAdapter
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

def build_faq(container):
    """Wires the FAQ Agent and its AI Services into the global dependency container."""
    logger.info("Building Layer 2: FAQ Agent...")
    
    # 1. INITIALIZE HEAVY SERVICES ONLY ONCE
    container.answer_generator = AnswerGeneratorService(llm=container.llm)
    container.query_rewriter = QueryRewriterService(llm=container.llm)
    container.reranker = RerankerService(model_name="ms-marco-MiniLM-L-12-v2")
    
    # ✅ CONFIGURATION FIX: Fallback gracefully to env configurations 
    faq_db_url = os.getenv("FAQ_DATABASE_URL")
    
    container.vector_store = VectorStoreService(
        db_url=faq_db_url, 
        model_name="BAAI/bge-small-en-v1.5"
    )
    container.verifier = VerifyAnswerService(model_name="llama-3.3-70b-versatile")
    
    # 2. BUILD THE GRAPH BY PASSING THE CONTAINER
    container.faq_graph = build_faq_graph(container)
    
    # 3. ATTACH ROUTING UTILITIES
    container.faq_input_adapter = FAQInputAdapter()
    container.faq_state_factory = FAQStateFactory()
    container.build_faq_output = build_faq_output

    # 4. REGISTRY
    if not hasattr(container, "specialist_graphs"):
        container.specialist_graphs = {}
    if not hasattr(container, "output_mappers"):
        container.output_mappers = {}

    container.specialist_graphs["faq_agent"] = container.faq_graph
    container.output_mappers["faq_agent"] = build_faq_output
    
    logger.info("FAQ Agent successfully wired into container.")