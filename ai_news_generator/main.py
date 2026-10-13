#!/usr/bin/env python3
"""
Main entry point for the AI News Generator using CrewAI Flows.

This script provides a command-line interface to generate news content
using the NewsGeneratorFlow implementation.
"""

import argparse
import sys
from typing import Optional
from news_flow import NewsGeneratorFlow


def main():
    """
    Main function to run the AI News Generator Flow from command line.
    """
    parser = argparse.ArgumentParser(
        description="Generate AI news content using CrewAI Flows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --topic "Latest developments in artificial intelligence"
  python main.py --topic "Climate change solutions" --output article.md
        """
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Topic to research and write about"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file to save the generated content (optional)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if not args.topic.strip():
        print("Error: Topic cannot be empty", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"🚀 Starting AI News Generator Flow for topic: '{args.topic}'")
        print("📊 Initializing research phase...")
        
        # Create and run the flow
        flow = NewsGeneratorFlow()
        result = flow.kickoff(inputs={"topic": args.topic})
        
        # Convert result to string if it's not already
        content = str(result)
        
        print("✅ Content generation completed!")
        
        # Save to file if specified
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Content saved to: {args.output}")
            except IOError as e:
                print(f"Error saving file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Print to stdout
            print("\n" + "="*80)
            print("GENERATED CONTENT:")
            print("="*80)
            print(content)
            print("="*80)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())