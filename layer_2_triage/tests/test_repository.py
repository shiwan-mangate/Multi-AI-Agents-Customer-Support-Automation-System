from repositories.ticket_repository import TicketRepository
from crm_agent.db.connection import SessionLocal

def test_ticket_signals():
    repo = TicketRepository()
    target_id = 1
    target_category = "refund_request"

    print(f"🚀 Testing Behavioral Signals for Customer ID: {target_id}\n")
    
    try:
        unresolved_repeats = repo.count_unresolved_repeat_issues(target_id, target_category)
        print(f"📊 [SIGNAL] Unresolved Repeat '{target_category}': {unresolved_repeats}")

        fourteen_day_spike = repo.get_recent_ticket_count(target_id, days=14)
        print(f"📊 [SIGNAL] 14-Day Ticket Spike: {fourteen_day_spike}")

        last_sentiment = repo.get_last_ticket_sentiment(target_id)
        print(f"📊 [SIGNAL] Last Known Sentiment: {last_sentiment}")
    
        print("\n🔎 Operational Analysis:")
        if unresolved_repeats > 0 and last_sentiment == "angry":
            print("⚠️ ALERT: High risk detected. Unresolved loop + Angry sentiment.")
        elif fourteen_day_spike > 2:
            print("📢 NOTICE: Elevated contact frequency detected.")
        else:
            print("✅ Status: Standard operational flow.")

    except Exception as e:
        print(f"❌ Test Failed: {e}")
    finally:
        repo.close()

if __name__ == "__main__":
    test_ticket_signals()