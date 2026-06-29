import json
import logging
from app.nodes.supervisor_node import supervisor_node 
from mock_builder import build_mock_ticket


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eval_runner")

def run_layer_1_evals():
    try:
        with open("golden_dataset.json", "r") as f:
            dataset = json.load(f)
    except FileNotFoundError:
        logger.error("Dataset not found at evals/golden_dataset.json")
        return

    results = []
    system_errors = []  
    
    logger.info(f"Running Evaluation on {len(dataset)} cases.")

    for case in dataset:
        metadata_payload = {
            "customer_info": case.get("customer_metadata", {}),
            "language": case.get("language", "english"),
            "priority": case.get("priority", "medium")
        }

        mock_ticket = build_mock_ticket(
            case_id=case.get("case_id"),
            input_text=case.get("input"),
            metadata=metadata_payload
        )

        try:
            prediction = supervisor_node(mock_ticket)

            results.append({
                "case": case,
                "prediction": prediction.model_dump()
            })

        except Exception as e:
            
            logger.error(f"System Crash on {case.get('case_id')}: {str(e)}")

            system_errors.append({
                "case_id": case.get("case_id"),
                "error": str(e)
            })

    display_metrics(results, system_errors)


def display_metrics(results, system_errors):
    total_attempted = len(results) + len(system_errors)

    if total_attempted == 0:
        return

    intent_correct = 0
    route_correct = 0

    print("\n" + "=" * 60)
    print("LAYER 1 ORCHESTRATION BENCHMARK")
    print("=" * 60)

    for r in results:
        expected = r["case"].get("expected", {}) 
        actual = r["prediction"]

        
        i_match = actual.get("intent") == expected.get("intent")
        r_match = actual.get("route_to") == expected.get("route_to")

        if i_match:
            intent_correct += 1

        if r_match:
            route_correct += 1

        if not i_match or not r_match:
            print(f"\nLOGIC FAILURE: {r['case'].get('case_id')}")
            print(f"Input: {r['case'].get('input')[:50]}...")
            print(f"Expected Intent: {expected.get('intent')}")
            print(f"Actual Intent:   {actual.get('intent')}")
            print("-" * 40)

   
    for err in system_errors:
        print(f"\nSYSTEM ERROR: {err['case_id']}")
        print(f"Details: {err['error']}")
        print("-" * 40)

    print("\nFINAL PERFORMANCE METRICS")
    print(f"Intent Accuracy:    {(intent_correct / len(results)) * 100:.2f}%"
          if results else "N/A")

    print(f"Routing Accuracy:   {(route_correct / len(results)) * 100:.2f}%"
          if results else "N/A")

    print(f"System Reliability: {((len(results)) / total_attempted) * 100:.2f}%")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_layer_1_evals()