# Layer 0 - Codebase Analysis & Integration Guide

## Overview
Layer 0 is the **entry point and data normalization layer** for the multi-agent customer support system. It handles incoming customer requests from any channel, normalizes them into a unified format, and enriches them with context before passing to downstream layers.

---

## Architecture & Components

### 1. **FastAPI Application** (`app.py`)
- **Role**: HTTP server exposing webhook endpoint
- **Endpoint**: `POST /webhook`
- **Input Model**: `RequestModel`
- **Output Model**: `UnifiedTicket`
- **Features**:
  - Request/response logging middleware
  - Global exception handling (validation errors, server errors)
  - Comprehensive error responses with status codes (400, 422, 500)

### 2. **Main Processing Pipeline** (`main.py`)
The core orchestration function that:
1. **Normalizes** incoming data
2. **Detects language** of customer message
3. **Fetches customer info** from CRM
4. **Assigns priority** based on customer tier
5. **Validates** against UnifiedTicket schema
6. **Returns** structured ticket dictionary

**Flow**:
```
Input Data → Normalizer → Language Detection → CRM Lookup → 
Priority Assignment → Validation → UnifiedTicket Output
```

---

## Data Models (`model.py`)

### **RequestModel** (Input)
```python
{
  "message": str,        # Customer's message/issue
  "customer_id": str,    # Unique customer identifier
  "name": str            # Customer name
}
```

### **UnifiedTicket** (Output)
```python
{
  "ticket_id": str,           # Auto-generated UUID
  "channel": str,             # Source channel (default: "web")
  "customer_id": str,         # From input
  "customer_name": str,       # From input
  "timestamp": str,           # ISO UTC timestamp
  "issue_description": str,   # Customer's message
  "message_text": str,        # Customer's message (duplicate)
  "language": str,            # Detected language code (e.g., "en", "hi")
  "intent": Optional[str],    # Placeholder for downstream analysis
  "order_id": Optional[str],  # Placeholder for order context
  "issue_type": Optional[str],# Placeholder for issue classification
  "customer_info": {          # Enriched from CRM
    "lifetime_value": int,
    "previous_tickets": int,
    "tier": str               # "gold" | "silver" | "unknown"
  },
  "priority": str             # "high" (gold) | "medium" (silver) | "low" (other)
}
```

---

## Key Modules

### **Normalizer** (`normalizer.py`)
**Purpose**: Standardize incoming data regardless of source format

**Operations**:
- Extracts and validates: `message`, `customer_id`, `customer_name`
- Generates: `ticket_id` (UUID4), `timestamp` (ISO 8601 UTC)
- Sets defaults: `channel` (defaults to "web")
- Creates standardized dictionary with all required fields
- Handles missing/empty fields gracefully

**Output**: Dictionary with 11 standardized fields

### **Language Detector** (`language.py`)
**Purpose**: Detect customer message language (especially English & Hindi/Hinglish)

**Features**:
- **Hinglish Detection**: Looks for Hindi/Urdu-specific words
  - Strong markers: "mujhe", "chahiye", "nahi", etc.
  - Common markers: "hai", "aur", "ko", etc.
- **Fallback Libraries**:
  - `langid`: Language classification
  - `langdetect`: Probability-based detection
- **Edge Cases**:
  - Messages < 3 chars → default to "en"
  - Handles Swahili misclassification
  - Returns high-probability languages (>0.85)

**Output**: Language code string (e.g., "en", "hi", "es", etc.)

### **CRM Module** (`crm.py`)
**Purpose**: Fetch customer context for priority assignment

**Current Implementation**: Mock database with hardcoded customers
```python
"C1": { "lifetime_value": 5000, "previous_tickets": 3, "tier": "gold" }
"C2": { "lifetime_value": 200,  "previous_tickets": 1, "tier": "silver" }
```

**Function**: `get_customer_info(customer_id)` → Returns dict or defaults

### **Logger** (`logger.py`)
**Purpose**: Structured logging for debugging and monitoring

**Format**: `timestamp | level | name | message`

---

## Integration Points

### **Inputs to Layer 0**
- HTTP POST requests from any customer channel (web, email, chat, etc.)
- Expected data: `RequestModel` JSON

### **Outputs from Layer 0**
- `UnifiedTicket` → Sent to downstream layers (Layer 1, Layer 2 agents, Layer 3)

### **Downstream Layer Dependencies**
Layer 0 provides structured input for:
1. **Layer 1** (Likely: Intent classification, order/issue extraction)
2. **Layer 2 Agents** (Triage, FAQ, Refund, Escalation, Account, Proactive)
3. **Layer 3** (Likely: Final decision/action execution)

---

## Current Limitations & Integration Notes

### ⚠️ Things to Address Before Integration:

1. **CRM Module is Mocked**
   - Currently hardcoded to 2 test customers (C1, C2)
   - **Action**: Replace with real CRM API call (Salesforce, HubSpot, etc.)
   - Interface: `get_customer_info(customer_id)` can remain, just swap implementation

2. **No Intent/Issue Extraction**
   - Fields like `intent`, `order_id`, `issue_type` are None
   - **Action**: These should be populated by Layer 1 or external NLP model
   - Layer 0 currently just reserves space for them

3. **Channel Detection is Hardcoded**
   - Defaults to "web" if not specified
   - **Action**: Update to detect channel from request headers/metadata

4. **Duplicate Fields**
   - `message_text` and `issue_description` are identical
   - **Action**: Consider consolidation in downstream usage

5. **No Request Validation Before Normalization**
   - Empty/missing customer_id gets "unknown"
   - **Action**: Consider adding stricter validation or default rejection

---

## How to Use Layer 0

### Start the Server
```bash
cd layer_0
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Make a Request
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My order hasn\'t arrived",
    "customer_id": "C1",
    "name": "John Doe"
  }'
```

### Expected Response
```json
{
  "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
  "channel": "web",
  "customer_id": "C1",
  "customer_name": "John Doe",
  "timestamp": "2026-06-10T09:42:36.123456Z",
  "issue_description": "My order hasn't arrived",
  "message_text": "My order hasn't arrived",
  "language": "en",
  "intent": null,
  "order_id": null,
  "issue_type": null,
  "customer_info": {
    "lifetime_value": 5000,
    "previous_tickets": 3,
    "tier": "gold"
  },
  "priority": "high"
}
```

---

## Integration Checklist

- [ ] **Phase 1 - Connection**
  - [ ] Verify Layer 0 API is accessible to other components
  - [ ] Test webhook endpoint with sample payloads
  - [ ] Confirm UnifiedTicket schema matches downstream expectations

- [ ] **Phase 2 - Real CRM Integration**
  - [ ] Replace mock CRM with actual API calls
  - [ ] Add API key/authentication handling
  - [ ] Implement error handling for CRM failures (fallback to defaults)

- [ ] **Phase 3 - Channel Detection**
  - [ ] Parse channel from request headers/metadata
  - [ ] Support channels: "web", "email", "chat", "phone", etc.

- [ ] **Phase 4 - Downstream Handoff**
  - [ ] Configure Layer 0 to route UnifiedTickets to Layer 1
  - [ ] Validate Layer 1 can process UnifiedTicket format
  - [ ] Test end-to-end flow

---

## Dependencies
- `fastapi`: Web framework
- `pydantic`: Data validation
- `langid`: Language identification
- `langdetect`: Language probability detection
- `logging`: Standard library logging

