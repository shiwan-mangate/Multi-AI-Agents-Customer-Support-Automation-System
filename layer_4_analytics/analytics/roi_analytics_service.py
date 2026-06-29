# layer_4_analytics/analytics/roi_analytics_service.py

from datetime import datetime
from typing import List, Dict, Any, Union

from layer_4_analytics.schemas.roi_metrics import ROIMetrics


AUTO_RESOLUTION_TYPES = {
    "faq_answer",
    "account_action",
    "refund_completed",
}

ESCALATION_TYPES = {
    "escalation_created",
    "security_escalation",
}


class ROIAnalyticsService:
    """
    Core commercial business intelligence engine.
    Calculates operational savings, automated resolution ratios, and definitive 
    Return on Investment (ROI) percentages for individual multi-tenant clients.
    """

    @staticmethod
    def calculate_roi_metrics(
        customer_id: Union[str, int],
        customer_name: str,
        mapped_rows: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime,
        estimated_cost_per_ticket: float,
        platform_cost: float
    ) -> ROIMetrics:
        """
        Processes normalized support tickets to compute gross savings, net savings, 
        and the final ROI ratio for a specific customer reporting window.
        """
        
        auto_resolved_tickets = 0
        escalated_tickets = 0

        for row in mapped_rows:

            resolution_type = row.get("resolution_type")
            status = row.get("status")

            # Successfully handled completely by AI
            if (
                resolution_type in AUTO_RESOLUTION_TYPES
                and status == "resolved"
            ):
                auto_resolved_tickets += 1

            # Required human/security escalation
            elif (
                resolution_type in ESCALATION_TYPES
                or status == "escalated"
            ):
                escalated_tickets += 1

        total_tickets = auto_resolved_tickets + escalated_tickets

        auto_resolution_rate = 0.0
        if total_tickets > 0:
            auto_resolution_rate = (auto_resolved_tickets / total_tickets) * 100.0

        gross_savings = auto_resolved_tickets * estimated_cost_per_ticket
        net_savings = gross_savings - platform_cost

        if platform_cost == 0.0:
            roi_percentage = float("inf") if net_savings > 0 else 0.0
        else:
            roi_percentage = (net_savings / platform_cost) * 100.0

        return ROIMetrics(
            customer_id=customer_id,
            customer_name=customer_name,
            total_tickets=total_tickets,
            auto_resolved_tickets=auto_resolved_tickets,
            escalated_tickets=escalated_tickets,
            auto_resolution_rate=round(auto_resolution_rate, 2),
            estimated_cost_per_ticket=round(estimated_cost_per_ticket, 2),
            gross_savings=round(gross_savings, 2),
            platform_cost=round(platform_cost, 2),
            net_savings=round(net_savings, 2),
            roi_percentage=round(roi_percentage, 2) if platform_cost != 0.0 else roi_percentage,
            period_start=period_start,
            period_end=period_end
        )