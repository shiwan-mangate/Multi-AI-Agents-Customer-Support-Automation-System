import os
from dotenv import load_dotenv
from layer_2_faq.ingestion.ingest_pipeline import FAQIngestionPipeline

load_dotenv()

FAQ_FILES = [
    ("layer_2_faq/knowledge_base/account_and_billing_faq1.md", "account_and_billing_faq"),
    ("layer_2_faq/knowledge_base/order_cancellation_faq.md", "order_cancellation_faq"),
    ("layer_2_faq/knowledge_base/privacy_and_data_faq1.md", "privacy_and_data_faq"),
    ("layer_2_faq/knowledge_base/product_warranty_faq1.md", "product_warranty_faq"),
    ("layer_2_faq/knowledge_base/refund_policy_faq.md", "refund_policy_faq"),
    ("layer_2_faq/knowledge_base/return_policy_faq.md", "return_policy_faq"),
    ("layer_2_faq/knowledge_base/shipping_policy_faq.md", "shipping_policy_faq"),
    ("layer_2_faq/knowledge_base/subscription_terms_faq.md", "subscription_terms_faq"),
    ("layer_2_faq/knowledge_base/technical_support_faq1.md", "technical_support_faq"),
]

def main():
    pipeline = FAQIngestionPipeline()

    for file_path, doc_name in FAQ_FILES:
        print(f"\nIngesting: {doc_name}")
        pipeline.run(file_path, doc_name)

    print("\nVector DB population complete.")

if __name__ == "__main__":
    main()