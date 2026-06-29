# layer_4_analytics/analytics/agent_performance_service.py

from datetime import datetime
from typing import List, Dict, Any

from layer_4_analytics.schemas.agent_metrics import AgentMetrics


class AgentPerformanceAnalyticsService:
    """
    Core business intelligence engine for computing Layer 2 agent operational KPIs.
    Consumes mapped, normalized arrays of transcript dictionaries and outputs fully 
    validated, timezone-aware AgentMetrics Pydantic contracts.
    """

    @staticmethod
    def calculate_agent_metrics(
        mapped_rows: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime,
        satisfaction_lookup: Dict[str, float] = None
    ) -> List[AgentMetrics]:
        """
        Groups transcript events by agent, computes volumetric and velocity KPIs,
        and constructs the final reporting schemas.
        """
        if satisfaction_lookup is None:
            satisfaction_lookup = {}

       
        agent_groups: Dict[str, List[Dict[str, Any]]] = {}
        for row in mapped_rows:
            agent = row.get("agent_name", "unknown_agent")
            if agent not in agent_groups:
                agent_groups[agent] = []
            agent_groups[agent].append(row)

        results: List[AgentMetrics] = []

       
        for agent_name, agent_rows in agent_groups.items():
            tickets_handled = len(agent_rows)
            
            if tickets_handled == 0:
                continue

        
            resolved_count = sum(1 for r in agent_rows if r.get("status") == "resolved")
            escalated_count = sum(1 for r in agent_rows if r.get("status") == "escalated")

            
            resolution_rate = (resolved_count / tickets_handled) * 100.0
            escalation_rate = (escalated_count / tickets_handled) * 100.0

            
            valid_times = [
                r.get("resolution_time_seconds", 0.0) 
                for r in agent_rows 
                if r.get("resolution_time_seconds", 0.0) > 0.0
            ]
            
            avg_resolution_time = (sum(valid_times) / len(valid_times)) if valid_times else 0.0

            
            satisfaction_rate = satisfaction_lookup.get(agent_name, 0.0)

        
            metrics = AgentMetrics(
                agent_name=agent_name,
                tickets_handled=tickets_handled,
                resolved_count=resolved_count,
                escalated_count=escalated_count,
                resolution_rate=round(resolution_rate, 2),
                escalation_rate=round(escalation_rate, 2),
                avg_resolution_time_seconds=round(avg_resolution_time, 2),
                satisfaction_rate=round(satisfaction_rate, 2),
                period_start=period_start,
                period_end=period_end
            )
            
            results.append(metrics)

        return results