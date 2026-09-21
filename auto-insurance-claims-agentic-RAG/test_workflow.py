import argparse
import json
from insurance_claim_processor import process_claim

def main():
    parser = argparse.ArgumentParser(description='Process an insurance claim')
    parser.add_argument('--file', type=str, help='Path to claim JSON file')
    args = parser.parse_args()
    
    if not args.file:
        print("Please provide a path to a claim JSON file using --file")
        return
    
    print(f"Processing claim from {args.file}...")
    
    try:
        decision, logs = process_claim(claim_json_path=args.file)
        
        print("\n" + "="*50)
        print("CLAIM DECISION:")
        print(decision.model_dump_json(indent=2))
        print("="*50)
    except Exception as e:
        print(f"Error processing claim: {str(e)}")

if __name__ == "__main__":
    main()