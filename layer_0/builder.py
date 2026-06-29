## layer_0/builder.py
def build_ticket(normalized_data: dict,customer_info:dict):
    normalized_data["customer_info"] = customer_info
    return normalized_data        
