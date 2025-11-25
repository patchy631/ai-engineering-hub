import argparse
import mimetypes
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from evaluation_geval import create_evaluator_geval

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".docx"}


def discover_invoice_files(folder: Path) -> List[Path]:
    """Discover invoice files in the specified folder."""
    if not folder.exists():
        raise FileNotFoundError(f"Folder {folder} does not exist")
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS]
    if len(files) < 2:
        raise ValueError("Please provide at least two invoice files for a meaningful evaluation.")
    return files


def infer_mime_type(file_path: Path) -> str:
    """Infer MIME type for the given file path."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def main():
    parser = argparse.ArgumentParser(
        description="Run Ground X vs GPT-4o invoice evaluation using GEval metrics."
    )
    parser.add_argument(
        "invoices_folder",
        type=str,
        help="Path to folder containing invoice files (PDF/PNG/JPG/etc.)"
    )
    args = parser.parse_args()

    invoices_folder = Path(args.invoices_folder).expanduser().resolve()
    invoice_paths = discover_invoice_files(invoices_folder)

    print("Enter evaluation questions one per line; press ENTER on an empty line to finish:\n")
    questions: List[str] = []
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            if questions:
                break
            print("Please enter at least one question.")
            continue
        questions.append(line)

    print(f"Found {len(invoice_paths)} invoice files.")
    print(f"Collected {len(questions)} evaluation questions.")

    load_dotenv()

    print("Creating evaluator (checking API keys)...")
    evaluator = create_evaluator_geval()

    invoice_data: List[Dict] = []
    for path in invoice_paths:
        print(f"Processing {path.name} with Ground X...")
        mime_type = infer_mime_type(path)
        try:
            xray_data = evaluator.process_invoice(str(path), path.name, mime_type)
            raw_bytes = path.read_bytes()
            invoice_data.append({
                "name": path.name,
                "xray_data": xray_data,
                "raw_bytes": raw_bytes,
                "mime_type": mime_type,
                "expected_outputs": {}
            })
            print(f"Processed {path.name} successfully.")
        except Exception as e:
            print(f"Failed to process {path.name}: {e}")
            return

    # Predefined expected answers for evaluation
    EXPECTED_ANSWERS = {
        "electricity": {
            "what is only the customer number:": "453987",
            "previous reading of water commercial:": "11,555,400",
            "how much is payment made on jun 17:": "data not available",
            "what is the account number:": "78356",
            "what is the due date?": "07/11/2024",
            # Question variations for flexible matching
            "customer number": "453987",
            "customer": "453987",
            "only customer number": "453987",
            "water commercial reading": "11,555,400",
            "previous water reading": "11,555,400",
            "commercial water reading": "11,555,400",
            "payment jun 17": "data not available",
            "payment made jun 17": "data not available",
            "account number": "78356",
            "account": "78356",
            "due date": "07/11/2024",
            "payment due date": "07/11/2024",
            "july 11 2024": "07/11/2024",
        },
        "energy-plus": {
            "what is only the customer number:": "data not available",
            "previous reading of water commercial:": "data not available",
            "how much is payment made on jun 17:": "$ 7,609.87cr",
            "what is the account number?": "0007873-98",
            "what is the due date?": "Jul 30, 2024",
            # Question variations for flexible matching
            "customer number": "data not available",
            "customer": "data not available",
            "only customer number": "data not available",
            "water commercial reading": "data not available",
            "previous water reading": "data not available",
            "commercial water reading": "data not available",
            "payment jun 17": "$ 7,609.87cr",
            "payment made jun 17": "$ 7,609.87cr",
            "account number": "0007873-98",
            "account": "0007873-98",
            "due date": "Jul 30, 2024",
            "payment due date": "Jul 30, 2024",
            "july 30 2024": "Jul 30, 2024",
        },
    }

    # Match user questions with expected answers
    for inv in invoice_data:
        base = Path(inv["name"]).stem.lower()
        if base in EXPECTED_ANSWERS:
            for q in questions:
                # Flexible matching implementation
                q_lower = q.lower().strip()
                matched = False
                
                for expected_q, expected_a in EXPECTED_ANSWERS[base].items():
                    expected_q_lower = expected_q.lower().strip()
                    
                    # Exact match validation
                    if q_lower == expected_q_lower:
                        inv["expected_outputs"][q] = expected_a
                        matched = True
                        break
                    
                    # Partial match validation using key identifying words
                    elif _smart_partial_match(q_lower, expected_q_lower):
                        inv["expected_outputs"][q] = expected_a
                        matched = True
                        break
                
                if not matched:
                    # Default expected output for unmatched questions
                    inv["expected_outputs"][q] = "data not available"

    # Brief summary of expected outputs setup
    print(f"\n✓ Configured expected outputs for {len(invoice_data)} files")
    print(f"✓ Ready to evaluate {len(questions)} questions\n")

    print("Running evaluation (Ground X vs GPT-4o)... This may take a while.")
    results = evaluator.run(invoice_data, questions)

    gx_results = results["groundx_parsing"]
    gpt_results = results["gpt4o_direct"]

    print("\n=== Evaluation Summary ===")
    
    # Calculate average scores for comparison
    gx_scores = [result["overall_score"] for result in gx_results if "overall_score" in result]
    gpt_scores = [result["overall_score"] for result in gpt_results if "overall_score" in result]
    
    gx_avg = sum(gx_scores) / len(gx_scores) if gx_scores else 0
    gpt_avg = sum(gpt_scores) / len(gpt_scores) if gpt_scores else 0
    
    print(f"Average Score: Ground X {gx_avg:.1f}/10 | GPT-4o {gpt_avg:.1f}/10 -> {'Ground X' if gx_avg > gpt_avg else 'GPT-4o'} wins")
    
    # Display detailed evaluation results
    print(f"\nDetailed Results:")
    for i, (gx_result, gpt_result) in enumerate(zip(gx_results, gpt_results)):
        gx_score = gx_result.get("overall_score", 0)
        gpt_score = gpt_result.get("overall_score", 0)
        print(f"Question {i+1}: Ground X {gx_score:.1f}/10 | GPT-4o {gpt_score:.1f}/10")
        if gx_result.get("reason"):
            print(f"  Ground X reason: {gx_result['reason']}")
        if gpt_result.get("reason"):
            print(f"  GPT-4o reason: {gpt_result['reason']}")
        print()

    dataset = results.get("dataset")
    if dataset:
        print(f"\nResults uploaded to Opik dataset ID: {getattr(dataset, 'id', 'unknown')} (GroundX vs GPT4o)")
    print("Done.")


def _smart_partial_match(user_question: str, expected_question: str) -> bool:
    """
    Smart partial matching that identifies key words in questions.
    
    Args:
        user_question: The question provided by the user
        expected_question: The expected question format
        
    Returns:
        bool: True if the questions match based on key identifying words
    """
    # Key word patterns for question identification
    key_words = {
        "account number": ["account", "number"],
        "customer number": ["customer", "number"],
        "only customer number": ["only", "customer", "number"],
        "water commercial reading": ["water", "commercial", "reading"],
        "previous water reading": ["previous", "water", "reading"],
        "commercial water reading": ["commercial", "water", "reading"],
        "payment jun 17": ["payment", "jun", "17"],
        "payment made jun 17": ["payment", "made", "jun", "17"],
        "due date": ["due", "date"],
        "payment due date": ["payment", "due", "date"],
        "july 11 2024": ["july", "11", "2024"],
        "july 30 2024": ["july", "30", "2024"],
    }
    
    # Validate if expected question contains key word patterns
    for pattern, required_words in key_words.items():
        if pattern in expected_question:
            # Check if user question contains all required words
            if all(word in user_question for word in required_words):
                return True
    
    return False


if __name__ == "__main__":
    main()
