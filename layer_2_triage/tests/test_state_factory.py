import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.state_factory import TriageStateFactory

def test_triage_state_initialization():
    """
    Validates that the StateFactory correctly transforms Layer 1 output
    into a strictly typed TriageState.
    """
    
   
    l1_mock_data = {
        "ticket_id": "TICKET-2001",
        "customer_email": "rahul@gmail.com",
        "intent": "refund_request",
        "confidence": 92, 
        "sentiment": "angry",
        "urgency": "high",
        "entities": {
            "order_id": "ORD-5521",
            "product_name": "headphones",
            "purchase_date": "5 days ago"
        }
    }

    print("🚀 Starting StateFactory Validation Test...")

    
    state = TriageStateFactory.create_triage_state(l1_mock_data)

   
    try:
       
        assert state["ticket_id"] == "TICKET-2001"
        assert state["customer_email"] == "rahul@gmail.com"
        
        
        assert state["supervisor_confidence"] == 0.92
        
       
        assert state["entities"]["order_id"] == "ORD-5521"
        assert state["entities"]["product_name"] == "headphones"
        
        assert state["next_agent"] is None
        
        
        assert len(state["workflow_logs"]) == 1
        assert state["workflow_logs"][0]["node"] == "state_factory"
        assert isinstance(state["workflow_logs"][0]["data"], dict)
        
     
        assert state["escalation_required"] is False
        assert state["ltv"] == 0.0
        assert isinstance(state["created_at"], datetime)

        print("✅ SUCCESS: TriageState initialized with 100% accuracy.")
        print(f"📊 Initialized at: {state['created_at']}")
        print(f"🔍 Audit Log: {state['workflow_logs'][0]['message']}")

    except AssertionError as e:
        print(f"❌ TEST FAILED: State attribute mismatch. {e}")
    except KeyError as e:
        print(f"❌ TEST FAILED: Missing expected key in state: {e}")

if __name__ == "__main__":
    test_triage_state_initialization()