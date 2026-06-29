import logging
import uuid
from typing import List, Any
from fastapi import HTTPException, status, BackgroundTasks
from platform_orchestration.dependency_container import DependencyContainer

from layer_2_proactive_agent.services.crm_signal_service import CRMSignalService
from layer_2_proactive_agent.schemas.enums import OutreachStatus

from layer_2_proactive_agent.database.model.proactive_event_record import (
    ProactiveEventRecord,
)

from api.schemas.proactive_responses import (
    ProactiveHistoryResponse,
    ProactiveEventItem,
    ActiveSuppressionsResponse,
    SuppressionItem,
    ActiveSignalsResponse,
    DetectedSignalItem,
    RecentEventsResponse,
    RunScanResponse
)

logger = logging.getLogger("api_proactive_service")

class ProactiveService:
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.event_repo = self.container.proactive_event_repository
        self.outreach_repo = self.container.proactive_outreach_repository
        self.signal_service = CRMSignalService(self.container.crm_customer_profile_repository)

    def get_customer_history(self, customer_id: int, request_id: str = "unknown") -> ProactiveHistoryResponse:
        logger.info(f"[{request_id}] Fetching proactive history for Customer {customer_id}")
        try:
            records = self.event_repo.get_customer_history(customer_id)
            items = [
                ProactiveEventItem(
                    workflow_id=r.workflow_id,
                    customer_id=r.customer_id,
                    signal_type=r.signal_type,
                    # FIX: Correctly mapping to the 'decision' column in the ORM
                    outreach_status=r.decision,
                    created_at=r.created_at,
                    metadata={
                        "decision": getattr(r, "decision", None),
                        "risk_score": getattr(r, "risk_score", None)
                    }
                ) for r in records
            ]
            return ProactiveHistoryResponse(
                customer_id=customer_id, total_events=len(items), events=items
            )
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch history: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error retrieving event history.")

    def get_active_suppressions(self, customer_id: int, request_id: str = "unknown") -> ActiveSuppressionsResponse:
        logger.info(f"[{request_id}] Fetching active suppressions for Customer {customer_id}")
        try:
            records = self.outreach_repo.get_active_suppressions(customer_id)
            items = [
                SuppressionItem(
                    customer_id=r.customer_id,
                    signal_type=r.signal_type,
                    reason=getattr(r, "decision", "SUPPRESSED"),
                    expires_at=r.expires_at
                ) for r in records
            ]
            return ActiveSuppressionsResponse(
                customer_id=customer_id, active_cooldowns=len(items), suppressions=items
            )
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch suppressions: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error retrieving active suppressions.")

    def get_active_signals(self, request_id: str = "unknown") -> ActiveSignalsResponse:
        logger.info(f"[{request_id}] Running live signal detection radar")
        try:
            raw_signals = self.signal_service.detect_signals()
            items = [
                DetectedSignalItem(
                    signal_id=s.signal_id,
                    customer_id=s.customer_id,
                    signal_type=s.signal_type.value if hasattr(s.signal_type, "value") else str(s.signal_type),
                    signal_source=s.signal_source.value if hasattr(s.signal_source, "value") else str(s.signal_source),
                    signal_context=s.signal_context
                ) for s in raw_signals
            ]
            return ActiveSignalsResponse(total_detected=len(items), signals=items)
        except Exception as e:
            logger.error(f"[{request_id}] Live signal detection failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error executing live CRM signal detection.")

    def get_recent_events(self, limit: int = 100, request_id: str = "unknown") -> RecentEventsResponse:
        logger.info(f"[{request_id}] Fetching recent global proactive events")
        try:
            records = self.event_repo.get_recent_events(limit=limit)
            items = [
                ProactiveEventItem(
                    workflow_id=r.workflow_id,
                    customer_id=r.customer_id,
                    signal_type=r.signal_type,
                    # FIX: Correctly mapping to the 'decision' column in the ORM
                    outreach_status=r.decision,
                    created_at=r.created_at,
                    metadata={
                        "decision": getattr(r, "decision", None)
                    }
                ) for r in records
            ]
            return RecentEventsResponse(total_events=len(items), events=items)
        except Exception as e:
            logger.error(f"[{request_id}] Failed to fetch global events: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Database error retrieving recent proactive events.")

    def _execute_proactive_scan(self, actionable_signals: List[Any], request_id: str):
        """Background task that processes the provided actionable signals."""
        logger.info(f"[{request_id}] Background Scan Execution Started for {len(actionable_signals)} signals")
        
        try:
            for signal in actionable_signals:
                try:
                    initial_state = self.container.proactive_state_factory.create(signal)
                    config = {"configurable": {"thread_id": signal.signal_id}}
                    
                    final_state = self.container.proactive_graph.invoke(initial_state, config=config)
                    output = final_state.get("output")
                    
                    if not output:
                        continue
                    
                    risk_level = "unknown"
                    if getattr(output, "risk_assessment", None):
                        risk_level = output.risk_assessment.risk_level.value if hasattr(output.risk_assessment.risk_level, "value") else str(output.risk_assessment.risk_level)

                    event_record = ProactiveEventRecord(
                        workflow_id=output.workflow_id,
                        signal_id=signal.signal_id,
                        customer_id=signal.customer_id,
                        signal_type=signal.signal_type.value if hasattr(signal.signal_type, "value") else str(signal.signal_type),
                        risk_level=risk_level,
                        decision=output.status.value if hasattr(output.status, "value") else str(output.status),
                        crm_event_id=""
                    )
                    
                    status_val = output.status.value if hasattr(output.status, "value") else str(output.status)
                    
                    if status_val == OutreachStatus.ESCALATION_REQUIRED.value:
                        handoff = output.escalation_handoff
                        unique_esc_id = f"ESC-{uuid.uuid4().hex[:8]}"
                        
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
                            "ticket": {
                                "ticket_id": handoff.ticket_id,
                                "customer_id": handoff.customer_id,
                                "channel": "system_proactive",
                                "message_raw": handoff.message_raw,
                                "message_english": handoff.message_english
                            }
                        }
                        
                        esc_state = self.container.escalation_state_factory.from_payload(escalation_payload)
                        esc_config = {"configurable": {"thread_id": handoff.ticket_id}}
                        
                        self.container.escalation_graph.invoke(esc_state, config=esc_config)
                        
                        self.container.workflow_repository.save_active_workflow(
                            workflow_id=unique_esc_id,
                            ticket_id=handoff.ticket_id,
                            thread_id=handoff.ticket_id,
                            agent_type="escalation_agent",
                            status="PENDING_REVIEW"
                        )
                        logger.info(f"[{request_id}] Escalation workflow {unique_esc_id} successfully invoked.")
                        
                        event_record.crm_event_id = "ESCALATION"
                        self.event_repo.save_event(event_record)
                        logger.info(
                            "[%s] Proactive Event Saved | Workflow=%s | Customer=%s",
                            request_id,
                            event_record.workflow_id,
                            event_record.customer_id
                        )

                    else:
                        crm_event = self.container.proactive_adapter.to_crm_event(output)
                        self.container.crm_event_repository.create_event(crm_event)
                        
                        event_record.crm_event_id = crm_event.event_id
                        self.event_repo.save_event(event_record)
                        logger.info(
                            "[%s] Proactive Event Saved | Workflow=%s | Customer=%s",
                            request_id,
                            event_record.workflow_id,
                            event_record.customer_id
                        )
                    
                    self.container.db.commit()

                except Exception as inner_e:
                    self.container.db.rollback()
                    logger.error(f"[{request_id}] Failed to process signal {signal.signal_id}: {inner_e}", exc_info=True)

            logger.info(f"[{request_id}] Background Scan Complete.")
            
        except Exception as e:
            logger.error(f"[{request_id}] Background Scan Fatal Error: {e}", exc_info=True)
            self.container.db.rollback()
        finally:
            self.container.db.close()

    def run_scan_async(self, background_tasks: BackgroundTasks, request_id: str) -> RunScanResponse:
        logger.info(f"[{request_id}] Triggering manual proactive scan")
        try:
            raw_signals = self.signal_service.detect_signals()
            
            actionable = []
            for s in raw_signals:
                is_suppressed, _ = self.container.proactive_suppression_service.should_suppress(
                    customer_id=s.customer_id, signal_type=s.signal_type
                )
                if not is_suppressed:
                    actionable.append(s)

            background_tasks.add_task(self._execute_proactive_scan, actionable, request_id)

            return RunScanResponse(
                status="PROCESSING",
                detail="Manual proactive scan queued and currently executing.",
                signals_detected=len(raw_signals),
                signals_dispatched=len(actionable)
            )
        except Exception as e:
            logger.error(f"[{request_id}] Failed to trigger manual scan: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to initialize the proactive scan.")