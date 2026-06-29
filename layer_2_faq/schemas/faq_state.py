from typing import TypedDict, Optional, List, Dict, Any, Annotated
from datetime import datetime
from operator import add

class FAQState(TypedDict):
    """
    Production-hardened State schema for the FAQ Specialist Agent.
    Synchronized with validate_contract_node to support first-class 
    escalation and auditability.
    """
    ticket: Dict[str, Any]             
    entities: Dict[str, Any]           
    ticket_id: str                      
    customer_email: str                 
    customer_id: int                    
    assigned_agent: str                
    decision_target: Optional[str]      

   
    initial_intent: str                 
    initial_urgency: str                
    initial_sentiment: str              
    supervisor_confidence: float        
    
    customer_tier: str                  
    ltv: float                          
    unresolved_repeat_count: int        
    total_tickets: int                  
    total_escalations: int              
    last_sentiment: str                 
    
    order_context: Optional[Dict[str, Any]] 
    
    final_priority: str                 
    sla_duration_hours: int             
    sla_deadline: datetime              

  
    rewritten_query: Optional[str]      
    query_intent: Optional[str]         
    ambiguity_detected: Optional[bool]  
    clarification_question: Optional[str] 
    clarification_response: Optional[str] 

    retrieval_strategy: Optional[str]   
    metadata_filters: Optional[Dict[str, Any]]

  
    retrieved_child_chunks: List[Dict[str, Any]]
    similarity_scores: List[float]
    reranked_chunks: List[Dict[str, Any]]
    rerank_scores: List[float]                
    expanded_parent_context: List[Dict[str, Any]]

    grounded_answer: Optional[str]      
    citations: Annotated[List[Dict[str, Any]], add] 
    generation_metadata: Optional[Dict[str, Any]] 

   
    verifier_score: Optional[float]    
    verifier_reason: Optional[str]      
    retry_count: int                    
    correction_note: Optional[str]      
    attempt_history: Annotated[List[Dict[str, Any]], add]

    
    confidence_score: Optional[float]
    escalation_required: bool          
    escalation_reason: Optional[str]   

   
    feedback_status: Optional[str]      
    feedback_source: Optional[str]       
    chunk_quality_updates: Optional[List[Dict[str, Any]]]
    knowledge_gap_detected: Optional[bool] 
    knowledge_gap_reason: Optional[str]  

   
    workflow_logs: Annotated[List[Dict[str, Any]], add] 
    errors: Annotated[List[str], add]   
    timings: Dict[str, float]         
    current_node: str                   
    created_at: datetime                
    updated_at: datetime