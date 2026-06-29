import json
from datetime import datetime
from graphs.state_factory import TriageStateFactory
from graphs.triage_graph import build_triage_graph

def run_triage_test():
    # 1. Mock Layer 1 Payload (The "Input Signal")
    sample_ticket = {
        "ticket_id": "TKT-1001",
        "customer_email": "john@example.com",
        "intent": "refund_request",
        "urgency": "high",
        "sentiment": "frustrated",
        "confidence": 0.92, # Using float as per our refined parsing logic
        "entities": {
            "order_id": "1"
        },
        "ticket": {
            "channel": "email"
        }
    }

    print(f"🚀 Initializing Triage for Ticket: {sample_ticket['ticket_id']}")
    
    # 2. Initialize the TriageState via Factory
    # This prepares the Layer 2 schema from the Layer 1 raw data.
    initial_state = TriageStateFactory.create_triage_state(sample_ticket)

    # 3. Compile and Invoke the Graph
    triage_app = build_triage_graph()
    
    print("🧠 Orchestrating nodes...")
    # .invoke() runs the full linear chain START -> ... -> END
    final_state = triage_app.invoke(initial_state)

    # 4. Result Verification Report
    print("\n" + "="*50)
    print("🎯 TRIAGE EXECUTION COMPLETE")
    print("="*50)
    
    print(f"✅ Final Priority:   {final_state.get('final_priority')}")
    print(f"✅ SLA Commitment:   {final_state.get('sla_duration_hours')} Hours")
    print(f"✅ Final Score:      {final_state.get('final_score')}/10.0")
    print(f"✅ Next Agent:       {final_state.get('next_agent')}")
    print(f"✅ Escalation Reqd:  {final_state.get('escalation_required')}")
    
    if final_state.get("escalation_required"):
        print(f"⚠️ Escalation Reason: {final_state.get('escalation_reason')}")

    print("\n📋 WORKFLOW AUDIT TRAIL:")
    for log in final_state.get("workflow_logs", []):
        timestamp = log['timestamp'].split('T')[1].split('.')[0] # Clean time
        print(f"  [{timestamp}] {log['node']:<20} | {log['message']}")

    # 5. Insight Discovery
    print("\n💡 INSIGHT TAGS DETECTED:")
    print(f"  {', '.join(final_state.get('insight_tags', [])) if final_state.get('insight_tags') else 'None'}")
    
    print("="*50)

if __name__ == "__main__":
    try:
        run_triage_test()
    except Exception as e:
        print(f"❌ TEST CRASHED: {str(e)}")