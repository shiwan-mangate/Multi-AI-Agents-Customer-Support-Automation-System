## layer_0/crm.py
from layer_2_triage.repositories.customer_repository import CustomerRepository

from layer_2_triage.repositories.ticket_repository import (
    TicketRepository,
)


# layer_0/crm.py

class CustomerInfoService:

    def __init__(
        self,
        profile_repo: CustomerRepository,
        ticket_repo: TicketRepository,
    ):
        self.profile_repo = profile_repo
        self.ticket_repo = ticket_repo

    def get_customer_info(self, customer_id: int):
        count = self.ticket_repo.get_previous_ticket_count(customer_id)

       
        customer_info = self.profile_repo.get_customer_by_id(customer_id)

        if customer_info is None:
            customer_profile = {
                "lifetime_value": 0,
                "previous_tickets": 0,
                "tier": "standard",
            }
        else:
            customer_profile = {
                "lifetime_value": customer_info["total_spent"], 
                "previous_tickets": count,
                "tier": customer_info["account_tier"],
            }

        return customer_profile