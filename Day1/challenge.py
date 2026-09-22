"""Challenge: a harder budget question that needs several steps.

The question has no course code and needs lookups + arithmetic + comparison.
The rule-based workflow has no rule for it; the agent plans its own steps.

Usage:
    python challenge.py
"""
from agent import run_agent
from config import CHALLENGE_QUESTION, timed
from workflow import answer as workflow_answer


def main() -> None:
    print(f"CHALLENGE QUESTION:\n  {CHALLENGE_QUESTION}\n")

    print("--- RULE-BASED WORKFLOW ---")
    result, secs = timed(workflow_answer, CHALLENGE_QUESTION)
    print(f"A: {result}\n   [{secs * 1000:.2f} ms]\n")

    print("--- AI AGENT ---")
    try:
        result, secs = timed(run_agent, CHALLENGE_QUESTION)
        print(f"A: {result['answer'].strip()}")
        print(f"   [{secs:.2f}s, {result['steps']} LLM call(s), "
              f"{result['tool_calls']} tool call(s), finished={result['finished']}]")
    except Exception as exc:
        print(f"ERROR: {exc}\nRun `python check_setup.py` to diagnose.")

    print("\nCorrect pairs for reference: CS101+AI202=30000 (5000 left), "
          "CS101+DS303=27000 (8000 left), AI202+DS303=33000 (2000 left).")


if __name__ == "__main__":
    main()
