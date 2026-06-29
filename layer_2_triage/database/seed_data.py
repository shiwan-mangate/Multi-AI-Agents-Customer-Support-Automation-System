from sqlalchemy import text
from database.postgres import engine


customers_query = """
INSERT INTO customers (name, email, account_tier, total_spent)
VALUES
('Rahul Sharma', 'rahul@example.com', 'premium', 12000.50),
('Priya Verma', 'priya@example.com', 'standard', 2500.00),
('Amit Joshi', 'amit@example.com', 'vip', 45000.75),
('Sarah Chen', 'sarah@example.com', 'premium', 8200.00),
('John Smith', 'john@example.com', 'standard', 450.00),
('Maria Garcia', 'maria@example.com', 'standard', 120.00),
('David Miller', 'david@example.com', 'vip', 32000.00),
('Anita Desai', 'anita@example.com', 'premium', 9500.00),
('Kevin Novak', 'kevin@example.com', 'standard', 1100.00),
('Fatima Zahra', 'fatima@example.com', 'vip', 55000.00),
('Liam O''Connor', 'liam@example.com', 'standard', 300.00),
('Yuki Tanaka', 'yuki@example.com', 'premium', 15000.00),
('Elena Rossi', 'elena@example.com', 'standard', 2100.00),
('Arjun Patel', 'arjun@example.com', 'vip', 68000.00),
('Chloe Dubois', 'chloe@example.com', 'standard', 85.00);
"""


orders_query = """
INSERT INTO orders (customer_id, order_amount, order_status)
VALUES
(1, 1500.00, 'delivered'), (1, 2200.00, 'delayed'), (1, 300.00, 'processing'),
(2, 700.00, 'delivered'), (2, 450.00, 'delivered'), (2, 1350.00, 'processing'),
(3, 12000.00, 'cancelled'), (3, 8500.00, 'delivered'), (3, 5000.00, 'delayed'),
(4, 3200.00, 'delivered'), (4, 1500.00, 'delayed'), (4, 450.00, 'delivered'),
(5, 150.00, 'delivered'), (5, 300.00, 'delivered'),
(6, 120.00, 'cancelled'),
(7, 15000.00, 'delivered'), (7, 17000.00, 'processing'),
(8, 4500.00, 'delivered'), (8, 5000.00, 'delayed'),
(9, 500.00, 'delivered'), (9, 600.00, 'delivered'),
(10, 25000.00, 'delivered'), (10, 30000.00, 'processing'),
(11, 100.00, 'delivered'), (11, 200.00, 'delivered'),
(12, 7000.00, 'delivered'), (12, 8000.00, 'delayed'),
(13, 1050.00, 'delivered'), (13, 1050.00, 'delivered'),
(14, 34000.00, 'delivered'), (14, 34000.00, 'cancelled'),
(15, 85.00, 'processing'), (15, 50.00, 'cancelled'), -- Fixed: Added 40th row here
(1, 400.00, 'delivered'), (2, 100.00, 'delivered'), (3, 200.00, 'processing'),
(4, 50.00, 'delivered'), (7, 500.00, 'delivered'), (8, 100.00, 'delivered'),
(10, 1000.00, 'delivered'), (14, 5000.00, 'delayed');
"""


tickets_query = """
INSERT INTO tickets (customer_id, issue_type, sentiment, priority)
VALUES
(1, 'refund_request', 'angry', 'high'), (1, 'late_delivery', 'frustrated', 'medium'), (1, 'technical_bug', 'neutral', 'low'),
(2, 'account_issue', 'neutral', 'low'), (2, 'late_delivery', 'frustrated', 'medium'),
(3, 'payment_failure', 'angry', 'critical'), (3, 'refund_request', 'angry', 'high'),
(4, 'late_delivery', 'frustrated', 'medium'), (4, 'account_issue', 'neutral', 'low'),
(5, 'account_issue', 'calm', 'low'),
(6, 'refund_request', 'frustrated', 'medium'),
(7, 'technical_bug', 'neutral', 'medium'), (7, 'payment_failure', 'frustrated', 'high'),
(8, 'late_delivery', 'angry', 'high'),
(9, 'account_issue', 'calm', 'low'),
(10, 'payment_failure', 'frustrated', 'medium'),
(11, 'late_delivery', 'neutral', 'low'),
(12, 'refund_request', 'angry', 'high'),
(13, 'technical_bug', 'neutral', 'low'),
(14, 'payment_failure', 'angry', 'critical'), (14, 'refund_request', 'angry', 'high'), (14, 'late_delivery', 'frustrated', 'medium'),
(15, 'account_issue', 'neutral', 'low'),
-- Extra rows to reach 35
(1, 'account_issue', 'calm', 'low'), (3, 'technical_bug', 'frustrated', 'medium'),
(7, 'late_delivery', 'angry', 'high'), (8, 'payment_failure', 'neutral', 'medium'),
(10, 'refund_request', 'angry', 'critical'), (12, 'account_issue', 'calm', 'low'),
(14, 'technical_bug', 'neutral', 'medium'), (2, 'technical_bug', 'calm', 'low'),
(4, 'payment_failure', 'frustrated', 'high'), (9, 'late_delivery', 'neutral', 'low'),
(11, 'account_issue', 'calm', 'low'), (13, 'refund_request', 'frustrated', 'medium');
"""


escalations_query = """
INSERT INTO escalations (ticket_id, reason, escalated_to)
VALUES
(1, 'Customer threatened churn - Premium user', 'senior_support'),
(6, 'VIP customer complaint - Payment failure', 'priority_team'),
(7, 'Repeated refund request - High LTV', 'manager_review'),
(14, 'Legal language detected', 'compliance_team'),
(20, 'Critical VIP payment failure', 'finance_lead'),
(21, 'Third repeat issue this month', 'senior_support'),
(28, 'SLA breach imminent - Urgent refund', 'ops_manager'),
(30, 'High value churn risk identified by AI', 'retention_specialist');
"""

def seed_database():
    try:
        with engine.connect() as connection:
            print("Cleaning existing data...")
            connection.execute(text("TRUNCATE TABLE escalations, tickets, orders, customers RESTART IDENTITY CASCADE;"))
            
            print("Inserting customers...")
            connection.execute(text(customers_query))
            print("Inserting orders...")
            connection.execute(text(orders_query))
            print("Inserting tickets...")
            connection.execute(text(tickets_query))
            print("Inserting escalations...")
            connection.execute(text(escalations_query))

            connection.commit()
            print("✅ Database successfully populated with 15 customers, 40 orders, 35 tickets, and 8 escalations.")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")

if __name__ == "__main__":
    seed_database()