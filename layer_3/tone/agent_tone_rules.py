"""
Configuration file for agent-specific communication behavior.
Maps specific Layer 2 Specialist Agents to their expected baseline personas.
Used by the ToneAdjustmentService to combine agent persona with cultural expectations.
"""

AGENT_TONE_RULES = {
    "faq_agent": {
        "tone": "helpful",
        "empathy": False,
        "apology": False,
        "formality": "neutral"
    },
    
    "refund_agent": {
        "tone": "professional",
        "empathy": True,
        "apology": False,
        "formality": "neutral"
    },
    
    "account_agent": {
        "tone": "professional",
        "empathy": False,
        "apology": False,
        "formality": "neutral"
    },
    
    "faq_agent": {
    "tone": "professional",
    "empathy": True,
    "apology": True,
    "formality": "neutral"
},
    
    "escalation_agent": {
        "tone": "empathetic",
        "empathy": True,
        "apology": True,
        "formality": "formal"
    },
    
    "proactive_agent": {
        "tone": "friendly",
        "empathy": False,
        "apology": False,
        "formality": "warm"
    }
}