## layer_0/main.py
from layer_0.model import UnifiedTicket
from layer_0.language import detect_language

def main(data, normalizer, language_detector, crm_repository):
    normalized_data = normalizer(data)
    message = normalized_data.get("message_text", "")

    
    normalized_data["language"] = detect_language(message)


    customer_id = normalized_data.get("customer_id")
    customer_info = crm_repository.get_customer_info(customer_id)

    if customer_info is None:
        raise ValueError(f"Customer {customer_id} not found")

    normalized_data["customer_info"] = customer_info
    

    tier = customer_info.get("tier", "").upper()
    
    if tier == "ENTERPRISE": 
        normalized_data["priority"] = "urgent"
    elif tier == "PREMIUM":
        normalized_data["priority"] = "high"
    else:
        normalized_data["priority"] = "low"

    validated_ticket = UnifiedTicket(**normalized_data)
    return validated_ticket