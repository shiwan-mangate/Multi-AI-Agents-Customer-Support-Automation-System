from abc import ABC, abstractmethod
from typing import Optional

from layer_2_refund.schemas.refund_models import (
    OrderData,
    OrderStatus,
    CustomerData
)


class AbstractOrderRepository(ABC):
    """Contract for interacting with the 'orders' database table."""

    @abstractmethod
    def get_order_by_id(
        self,
        order_id: int
    ) -> Optional[OrderData]:
        """
        Fetch order details.

        Returns:
            OrderData if found.
            None otherwise.
        """
        pass

    @abstractmethod
    def update_order_status(
        self,
        order_id: int,
        status: OrderStatus
    ) -> bool:
        """
        Update order status.

        Returns:
            True if updated.
            False otherwise.
        """
        pass


class AbstractCustomerRepository(ABC):
    """Contract for interacting with the 'customers' database table."""

    @abstractmethod
    def get_customer_by_id(
        self,
        customer_id: int
    ) -> Optional[CustomerData]:
        """
        Fetch customer profile.

        Returns:
            CustomerData if found.
            None otherwise.
        """
        pass

    @abstractmethod
    def update_customer_after_refund(
        self,
        customer_id: int,
        new_total_spent: float
    ) -> bool:
        """
        Update customer spending after successful refund execution.
        
        Note: Aligned with DB schema (updates 'total_spent').

        Returns:
            True if updated.
            False otherwise.
        """
        pass