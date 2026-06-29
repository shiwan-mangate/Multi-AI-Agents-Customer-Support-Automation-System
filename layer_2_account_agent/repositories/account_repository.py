from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

# Import the exact models we generated for the Account Agent
from layer_2_account_agent.db.model.auth_accounts_model import AuthAccount
from layer_2_account_agent.db.model.subscriptions_model import Subscription

logger = logging.getLogger(__name__)

class AccountRepository:
    """
    Repository for authentication state, account security operations,
    and subscription lifecycle management.
    """

    def __init__(self, session: Session):
        self.session = session

    # =========================================================
    # INTERNAL MUTATION HELPER
    # =========================================================

    def _execute_mutation(
        self,
        query,
        update_values: Dict[str, Any],
        error_message: str
    ) -> bool:
        """
        Executes ORM UPDATE mutations safely with transaction handling.
        Accepts a filtered SQLAlchemy Query object and a dictionary of values to update.
        """
        try:
            # SQLAlchemy native update command
            rowcount = query.update(update_values, synchronize_session=False)

            if rowcount == 0:
                self.session.rollback()
                logger.warning("%s | No rows affected.", error_message)
                return False

            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
                
            return True

        except Exception:
            self.session.rollback()
            logger.exception(error_message)
            return False

    # =========================================================
    # AUTHENTICATION / SECURITY
    # =========================================================

    def get_auth_account(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch authentication/security state for a customer.
        """
        try:
            # Querying the exact columns matching your original SELECT statement
            result = self.session.query(
                AuthAccount.auth_account_id,
                AuthAccount.customer_id,
                AuthAccount.login_provider,
                AuthAccount.account_locked,
                AuthAccount.failed_login_attempts,
                AuthAccount.two_factor_enabled,
                AuthAccount.suspicious_flag,
                AuthAccount.last_login_at,
                AuthAccount.last_password_reset_at,
                AuthAccount.created_at,
                AuthAccount.updated_at
            ).filter(
                AuthAccount.customer_id == customer_id
            ).first()

            # _asdict() replicates dict(result.mappings()) exactly
            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed to fetch auth account for customer_id=%s",
                customer_id
            )
            return None

    def increment_failed_attempts(self, customer_id: int) -> bool:
        """
        Increment failed login attempts.
        """
        query = self.session.query(AuthAccount).filter(
            AuthAccount.customer_id == customer_id
        )
        
        # Using AuthAccount.failed_login_attempts + 1 directly translates to the SQL increment
        update_values = {
            "failed_login_attempts": AuthAccount.failed_login_attempts + 1,
            "updated_at": func.now()
        }

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to increment failed attempts for customer_id={customer_id}"
        )

    def reset_failed_attempts(self, customer_id: int) -> bool:
        """
        Reset failed login attempts after successful verification.
        """
        query = self.session.query(AuthAccount).filter(
            AuthAccount.customer_id == customer_id
        )
        
        update_values = {
            "failed_login_attempts": 0,
            "updated_at": func.now()
        }

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to reset failed attempts for customer_id={customer_id}"
        )

    def unlock_account(self, customer_id: int) -> bool:
        """
        Unlock account after successful verification.
        Does NOT clear suspicious_flag automatically.
        """
        query = self.session.query(AuthAccount).filter(
            AuthAccount.customer_id == customer_id
        )
        
        update_values = {
            "account_locked": False,
            "failed_login_attempts": 0,
            "updated_at": func.now()
        }

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to unlock account for customer_id={customer_id}"
        )

    def mark_suspicious(self, customer_id: int) -> bool:
        """
        Lock and flag account for security review.
        """
        query = self.session.query(AuthAccount).filter(
            AuthAccount.customer_id == customer_id
        )
        
        update_values = {
            "suspicious_flag": True,
            "account_locked": True,
            "updated_at": func.now()
        }

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to mark suspicious account for customer_id={customer_id}"
        )

    def update_last_password_reset(self, customer_id: int) -> bool:
        """
        Record password reset event timestamp.
        """
        query = self.session.query(AuthAccount).filter(
            AuthAccount.customer_id == customer_id
        )
        
        update_values = {
            "last_password_reset_at": func.now(),
            "updated_at": func.now()
        }

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to update password reset timestamp for customer_id={customer_id}"
        )

    def record_successful_login(self, customer_id: int) -> bool:
        """
        Record successful login and reset failed attempts.
        """
        query = self.session.query(AuthAccount).filter(
            AuthAccount.customer_id == customer_id
        )
        
        update_values = {
            "failed_login_attempts": 0,
            "last_login_at": func.now(),
            "updated_at": func.now()
        }

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to record successful login for customer_id={customer_id}"
        )

    # =========================================================
    # SUBSCRIPTION MANAGEMENT
    # =========================================================

    def get_subscription(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch most relevant active subscription state.
        """
        try:
            result = self.session.query(
                Subscription.subscription_id,
                Subscription.customer_id,
                Subscription.plan_name,
                Subscription.billing_cycle,
                Subscription.status,
                Subscription.auto_renew,
                Subscription.started_at,
                Subscription.renews_at,
                Subscription.cancelled_at,
                Subscription.created_at,
                Subscription.updated_at
            ).filter(
                Subscription.customer_id == customer_id,
                # Translating the IN clause exactly
                Subscription.status.in_(['active', 'paused', 'trial', 'past_due'])
            ).order_by(
                Subscription.created_at.desc()
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed to fetch subscription for customer_id=%s",
                customer_id
            )
            return None

    def update_subscription_status(
        self,
        customer_id: int,
        new_status: str
    ) -> bool:
        """
        Update subscription lifecycle state.
        """
        query = self.session.query(Subscription).filter(
            Subscription.customer_id == customer_id,
            Subscription.status.in_(['active', 'paused', 'trial', 'past_due'])
        )

        update_values = {
            "status": new_status,
            "updated_at": func.now()
        }

        # Handle the CASE WHEN logic natively in Python
        if new_status == 'cancelled':
            update_values["cancelled_at"] = func.now()

        return self._execute_mutation(
            query,
            update_values,
            f"Failed to update subscription for customer_id={customer_id}"
        )