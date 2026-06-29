# layer_4_analytics/reports/executive_summary_service.py

import math
from layer_4_analytics.schemas.dashboard_snapshot import DashboardSnapshot


class ExecutiveSummaryService:
    """
    The pinnacle presentation layer for Layer 4.
    Consumes the master DashboardSnapshot contract and distills it into 
    a high-level, executive-friendly text summary spanning operations, 
    finance, customer health, and knowledge gaps.
    """

    AGENT_DISPLAY_NAMES = {
        "faq_agent": "FAQ Agent",
        "refund_agent": "Refund Agent",
        "account_agent": "Account Agent",
        "escalation_agent": "Escalation Agent",
        "proactive_agent": "Proactive Agent"
    }

    @staticmethod
    def generate_summary(snapshot: DashboardSnapshot) -> str:
        """
        Generates a comprehensive executive report. Extracts the 'top' performing 
        or 'highest' priority metrics from the underlying snapshot arrays safely.
        """

        start_date = snapshot.report_period_start.strftime("%Y-%m-%d")
        end_date = snapshot.report_period_end.strftime("%Y-%m-%d")

   
        trend = snapshot.satisfaction_metrics.trend_percentage
        if trend > 0:
            trend_display = f"+{trend:,.2f}%"
        elif trend < 0:
            trend_display = f"{trend:,.2f}%"  
        else:
            trend_display = "±0.00%"
        
        if snapshot.roi_metrics is not None:
            roi_val = snapshot.roi_metrics.roi_percentage
            roi_display = (
                "Infinite"
                if math.isinf(roi_val)
                else f"{roi_val:,.2f}%"
            )
            net_savings_display = (
                f"${snapshot.roi_metrics.net_savings:,.2f}"
            )
        else:
            roi_display = "N/A (Platform Dashboard)"
            net_savings_display = "N/A"


        if snapshot.agent_metrics:
            top_agent = max(snapshot.agent_metrics, key=lambda x: x.resolution_rate)
          
            agent_name = ExecutiveSummaryService.AGENT_DISPLAY_NAMES.get(
                top_agent.agent_name, 
                top_agent.agent_name.replace("_", " ").title()
            )
            agent_display = f"{agent_name}\n\nResolution Rate:\n{top_agent.resolution_rate:,.2f}%"
        else:
            agent_display = "N/A\n\nResolution Rate:\nN/A"

        if snapshot.intent_metrics:
            top_intent = max(snapshot.intent_metrics, key=lambda x: x.ticket_count)
            intent_name = top_intent.intent_name.replace("_", " ").title()
         
            if intent_name.lower() == "faq":
                intent_name = "FAQ"
            intent_display = f"{intent_name} ({top_intent.percentage:,.0f}%)"
        else:
            intent_display = "N/A"

        if snapshot.language_metrics:
            top_lang = max(snapshot.language_metrics, key=lambda x: x.ticket_count)
            lang_display = top_lang.language_name
        else:
            lang_display = "N/A"


        high_risk_count = len(snapshot.high_risk_customers)
        if high_risk_count > 0:
            highest_risk = snapshot.high_risk_customers[0]
            risk_account_display = f"{highest_risk.customer_name} (Risk Score: {highest_risk.risk_score:,.1f})"
        else:
            risk_account_display = "No High Risk Customers"

        if snapshot.knowledge_gaps:
            top_gap = snapshot.knowledge_gaps[0]
            knowledge_display = (
                f"Top Knowledge Gap:\n{top_gap.topic.replace('_', ' ').title()}\n\n"
                f"Occurrences:\n{top_gap.occurrences}\n\n"
                f"Suggested Action:\n{top_gap.suggested_action}"
            )
        else:
            knowledge_display = (
                "Top Knowledge Gap:\nNone Detected\n\n"
                "Occurrences:\n0\n\n"
                "Suggested Action:\nN/A"
            )


        report = f"""
==================================================
EXECUTIVE SUMMARY REPORT
==================================================

Reporting Window:
{start_date} → {end_date}

--------------------------------------------------
PLATFORM OVERVIEW
--------------------------------------------------

Total Tickets:        {snapshot.total_tickets:,}
Total Customers:      {snapshot.total_customers:,}

Customer Satisfaction:
{snapshot.satisfaction_metrics.satisfaction_rate:,.2f}% (Trend: {trend_display})

ROI:
{roi_display}

Net Savings:
{net_savings_display}

--------------------------------------------------
OPERATIONAL HIGHLIGHTS
--------------------------------------------------

Top Agent:
{agent_display}

Most Common Intent:
{intent_display}

Top Language:
{lang_display}

--------------------------------------------------
CUSTOMER HEALTH
--------------------------------------------------

High Risk Customers:
{high_risk_count}

Highest Risk Account:
{risk_account_display}

--------------------------------------------------
KNOWLEDGE INTELLIGENCE
--------------------------------------------------

{knowledge_display}

==================================================
END OF REPORT
==================================================
""".strip()

        return report