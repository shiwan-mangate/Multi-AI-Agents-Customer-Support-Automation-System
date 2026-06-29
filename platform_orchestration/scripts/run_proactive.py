# platform_orchestration/scripts/run_proactive.py

import sys
import os
import uuid
import time  # <-- Added for daemon sleeping

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging
from platform_orchestration.dependency_container import DependencyContainer
from layer_2_proactive_agent.services.crm_signal_service import CRMSignalService
from layer_2_proactive_agent.schemas.enums import OutreachStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("proactive_scanner")

def main():
    logger.info("Initializing Dependency Container (One-Time Setup)...")
    
    # 🟢 Initialize heavy models and graphs ONLY ONCE
    container = DependencyContainer()
    signal_service = CRMSignalService(container.crm_customer_profile_repository)
    
    # Fetch sleep interval from environment variables, defaulting to 60 seconds
    scan_interval = int(os.environ.get("PROACTIVE_SCAN_INTERVAL", 60))
    logger.info(f"Proactive Scanner Daemon Online. Polling CRM every {scan_interval} seconds.")

    # 🟢 Infinite Daemon Loop
    while True:
        try:
            logger.info("Starting Proactive CRM Signal Scan...")
            raw_signals = signal_service.detect_signals()
            
            signals = []
            for s in raw_signals:
                is_suppressed, _ = container.proactive_suppression_service.should_suppress(
                    customer_id=s.customer_id,
                    signal_type=s.signal_type
                )
                if not is_suppressed:
                    signals.append(s)

            if not signals:
                logger.info(f"Scan complete. {len(raw_signals)} detected, 0 actionable (all suppressed or empty).")
            else:
                logger.info(f"Processing {len(signals)} actionable signals...")

                for signal in signals:
                    logger.info(f"Invoking Graph for Signal: {signal.signal_id} | Customer {signal.customer_id}")
                    
                    try:
                        initial_state = container.proactive_state_factory.create(signal)
                        config = {"configurable": {"thread_id": signal.signal_id}}
                        
                        final_state = container.proactive_graph.invoke(initial_state, config=config)
                        
                        output = final_state.get("output")
                        
                        if not output:
                            logger.error(f"Graph failed to produce ProactiveOutput for {signal.signal_id}")
                            continue

                        status_val = output.status.value if hasattr(output.status, "value") else str(output.status)

                        if status_val == OutreachStatus.ESCALATION_REQUIRED.value:
                            logger.info(f"CRITICAL RISK: Routing {signal.signal_id} to Escalation Agent.")
                            handoff = output.escalation_handoff
                            
                            escalation_payload = {
                                "ticket_id": handoff.ticket_id,
                                "customer_id": handoff.customer_id,
                                "customer_email": handoff.customer_email,
                                "channel": "system_proactive",
                                "message_raw": handoff.message_raw,
                                "message_english": handoff.message_english,
                                "intent": handoff.initial_intent,
                                "urgency": handoff.initial_urgency,
                                "sentiment": handoff.initial_sentiment,
                                "source_agent": "proactive_agent",
                                
                                # 🟢 FIX: We now provide the exact keys the validate_contract_node demands
                                "ticket": {
                                    "ticket_id": handoff.ticket_id,
                                    "customer_id": handoff.customer_id,
                                    "channel": "system_proactive",
                                    "message_raw": handoff.message_raw,        
                                    "message_english": handoff.message_english 
                                }
                            }
                            
                            esc_state = container.escalation_state_factory.from_payload(escalation_payload)
                            esc_config = {"configurable": {"thread_id": handoff.ticket_id}}
                            
                            esc_final_state = container.escalation_graph.invoke(esc_state, config=esc_config)
                            
                            unique_esc_id = f"ESC-{uuid.uuid4().hex[:8]}"
                            
                            container.workflow_repository.save_active_workflow(
                                workflow_id=unique_esc_id,
                                ticket_id=handoff.ticket_id,
                                thread_id=handoff.ticket_id,
                                agent_type="escalation_agent",
                                status="PENDING_REVIEW"
                            )
                            logger.info(f"⏸️ Ticket {handoff.ticket_id} paused for Human Manager Review (Workflow: {unique_esc_id}).")

                        else:
                            logger.info(f"Autonomous handling ({status_val}). Dropping to CRM Outbox.")
                            
                            crm_event = container.proactive_adapter.to_crm_event(output)
                            
                            container.crm_event_repository.create_event(crm_event)
                            try:
                                container.db.commit()
                            except Exception:
                                container.db.rollback()
                                raise
                            logger.info(f" Queued CRM Event for {signal.signal_id}")

                    except Exception as exc:
                        logger.exception(f" Failed to process signal {signal.signal_id}: {exc}")
                        container.db.rollback()

        except Exception as global_exc:
            # Catch overarching errors (e.g., Database disconnected during detect_signals)
            logger.error(f"Critical error during proactive scan cycle: {global_exc}")
            try:
                container.db.rollback()
            except Exception:
                pass

        # 🟢 Sleep to keep container alive and prevent hammering the DB
        logger.info(f"Sleeping for {scan_interval} seconds before next scan cycle...")
        time.sleep(scan_interval)

if __name__ == "__main__":
    main()