import logging
import json
from platform_orchestration.dependency_container import DependencyContainer
from layer_2_triage.mapper.triage_output_adapter import build_triage_output
from langgraph.types import Command
import time
import psycopg
# Must import the CRM Schema to perform the quarantine validation check!
from crm_agent.schemas.crm_event import CRMResolvedEvent

logger = logging.getLogger("inbound_ticket_pipeline")

# ==========================================
# 🟢 GLOBAL STATE HELPERS
# ==========================================
PAUSED_STATES = [
    "HUMAN_REVIEW_REQUIRED",
    "PENDING",
    "PENDING_REVIEW",
    "PENDING_CLARIFICATION",
    "clarification_required"
]

def is_paused_status(status: str | None) -> bool:
    """Centralizes pause logic for easy V2 Enum migration."""
    return status in PAUSED_STATES


class InboundTicketPipeline:
    def __init__(self, container: DependencyContainer):
        self.container = container

    # ==========================================
    # 🟢 CRM INGESTION HELPER
    # ==========================================
    def _trace(self,ticket_id: str,stage: str,status: str,details: str | None = None,):
        try:
            self.container.workflow_trace_repository.create(
                ticket_id=ticket_id,
                stage=stage,
                status=status,
                details=details,
            )
            self.container.db.commit()

        except Exception:
            self.container.db.rollback()
            raise
        
    def _enqueue_crm_event(self, agent_type: str, agent_output: dict, global_context: dict):
        """Passes specialist outputs through adapters and into the async CRM database queue."""
        adapter = getattr(self.container, "crm_adapters", {}).get(agent_type)
        
        if not adapter:
            logger.warning(f"No CRM adapter registered for {agent_type}. Skipping CRM enqueue.")
            return

        try:
            if not agent_output:
                raise ValueError(
                    f"CRM received empty output from {agent_type}"
                )

            if (agent_type == "escalation_agent"and isinstance(agent_output, dict)and agent_output.get("response") is None):
                raise ValueError(
                    "CRM received escalation output without response."
                )

            safe_output = json.loads(json.dumps(
                agent_output, 
                default=lambda x: x.value if hasattr(x, 'value') else str(x)
            ))

            raw_crm_event = adapter.to_crm_event(
                agent_output=safe_output,
                global_context=global_context
            )
            
            validated_crm_event = CRMResolvedEvent.model_validate(
                raw_crm_event.model_dump(mode="json")
            )
            
            self.container.crm_event_repository.create_event(validated_crm_event)
            
            try:
                self.container.db.commit()
            except Exception:
                self.container.db.rollback()
                raise
            
            logger.info(f"✅ CRM ASYNC HANDOFF | Queued event {validated_crm_event.event.event_id} for Ticket {validated_crm_event.ticket.ticket_id}")
            
        except Exception as e:
            self.container.db.rollback()
            logger.error(f"❌ CRM Handoff Failed: {e}")
            raise e

    def process(self, data: dict) -> dict:
        logger.info("Initializing inbound pipeline processing sequence...")

        def enum_safe(val):
            """Safely extracts string values from Enums or recovered Checkpoint strings."""
            if val is None:
                return None
            return val.value if hasattr(val, "value") else str(val)
        
        ticket_id = data.get("ticket_id", "UNKNOWN")
        self._trace(
                ticket_id,
                "layer0-Normalization",
                "RUNNING"
            )

        unified_ticket = self.container.layer0_main(data=data)
        ticket_id = unified_ticket.ticket_id
        self._trace(
            ticket_id,
            "layer0-Normalization",
            "COMPLETE"
        )

        try:
            from sqlalchemy import text
            self.container.db.execute(text("""
                INSERT INTO tickets (ticket_id, customer_id, issue_type, created_at) 
                VALUES (:tid, :cid, 'inbound_orchestration', NOW()) 
                ON CONFLICT (ticket_id) DO NOTHING;
            """), {"tid": unified_ticket.ticket_id, "cid": unified_ticket.customer_id})
            self.container.db.commit()
            logger.info(f"Database pre-seeded with ticket {unified_ticket.ticket_id} successfully.")
        except Exception as e:
            self.container.db.rollback()
            logger.error(f"FATAL ORCHESTRATION ERROR: Could not seed ticket {unified_ticket.ticket_id} in DB: {e}")

        self._trace(
            ticket_id,
            "layer0-Translation",
            "RUNNING"
        )
        supervisor_payload = self.container.layer0_translation_adapter.to_supervisor_payload(unified_ticket)
        self._trace(
            ticket_id,
            "layer0-Translation",
            "COMPLETE"
        )

        self._trace(
            ticket_id,
            "layer1-Supervisor-Agent",
            "RUNNING"
        )
        supervisor_result = self.container.supervisor_node(supervisor_payload)
        self._trace(
            ticket_id,
            "layer1-Supervisor-Agent",
            "COMPLETE"
        )

        # --- LAYER 2 TRIAGE INTEGRATION ---
        self._trace(
            ticket_id,
            "layer2-Triage-Agent",
            "RUNNING"
        )
        customer_data = supervisor_payload.get("customer", {})
        triage_input = {
            "ticket_id": supervisor_result.ticket_id,
            "channel": supervisor_payload.get("metadata", {}).get("channel", "email"),
            "customer_id": customer_data.get("customer_id"),
            "customer_email": customer_data.get("email", ""),
            "customer_tier": customer_data.get("tier", "standard"),
            "ltv": customer_data.get("lifetime_value", 0.0),
            "message_raw": supervisor_payload.get("message", {}).get("original", ""), 
            "message_english": supervisor_payload.get("message", {}).get("normalized", ""),
            "intent": supervisor_result.intent,
            "urgency": supervisor_result.urgency,
            "sentiment": supervisor_result.sentiment,
            "confidence": supervisor_result.confidence,
            "entities": supervisor_result.entities
        }

        triage_state = self.container.triage_state_factory.create_triage_state(triage_input)
        config = {"configurable": {"thread_id": supervisor_result.ticket_id}}

        logger.warning("Pool Stats: %s", self.container.pg_pool.get_stats())

        conn = self.container.pg_pool.getconn()

        logger.warning(
            "CHECKPOINT TEST CONNECTION OK"
        )
        self.container.pg_pool.putconn(conn)


        logger.warning("=== TESTING PSYCOPG POOL ===")

        try:
            with self.container.pg_pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT current_database(), now();")
                    logger.warning(cur.fetchone())
        except Exception:
            logger.exception("POOL FAILED")

        try:
            logger.warning("BEFORE INVOKE")
            logger.warning("POOL ID = %s", id(self.container.pg_pool))
            logger.warning("CHECKPOINTER ID = %s", id(self.container.checkpointer))

            final_triage_state = self.container.triage_graph.invoke(triage_state, config=config)

            logger.warning("AFTER INVOKE")
        except psycopg.errors.AdminShutdown:
            logger.warning("Checkpoint connection died. Rebuilding container.")
            raise

        triage_output = build_triage_output(final_triage_state)
        self._trace(
            ticket_id,
            "layer2-Triage-Agent",
            "COMPLETE"
        )

        # --- SPECIALIST ROUTING ---
        self._trace(
            ticket_id,
            "layer2-Specialist-Routing",
            "RUNNING"
        )
        target_agent = (
            triage_output.get("next_agent")
            if isinstance(triage_output, dict)
            else getattr(triage_output, "next_agent", None)
        )

        logger.warning("FULL TRIAGE OUTPUT = %s", triage_output)
        logger.warning(
            "TRIAGE DEBUG | order_context=%s | escalation_required=%s | escalation_reason=%s | next_agent=%s",
            triage_output.get("order_context"),
            triage_output.get("escalation_required"),
            triage_output.get("escalation_reason"),
            triage_output.get("next_agent")
        )
        logger.warning("TRIAGE ROUTING DECISION | next_agent=%s", target_agent)
        self._trace(
            ticket_id,
            "layer2-Specialist-Routing",
            "COMPLETE"
        )
        selected_graph = self.container.get_graph(target_agent)
        
        specialist_result = None
        is_paused = False

        if target_agent == "refund_agent" and selected_graph:
            self._trace(
                ticket_id,
                "layer2-Refund-Agent",
                "RUNNING"
            )
            logger.info("Executing Refund Agent Workflow...")
            refund_request = self.container.refund_input_adapter.build_refund_request(triage_output=triage_output, unified_ticket=unified_ticket)
            idempotency_key = f"{refund_request.ticket_id}_{refund_request.order_id}"
            refund_state = self.container.refund_state_factory(request=refund_request, idempotency_key=idempotency_key)
            start = time.perf_counter()
            refund_final_state = selected_graph.invoke(refund_state, config={"configurable": {"thread_id": refund_request.ticket_id}})
            duration_ms = int((time.perf_counter() - start) * 1000)
            refund_final_state["duration_ms"] = duration_ms
            specialist_result = self.container.build_refund_output(refund_final_state)

            if specialist_result and getattr(specialist_result, "review_status", None) == "PENDING":
                self.container.workflow_repository.save_active_workflow(workflow_id=specialist_result.workflow_id, ticket_id=refund_request.ticket_id, thread_id=refund_request.ticket_id, agent_type=target_agent, status="PENDING_REVIEW")

            self._trace(
                ticket_id,
                "layer2-Refund-Agent",
                "COMPLETE"
            )
        elif target_agent == "faq_agent" and selected_graph:
            self._trace(
                ticket_id,
                "layer2-FAQ-Agent",
                "RUNNING"
            )
            logger.info("Executing FAQ Agent Workflow...")
            faq_payload = self.container.faq_input_adapter.build_payload(triage_output=triage_output, unified_ticket=unified_ticket)
            faq_state = self.container.faq_state_factory.from_triage_payload(faq_payload)
            start  = time.perf_counter()
            faq_final_state = selected_graph.invoke(faq_state, config={"configurable": {"thread_id": faq_payload["ticket_id"]}})
            duration_ms = int((time.perf_counter() - start) * 1000)
            faq_final_state["duration_ms"] = duration_ms
            specialist_result = self.container.build_faq_output(faq_final_state)

            if specialist_result and getattr(specialist_result, "status", None) == "clarification_required":
                self.container.workflow_repository.save_active_workflow(workflow_id=f"FAQ-{faq_payload['ticket_id']}", ticket_id=faq_payload["ticket_id"], thread_id=faq_payload["ticket_id"], agent_type=target_agent, status="PENDING_CLARIFICATION")
            
            self._trace(
                ticket_id,
                "layer2-FAQ-Agent",
                "COMPLETE"
            )
        elif target_agent == "account_agent" and selected_graph:
            self._trace(
                ticket_id,
                "layer2-Account-Agent",
                "RUNNING"
            )
            logger.info("Executing Account Agent Workflow...")
            account_payload = self.container.account_input_adapter.build_payload(triage_output=triage_output, unified_ticket=unified_ticket)
            account_state = self.container.account_state_factory.from_triage_output(account_payload)
            start = time.perf_counter()
            account_final_state = selected_graph.invoke(account_state, config={"configurable": {"thread_id": account_payload["ticket_id"]}})
            duration_ms = int((time.perf_counter() - start) * 1000)
            account_final_state["duration_ms"] = duration_ms
            specialist_result = self.container.build_account_output(account_final_state)
            
            if specialist_result and getattr(specialist_result, "status", None) == "clarification_required":
                self.container.workflow_repository.save_active_workflow(workflow_id=f"ACC-{account_payload['ticket_id']}", ticket_id=account_payload["ticket_id"], thread_id=account_payload["ticket_id"], agent_type=target_agent, status="PENDING_CLARIFICATION")
            
            self._trace(
                ticket_id,
                "layer2-Account-Agent",
                "COMPLETE"
            )
        elif target_agent == "escalation_agent" and selected_graph:
            self._trace(
                ticket_id,
                "layer2-Escalation-Agent",
                "RUNNING"
            )
            logger.info("Executing Escalation Agent Workflow...")
            escalation_payload = self.container.escalation_input_adapter.build_payload(triage_output=triage_output, unified_ticket=unified_ticket, source_agent="triage_agent")
            escalation_state = self.container.escalation_state_factory.from_payload(escalation_payload)
            config = {"configurable": {"thread_id": escalation_payload["ticket_id"]}}
            start = time.perf_counter()
            escalation_final_state = selected_graph.invoke(escalation_state, config=config)
            
            duration_ms = int((time.perf_counter() - start) * 1000)
            escalation_final_state["duration_ms"] = duration_ms
            current_snapshot = selected_graph.get_state(config)
            current_snapshot.values["duration_ms"] = duration_ms
            
            is_paused = len(current_snapshot.next) > 0

            review_payload = None

            if is_paused:
                self._trace(
                    ticket_id,
                    "Human-Manager-Review",
                    "WAITING"
                )
                values = current_snapshot.values
                
                risk_assessment = values.get("risk_assessment")
                routing_dec = values.get("routing_decision")
                human_brief = values.get("human_brief")
                
                review_payload = {
                    "ticket_id": values.get("ticket_id"),
                    "customer_id": values.get("customer_id"),
                    "risk_level": enum_safe(getattr(risk_assessment, "level", None)),
                    "assigned_team": getattr(routing_dec, "assigned_team", "general_support"),
                    "human_brief": (
                        human_brief.model_dump(mode="json")
                        if hasattr(human_brief, "model_dump")
                        else human_brief
                    ),
                }

            state_for_mapper = current_snapshot.values if is_paused else escalation_final_state
            
            specialist_result = self.container.build_escalation_output(
                final_state=state_for_mapper,
                thread_id=escalation_payload["ticket_id"],
                review_payload=review_payload
            )
            self._trace(
                ticket_id,
                "layer2-Escalation-Agent",
                "COMPLETE"
            )

            logger.warning("ESCALATION OUTPUT STATUS = %s", specialist_result.status)

            if is_paused or enum_safe(getattr(specialist_result, "status", None)) == "HUMAN_REVIEW_REQUIRED":
                self.container.workflow_repository.save_active_workflow(
                    workflow_id=f"ESC-{escalation_payload['ticket_id']}", 
                    ticket_id=escalation_payload["ticket_id"], 
                    thread_id=escalation_payload["ticket_id"], 
                    agent_type=target_agent, 
                    status="PENDING_REVIEW"
                )

        # Extract Status and Apply the Helper Function safely
        if isinstance(specialist_result, dict):
            final_status = specialist_result.get("status") or specialist_result.get("review_status")
        else:
            final_status = getattr(specialist_result, "status", getattr(specialist_result, "review_status", None))

        is_paused_for_human = is_paused_status(final_status)

        # ==========================================
        # 🟢 1. LAYER 3 OUTBOUND TRANSLATION 
        # ==========================================
        self._trace(
            ticket_id,
            "layer3-Outbound-Translation",
            "RUNNING"
        )
        from layer_2_escalation_agent.schemas.escalation_output import EscalationAgentResponse

        spec_status = enum_safe(getattr(specialist_result, "status", None))
        
        if (
            isinstance(specialist_result, EscalationAgentResponse)
            and spec_status in ["IN_PROGRESS", "HUMAN_REVIEW_REQUIRED"]
        ):
            logger.info("Escalation awaiting human review. Skipping outbound response pipeline.")
            return {
                "unified_ticket": unified_ticket,
                "supervisor_payload": supervisor_payload,
                "supervisor_result": supervisor_result,
                "triage_result": triage_output,
                "specialist_result": specialist_result,
                "customer_response": None
            }

        customer_response = None
        if specialist_result and not is_paused_for_human:
            try:
                cid = customer_data.get("customer_id")
                if cid:
                    customer_response = self.container.outbound_response_pipeline.process(
                        specialist_result=specialist_result,
                        customer_id=cid
                    )
            except Exception as e:
                logger.error(f"Failed to execute Outbound Translation Pipeline: {e}", exc_info=True)
        self._trace(
            ticket_id,
            "layer3-Outbound-Translation",
            "COMPLETE"
        )
        
        # ==========================================
        # 🟢 2. CRM ASYNC HANDOFF 
        # ==========================================
        self._trace(
            ticket_id,
            "CRM-Handoff",
            "RUNNING"
        )
        if (
            isinstance(specialist_result, EscalationAgentResponse)
            and enum_safe(getattr(specialist_result, "status", None)) in ["IN_PROGRESS", "HUMAN_REVIEW_REQUIRED"]
        ):
            logger.info("Escalation pending review. CRM event skipped.")
        elif not is_paused_for_human and specialist_result is not None:
            # Safely convert dictionary entities to a list of keys for the CRM
            raw_entities = getattr(supervisor_result, "entities", [])
            if isinstance(raw_entities, dict):
                safe_issue_tags = [str(k) for k in raw_entities.keys()]
            elif isinstance(raw_entities, list):
                safe_issue_tags = [str(x) for x in raw_entities]
            else:
                safe_issue_tags = []

            # ---------------------------------------------------------
            # 🟢 UPDATED: Defensive Transcript Loading & Appending
            # ---------------------------------------------------------
            transcript = None
            try:
                # Use unified_ticket.ticket_id for absolute guaranteed consistency
                transcript = self.container.crm_transcript_repository.get_by_ticket_id(unified_ticket.ticket_id)
            except Exception as e:
                logger.warning(f"Could not load previous transcript for CRM sync on ticket {unified_ticket.ticket_id}: {e}")

            # Safe list wrapping in case messages is None
            if transcript:
                conversation_history = list(getattr(transcript, "messages", []) or [])
            else:
                conversation_history = []

            # 🟢 THE FIX: Robust Customer Message Extraction
            logger.warning(
                "UNIFIED TICKET DUMP = %s",
                unified_ticket.model_dump(mode="json") if hasattr(unified_ticket, "model_dump") else unified_ticket
            )

            customer_msg = (
                supervisor_payload.get("message", {}).get("original")
                or getattr(unified_ticket, "message_raw", None)
                or getattr(unified_ticket, "message_english", None)
            )
            
            logger.warning("CUSTOMER MESSAGE = %s", customer_msg)

            if customer_msg:
                customer_entry = {
                    "role": "customer",
                    "content": customer_msg
                }
                # Prevent accidental duplication of the customer message
                if not conversation_history or conversation_history[-1] != customer_entry:
                    conversation_history.append(customer_entry)
            
            # Append the Agent Response Safely
            if customer_response:
                # Safely fallback through multiple potential response keys
                assistant_msg = (
                    customer_response.get("english_response")
                    or customer_response.get("customer_response")
                    or customer_response.get("response")
                )
                if assistant_msg:
                    assistant_entry = {
                        "role": "assistant",
                        "content": assistant_msg
                    }
                    # Prevent accidental duplication of the assistant message
                    if not conversation_history or conversation_history[-1] != assistant_entry:
                        conversation_history.append(assistant_entry)
            # ---------------------------------------------------------

            global_context = {
                "ticket_id": unified_ticket.ticket_id,
                "customer_id": customer_data.get("customer_id"),
                "customer_email": customer_data.get("email"),
                "tier": customer_data.get("tier", "standard"),
                "ltv": customer_data.get("lifetime_value", "0.00"),
                "language": customer_data.get("language", "en"),
                "query_intent": supervisor_result.intent,
                "sentiment_start": supervisor_result.sentiment,
                "sentiment_end": getattr(specialist_result, "sentiment", supervisor_result.sentiment) if not isinstance(specialist_result, dict) else specialist_result.get("sentiment", supervisor_result.sentiment),
                "priority": getattr(supervisor_result, "urgency", "medium"),
                "issue_tags": safe_issue_tags,
                "agents_involved": ["supervisor_agent", "triage_agent", target_agent],
                "conversation_history": conversation_history,
                "customer_response_native": customer_response.get("customer_response") if customer_response else None
            }

            logger.warning("GLOBAL CONTEXT LTV = %s", global_context.get("ltv"))
            
            output_dict = specialist_result.model_dump(mode="json") if hasattr(specialist_result, "model_dump") else specialist_result

            logger.warning(
                "PIPELINE INTENT = %s",
                global_context.get("query_intent")
            )
            self._enqueue_crm_event(target_agent, output_dict, global_context)
            self._trace(
                ticket_id,
                "CRM-Handoff",
                "COMPLETE"
            )

        return {
            "unified_ticket": unified_ticket,
            "supervisor_payload": supervisor_payload,
            "supervisor_result": supervisor_result,
            "triage_result": triage_output,
            "specialist_result": specialist_result,
            "customer_response": customer_response
        }

    def resume_specialist_workflow(self, ticket_id: str, human_decision: str, reviewer_id: str = "orchestrator_admin", notes: str = None):
        """Asynchronously resumes a suspended workflow and drops the final result into the CRM queue."""
        logger.info(f"Resuming Ticket {ticket_id} with manager decision: {human_decision}")

        workflow = self.container.workflow_repository.get(ticket_id)
        if not workflow:
            logger.error(f"Cannot resume: No active workflow found for {ticket_id}.")
            return None

        graph = self.container.get_graph(workflow.agent_type)
        if not graph:
            logger.error(f"Cannot resume: Graph for {workflow.agent_type} is not registered.")
            return None

        config = {"configurable": {"thread_id": workflow.thread_id}}

        try:
            snapshot = graph.get_state(config)
            logger.warning("CHECKPOINT VALUES = %s", snapshot.values if snapshot else None)
        except Exception as e:
            logger.exception("CHECKPOINT LOAD FAILED: %s", str(e))

        logger.warning(
            "WORKFLOW DB | ticket=%s | workflow=%s | thread=%s",
            workflow.ticket_id, workflow.workflow_id, workflow.thread_id
        )

        if workflow.agent_type in ["faq_agent", "account_agent"]:
            final_state = graph.invoke(Command(resume=human_decision), config=config)
            
            logger.warning("FINAL STATE KEYS = %s", list(final_state.keys()))
            logger.warning("FINAL CUSTOMER CONTEXT = %s", final_state.get("customer_context"))
            logger.warning("FINAL CUSTOMER ID = %s", final_state.get("customer_id"))
            logger.warning("FINAL CUSTOMER DATA = %s", final_state.get("customer_data"))
            
        elif workflow.agent_type == "escalation_agent":
            # 🟢 FIX: Graph-level interrupt_before requires update_state + invoke(None)
            before = graph.get_state(config)

            logger.warning(
                "BEFORE UPDATE = %s",
                before.values if before else None
            )

            graph.update_state(
                config,
                {
                    "human_decision": {
                        "decision": human_decision.lower(),
                        "reviewer_id": reviewer_id,
                        "notes": notes or f"System resumed with decision: {human_decision}"
                    },
                    "review_completed": True
                },
                as_node="human_review"
            )
            self._trace(
                ticket_id,
                "Human-Manager-Review",
                human_decision.upper(),   # APPROVE / REJECT / CLARIFY
            )

            after = graph.get_state(config)

            logger.warning(
                "AFTER UPDATE = %s",
                after.values if after else None
            )
            start = time.perf_counter()
            final_state = graph.invoke(
                None,
                config=config
            )
            duration_ms = int((time.perf_counter() - start) * 1000)
            final_state["duration_ms"] = duration_ms

            logger.warning(
                "BUILD_ESCALATION_OUTPUT CALLED"
            )

            logger.warning(
                "FINAL STATE HUMAN_DECISION = %s",
                final_state.get("human_decision")
            )

            logger.warning(
                "FINAL STATE HUMAN_DECISION TYPE = %s",
                type(final_state.get("human_decision"))
            )
            
            logger.warning("FINAL STATE KEYS = %s", list(final_state.keys()))
            logger.warning("FINAL CUSTOMER CONTEXT = %s", final_state.get("customer_context"))
            logger.warning("FINAL CUSTOMER ID = %s", final_state.get("customer_id"))
            logger.warning("FINAL CUSTOMER DATA = %s", final_state.get("customer_data"))
            
        else:
            before = graph.get_state(config)
            logger.warning("BEFORE UPDATE = %s", before.values if before else None)

            graph.update_state(config, {"human_decision": human_decision.upper()})
            
            after = graph.get_state(config)
            logger.warning("AFTER UPDATE = %s", after.values if after else None)
            
            final_state = graph.invoke(None, config=config)
            
            logger.warning("FINAL STATE KEYS = %s", list(final_state.keys()))
            logger.warning("FINAL CUSTOMER CONTEXT = %s", final_state.get("customer_context"))
            logger.warning("FINAL CUSTOMER ID = %s", final_state.get("customer_id"))
            logger.warning("FINAL CUSTOMER DATA = %s", final_state.get("customer_data"))

        # Prevent mapper from running on incomplete escalation workflows
        if workflow.agent_type == "escalation_agent":
            if final_state.get("current_node") != "response_node":
                raise ValueError(
                    f"Escalation workflow incomplete. "
                    f"Stopped at {final_state.get('current_node')}"
                )

            if final_state.get("response") is None:
                raise ValueError(
                    "Escalation workflow completed without response."
                )

        mapper = self.container.get_output_mapper(workflow.agent_type)
        final_response = None
        
        if mapper:
            if workflow.agent_type == "escalation_agent":
                final_response = mapper(
                    final_state=final_state,
                    thread_id=workflow.thread_id
                )
            else:
                final_response = mapper(final_state)

        if isinstance(final_state, dict):
            cust_ctx = final_state.get("customer_context")
            fallback_cid = final_state.get("customer_id", 0)

            if cust_ctx is None and workflow.agent_type == "refund_agent":
                cust_ctx = final_state.get("customer_data")
                logger.warning("REFUND CUSTOMER DATA = %s", cust_ctx)
                if cust_ctx:
                    fallback_cid = getattr(cust_ctx, "customer_id", 0)

            initial_intent = final_state.get("initial_intent", "unknown")
            initial_sentiment = final_state.get("initial_sentiment", "neutral")
            # 🟢 REMOVED: convo = final_state.get("messages", [])
        else:
            cust_ctx = getattr(final_state, "customer_context", None)
            fallback_cid = getattr(final_state, "customer_id", 0)
            initial_intent = getattr(final_state, "initial_intent", "unknown")
            initial_sentiment = getattr(final_state, "initial_sentiment", "neutral")
            # 🟢 REMOVED: convo = getattr(final_state, "messages", [])
                
        customer_tier = "standard"
        customer_ltv = "0.00"

        if cust_ctx:
            if isinstance(cust_ctx, dict):
                customer_tier = (
                    cust_ctx.get("tier")
                    or cust_ctx.get("customer_tier")
                    or cust_ctx.get("account_tier")
                    or "standard"
                )
                customer_ltv = (
                    cust_ctx.get("ltv")
                    or cust_ctx.get("lifetime_value")
                    or cust_ctx.get("total_spent")
                    or "0.00"
                )
            else:
                customer_tier = (
                    getattr(cust_ctx, "tier", None)
                    or getattr(cust_ctx, "customer_tier", None)
                    or getattr(cust_ctx, "account_tier", None)
                    or "standard"
                )
                customer_ltv = (
                    getattr(cust_ctx, "ltv", None)
                    or getattr(cust_ctx, "lifetime_value", None)
                    or getattr(cust_ctx, "total_spent", None)
                    or "0.00"
                )

        # ==========================================
        # 🟢 1. LAYER 3 OUTBOUND TRANSLATION (Post-Human)
        # ==========================================
        customer_response = None
        if final_response:
            try:
                cid = getattr(cust_ctx, "customer_id", fallback_cid) if not isinstance(cust_ctx, dict) else cust_ctx.get("customer_id", fallback_cid)
                if cid:
                    self._trace(
                        ticket_id,
                        "layer3-Outbound-Translation",
                        "RUNNING"
                    )
                    customer_response = self.container.outbound_response_pipeline.process(
                        specialist_result=final_response,
                        customer_id=cid
                    )
                    self._trace(
                        ticket_id,
                        "layer3-Outbound-Translation",
                        "COMPLETE"
                    )
                    logger.warning("OUTBOUND RESPONSE RESULT = %s", customer_response)
            except Exception as e:
                logger.error(f"Failed to execute Outbound Translation Pipeline on Resume: {e}", exc_info=True)

        # ==========================================
        # 🟢 1.5 BUILD CONVERSATION HISTORY
        # ==========================================

        # Load existing transcript instead of rebuilding it
        existing_messages = []

        transcript = self.container.crm_transcript_repository.get_by_ticket_id(ticket_id)

        if transcript and transcript.messages:
            existing_messages = list(transcript.messages)

        conversation_history = existing_messages

        # Handle both dict and object states for robustness
        ticket = (
            final_state.get("ticket", {})
            if isinstance(final_state, dict)
            else getattr(final_state, "ticket", {})
        )

        customer_message = None

        if ticket:
            if isinstance(ticket, dict):
                customer_message = (
                    ticket.get("message_raw")
                    or ticket.get("message_english")
                )
            else:
                customer_message = (
                    getattr(ticket, "message_raw", None)
                    or getattr(ticket, "message_english", None)
                )

        if not customer_message:
            customer_message = (
                final_state.get("message")
                if isinstance(final_state, dict)
                else getattr(final_state, "message", None)
            )

        if customer_message:
            should_append = (
                not conversation_history
                or conversation_history[-1].get("role") != "customer"
                or conversation_history[-1].get("content") != customer_message
            )

            if should_append:
                conversation_history.append(
                    {
                        "role": "customer",
                        "content": customer_message,
                    }
                )

        if customer_response:
            assistant_message = None

            if isinstance(customer_response, dict):
                assistant_message = (
                    customer_response.get("english_response")
                    or customer_response.get("customer_response")
                )
            else:
                assistant_message = (
                    getattr(customer_response, "english_response", None)
                    or getattr(customer_response, "customer_response", None)
                )

            if assistant_message:
                should_append = (
                    not conversation_history
                    or conversation_history[-1].get("role") != "assistant"
                    or conversation_history[-1].get("content") != assistant_message
                )

                if should_append:
                    conversation_history.append(
                        {
                            "role": "assistant",
                            "content": assistant_message,
                        }
                    )

        # ==========================================
        # 🟢 2. CRM ASYNC HANDOFF
        # ==========================================
        logger.warning("CID CHECK | cust_ctx=%s | fallback=%s", cust_ctx, fallback_cid)
        
        # Dynamic priority extraction
        priority = "UNKNOWN"
        if workflow.agent_type == "escalation_agent":
            risk = final_state.get("risk_assessment") if isinstance(final_state, dict) else getattr(final_state, "risk_assessment", None)
            if risk:
                priority = risk.level.value if hasattr(risk.level, "value") else str(risk.level)

        logger.warning(
            "FINAL TICKET OBJECT = %s",
            final_state.get("ticket") if isinstance(final_state, dict) else getattr(final_state, "ticket", None)
        )
        
        global_context = {
            "ticket_id": ticket_id,
            "customer_id": getattr(cust_ctx, "customer_id", fallback_cid) if not isinstance(cust_ctx, dict) else cust_ctx.get("customer_id", fallback_cid),
            "customer_email": getattr(cust_ctx, "customer_email", None) if not isinstance(cust_ctx, dict) else cust_ctx.get("customer_email"),
            "tier": customer_tier,
            "ltv": customer_ltv,
            "query_intent": initial_intent,
            "sentiment_start": initial_sentiment,
            "sentiment_end": initial_sentiment,
            "priority": priority,
            "issue_tags": ["escalation", "human_reviewed"] if workflow.agent_type == "escalation_agent" else ["human_reviewed"],
            "agents_involved": ["triage_agent", workflow.agent_type, "human_manager"],
            "conversation_history": conversation_history,  # 🟢 FIX: Now injecting manually built transcript
            "customer_response_native": customer_response.get("customer_response") if isinstance(customer_response, dict) else getattr(customer_response, "customer_response", None) if customer_response else None
        }
        
        output_dict = final_response.model_dump(mode="json") if hasattr(final_response, "model_dump") else final_response

        logger.warning(
            "CRM DEBUG | customer_id=%s | tier=%s | ltv=%s | priority=%s",
            global_context.get("customer_id"), global_context.get("tier"), global_context.get("ltv"), global_context.get("priority")
        )
        self._trace(    
            ticket_id,
            "CRM-Handoff",
            "RUNNING"
        )
        self._enqueue_crm_event(workflow.agent_type, output_dict, global_context)
        self._trace(
            ticket_id,
            "CRM-Persistence",
            "COMPLETED"
        )

        # Workflow marked completed ONLY after CRM dispatch succeeds
        self.container.workflow_repository.mark_completed(ticket_id)
        self._trace(
            ticket_id,
            "Workflow",
            "COMPLETED"
        )

        return {
            "specialist_result": final_response,
            "customer_response": customer_response 
        }