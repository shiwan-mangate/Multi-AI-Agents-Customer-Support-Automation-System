# layer_4_analytics/reports/roi_report_service.py

import math
from layer_4_analytics.schemas.roi_metrics import ROIMetrics

class ROIReportService:
    """
    Presentation layer for Commercial Data.
    Consumes validated ROIMetrics schemas and transforms them into 
    human-readable, formatted text reports for dispatch to Email, Slack, or PDFs.
    Contains zero business logic or calculations.
    """

    @staticmethod
    def generate_report(metrics: ROIMetrics) -> str:
        """
        Generates a structured, executive-ready ROI text report.
        Handles all string formatting, currency conversions, and date representations.
        """
     
        start_date = metrics.period_start.strftime("%Y-%m-%d")
        end_date = metrics.period_end.strftime("%Y-%m-%d")

       
        if math.isinf(metrics.roi_percentage):
            roi_display = "Infinite (Zero Platform Cost)"
        else:
            roi_display = f"{metrics.roi_percentage:,.2f}%"

       
        if metrics.net_savings > 0:
            summary_statement = (
                f"The platform successfully automated {metrics.auto_resolution_rate:,.2f}% of support volume "
                f"and generated ${metrics.net_savings:,.2f} in net savings during the reporting period."
            )
        elif metrics.net_savings == 0:
            summary_statement = (
                f"The platform automated {metrics.auto_resolution_rate:,.2f}% of support volume. "
                "The platform achieved operational parity during the reporting period."
            )
        else:
            summary_statement = (
                f"The platform automated {metrics.auto_resolution_rate:,.2f}% of support volume. "
                "Platform costs exceeded realized savings during the reporting period."
            )


        report = f"""
==================================================
ROI PERFORMANCE REPORT
==================================================

Customer:
{metrics.customer_name} (ID: {metrics.customer_id})

Reporting Period:
{start_date} → {end_date}

--------------------------------------------------
SUPPORT OPERATIONS
--------------------------------------------------

Total Actionable Tickets: {metrics.total_tickets:,}
AI Resolved Tickets:      {metrics.auto_resolved_tickets:,}
Escalated Tickets:        {metrics.escalated_tickets:,}

Automation Rate:          {metrics.auto_resolution_rate:,.2f}%

--------------------------------------------------
FINANCIAL IMPACT
--------------------------------------------------

Estimated Cost Per Human Ticket: ${metrics.estimated_cost_per_ticket:,.2f}

Gross AI Savings: ${metrics.gross_savings:,.2f}
Platform Cost:    ${metrics.platform_cost:,.2f}

Net Savings:      ${metrics.net_savings:,.2f}
ROI:              {roi_display}

--------------------------------------------------
SUMMARY
--------------------------------------------------

{summary_statement}
==================================================
""".strip()

        return report