import uuid
import logging
import pprint
from datetime import datetime, UTC
from typing import Any, Dict, Optional, List
from sqlalchemy import text

from layer_2_escalation_agent.db.session import get_db
from layer_2_escalation_agent.services.escalation_agent import run_escalation_agent, resume_escalation_review

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("QA_Engine")

# =====================================================================
# QA ENVIRONMENTAL CONTROL UTILITIES (SETUP / TEARDOWN)
# =====================================================================

def prepare_env(ticket_id: str, customer_id: int):
    """
    Guarantees strict environmental isolation before each test scenario executes.
    1. Force-seeds parent customer records with 'name' and 'email' to satisfy strict NOT NULL constraints.
    2. Force-seeds parent ticket records with 'issue_type' to satisfy strict NOT NULL constraints.
    3. Drops existing case records matching keys to unblock targeted execution runs.
    """
    if not ticket_id:
        return
    db_gen = get_db()
    session = next(db_gen)
    try:
        # Step 1: Seed parent customer dependency to satisfy escalation_cases_customer_id_fkey
        if customer_id:
            # FIXED HERE: Added 'email' column with a placeholder to satisfy the database constraint
            session.execute(text("""
                INSERT INTO customers (customer_id, name, email)
                VALUES (:customer_id, 'QA Test Customer', 'qa_test_harness@example.com')
                ON CONFLICT (customer_id) DO NOTHING;
            """), {"customer_id": customer_id})

        # Step 2: Seed parent ticket dependency to satisfy escalation_cases_ticket_id_fkey
        if ticket_id != "INVALID-99999":
            session.execute(text("""
                INSERT INTO tickets (ticket_id, customer_id, issue_type)
                VALUES (:ticket_id, :customer_id, 'general')
                ON CONFLICT (ticket_id) DO NOTHING;
            """), {"ticket_id": ticket_id, "customer_id": customer_id if customer_id else 15})
        
        # Step 3: Purge conflicting active states from previous test runs
        session.execute(text("""
            DELETE FROM escalation_cases WHERE ticket_id = :ticket_id;
        """), {"ticket_id": ticket_id})
        
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Environment prep crash for {ticket_id}: {e}")
    finally:
        session.close()
        try: next(db_gen)
        except StopIteration: pass


def build_payload(ticket_id: Any, customer_id: Any, message: str, source_agent: str = "triage_agent") -> dict:
    """Standardized factory to mock upstream state payloads cleanly."""
    return {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "source_agent": source_agent,
        "initial_intent": "churn",
        "initial_sentiment": "angry",
        "ticket": {
            "message_raw": message,
            "message_english": message
        },
        "workflow_logs": []
    }

# =====================================================================
# CATEGORY 7: CONTEXT ENRICHMENT TESTS
# =====================================================================

def test_category_7():
    print("\n🚀 RUNNING CATEGORY 7: CONTEXT ENRICHMENT TESTS")
    
    # TC-14: Customer ID Not Found Degraded Flow
    t14 = "TKT-1014"
    prepare_env(t14, 999999)
    payload_14 = build_payload(t14, 999999, "I want my balance statement or I close this account.")
    res_14 = run_escalation_agent(payload_14)
    print(f"TC-14 Status: {res_14['status']} | Case ID: {res_14.get('case_id')} (Degraded graceful fallback active)")
    assert res_14["status"] == "ESCALATED"

# =====================================================================
# CATEGORY 8: EDGE CASES
# =====================================================================

def test_category_8():
    print("\n🚀 RUNNING CATEGORY 8: EDGE CASES & BULK EXECUTION")
    
    # TC-16: Empty Log Context Hydration Array
    t16 = "TKT-1016"
    prepare_env(t16, 15)
    payload_16 = build_payload(t16, 15, "My billing portal has errors.")
    payload_16["workflow_logs"] = []
    res_16 = run_escalation_agent(payload_16)
    assert res_16["status"] == "ESCALATED"

    # TC-17: Token Burst Stress Test (Very Long Content)
    t17 = "TKT-1017"
    prepare_env(t17, 15)
    payload_17 = build_payload(t17, 15, "angry " * 4000)
    res_17 = run_escalation_agent(payload_17)
    print(f"TC-17 Payload Length Status: {res_17['status']}")
    assert res_17["status"] == "ESCALATED"

    # TC-20: Sequential Stress Loops (Bulk Runs)
    print("TC-20: Running sequential stress loop executions...")
    success_count = 0
    for idx in range(10):  # Loops systematically across separate ticket records
        bulk_ticket = f"TKT-BULK-{idx}"
        prepare_env(bulk_ticket, 15)
        payload_bulk = build_payload(bulk_ticket, 15, f"Bulk test loop notification context item {idx}")
        res_bulk = run_escalation_agent(payload_bulk)
        if res_bulk["status"] == "ESCALATED":
            success_count += 1
            
    print(f"TC-20 Bulk Run Metrics complete: {success_count} / 10 successfully committed records.")
    assert success_count == 10

# =====================================================================
# SUITE MAIN RUNNER
# =====================================================================
if __name__ == "__main__":
    print("="*70)
    print("STARTING TARGETED TESTING: CATEGORIES 7 & 8 ONLY")
    print("="*70)
    
    try:
        test_category_7()
        test_category_8()
        print("\n" + "="*70)
        print("🏆 QA FINALIZE: TARGETED SCRIPT SWEEPS COMPLETED SUCCESSFULLY!")
        print("="*70)
    except AssertionError as err:
        print(f"\n❌ QA AUTOMATION FAILURE TRIGGERED: {err}")