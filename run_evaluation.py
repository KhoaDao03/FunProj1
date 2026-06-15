"""
run_evaluation.py — Evaluation helper

Runs the 5 evaluation questions from planning.md through the full pipeline and
prints results in a format that is easy to paste into README.md.

Usage:
    python run_evaluation.py

Note: The Groq free tier allows 100,000 tokens per day. If you hit the limit,
the script will print the partial results and tell you how long to wait.
"""

import time
from groq import RateLimitError
from query import ask


def ask_with_retry(question, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return ask(question)
        except RateLimitError as e:
            if attempt < max_retries:
                print(f"  [Rate limit hit — waiting 60s before retry {attempt + 1}/{max_retries}]")
                time.sleep(60)
            else:
                return {
                    "answer": f"[Rate limit exceeded — run again later. Error: {e}]",
                    "sources": [],
                }

evaluation_questions = [
    {
        "id": 1,
        "question": "What was NVIDIA's total revenue for fiscal year 2025?",
        "expected": "~$130.5 billion (verify in NVDA-K10-2025.pdf, Item 8 Financial Statements)",
    },
    {
        "id": 2,
        "question": "What does Intel's 2025 10-K identify as its primary competitive risks in the semiconductor market?",
        "expected": "Competition from AMD, ARM-based chips, manufacturing delays relative to TSMC (verify in INTC-K10-2025.pdf, Item 1A Risk Factors)",
    },
    {
        "id": 3,
        "question": "How did Apple's iPhone revenue change between its 2024 and 2025 10-K filings?",
        "expected": "~$201B (FY2024) → ~$209B (FY2025) — verify in AAPL-K10-2024.pdf and AAPL-K10-2025.pdf, Item 8",
    },
    {
        "id": 4,
        "question": "According to SpaceX's S-1 registration statement, what is the intended use of proceeds from the offering?",
        "expected": "Specific allocation from the 'Use of Proceeds' section in SPCX-S1-2026.pdf",
    },
    {
        "id": 5,
        "question": "What was Amazon's AWS segment operating income for fiscal year 2025?",
        "expected": "~$45.6 billion (verify in AMZN-K10-2025.pdf, Item 7 segment results table)",
    },
]

DIVIDER = "=" * 72

def main():
    print(DIVIDER)
    print("SEC Filings RAG — Evaluation Report")
    print(DIVIDER)

    for item in evaluation_questions:
        result = ask_with_retry(item["question"])

        print(f"\n## Question {item['id']}")
        print(f"Question  : {item['question']}")
        print(f"Expected  : {item['expected']}")
        print(f"Response  : {result['answer']}")
        print("Sources   :")
        if result["sources"]:
            for s in result["sources"]:
                print(f"            - {s}")
        else:
            print("            (none — fallback triggered)")
        print("Judgment  : [accurate / partially accurate / inaccurate]")
        print()

    print(DIVIDER)
    print("Fill in the Judgment field for each question, then paste into README.md.")
    print(DIVIDER)


if __name__ == "__main__":
    main()
