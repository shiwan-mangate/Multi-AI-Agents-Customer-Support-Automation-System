import uuid
from datetime import datetime, UTC
from typing import List

from layer_2_proactive_agent.schemas.signal import Signal
from layer_2_proactive_agent.schemas.enums import SignalType, SignalSource
from layer_2_proactive_agent.utils.logger import logger
from crm_agent.repositories.customer_profile_repository import CustomerProfileRepository

from crm_agent.db.models.customer_profile_model import CustomerProfile


class CRMSignalService:
    """
    The 'Hunting Mechanism' for the Proactive Agent.
    Scans the CRM Database to detect at-risk customers and converts 
    them into strictly typed Signal contracts.
    """

    def __init__(self, profile_repo: CustomerProfileRepository):
        self.profile_repo = profile_repo
        
        # Business Logic Thresholds
        self.inactivity_threshold_days = 30
        self.churn_threshold = 80.0
        self.vip_churn_threshold = 60.0
        self.negative_interaction_threshold = 3

    def detect_signals(self) -> List[Signal]:
        """
        Scans the database and returns a list of detected Signals.
        Prioritizes critical VIP/Churn signals over simple inactivity.
        """
        logger.info("Status=START | Operation=SIGNAL_DETECTION | Source=CRM")
        signals = []

        try:
            session = self.profile_repo.session
            now = datetime.now(UTC)
            
            # Note: For MVP, loading all profiles in Python. 
            # For V2, push WHERE clauses into SQL (e.g., repo.get_high_churn_customers())
            profiles = session.query(CustomerProfile).all()

            for profile in profiles:
                customer_id = profile.customer_id
                
                # ---------------------------------------------------------
                # FIX: Explicitly cast DB Numeric (Decimal) to float to 
                # prevent TypeError against float thresholds & ensure JSON serialization
                # ---------------------------------------------------------
                churn_score = float(profile.churn_score or 0.0)
                ltv = float(profile.ltv or 0.0)
                
                negative_count = profile.negative_ticket_count or 0
                tier = (profile.tier or "standard").lower()
                
  
                # RULE 1: VIP Retention Risk (Highest Priority)
                if tier == "enterprise" and churn_score >= self.vip_churn_threshold:
                    signals.append(self._build_signal(
                        customer_id, 
                        SignalType.VIP_RETENTION_RISK, 
                        {
                            "churn_score": churn_score, 
                            "ltv": ltv,
                            "detected_at": now.isoformat()
                        } 
                    ))
                    continue
                   
             
                # RULE 2: High Churn Risk
                if churn_score >= self.churn_threshold:
                    signals.append(self._build_signal(
                        customer_id, 
                        SignalType.HIGH_CHURN_RISK, 
                        {
                            "churn_score": churn_score,
                            "detected_at": now.isoformat()
                        }
                    ))
                    
                    continue
                    

                # RULE 3: Recent Negative Experience
                if negative_count >= self.negative_interaction_threshold:
                    signals.append(self._build_signal(
                        customer_id, 
                        SignalType.RECENT_NEGATIVE_EXPERIENCE, 
                        {
                            "negative_interactions": negative_count,
                            "detected_at": now.isoformat()
                        }
                    ))
                    
                    continue
                    
         
                # RULE 4: Inactive Customer
                last_ticket_at = getattr(profile, "last_ticket_at", None)
                if last_ticket_at:
                    if last_ticket_at.tzinfo is None:
                        last_ticket_at = last_ticket_at.replace(tzinfo=UTC)
                    
                    days_inactive = (now - last_ticket_at).days
                    if days_inactive >= self.inactivity_threshold_days:
                        signals.append(self._build_signal(
                            customer_id, 
                            SignalType.INACTIVE_CUSTOMER, 
                            {
                                "days_inactive": days_inactive,
                                "detected_at": now.isoformat()
                            }
                        ))
                        
                        continue
                        

            logger.info("Status=SUCCESS | Operation=SIGNAL_DETECTION | SignalsFound=%s", len(signals))
            return signals

        except Exception as e:
            logger.exception("Status=FAILED | Operation=SIGNAL_DETECTION | Error=%s", str(e))
            raise

    def _build_signal(self, customer_id: int, signal_type: SignalType, context: dict) -> Signal:
        """Helper to construct the strictly typed immutable Signal."""

        unique_sig_id = f"SIG-{signal_type.name}-{customer_id}-{uuid.uuid4().hex[:4]}"
        
        return Signal(
            signal_id=unique_sig_id,
            customer_id=customer_id,
            signal_type=signal_type,
            signal_source=SignalSource.CRM,
            signal_context=context
        )