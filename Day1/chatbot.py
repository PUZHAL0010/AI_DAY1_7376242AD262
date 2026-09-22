"""System 1: Plain chatbot.

The question goes straight to the LLM. No private data, no tools, no loop.
Expect confident but WRONG (hallucinated) fees, because the model has never
seen this college's fee data.

Usage:
    python chatbot.py                      # runs the 4 standard questions
    python chatbot.py "your question"      # runs one custom question
"""
import sys

from config import LLM_MODEL, cli_questions, get_client, timed


def ask(question: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=0,
    )
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    print(f"=== PLAIN CHATBOT (model: {LLM_MODEL}) ===")
    for q in cli_questions(sys.argv):
        print(f"\nQ: {q}")
        try:
            answer, secs = timed(ask, q)
            print(f"A: {answer.strip()}")
            print(f"   [{secs:.2f}s, 1 LLM call, 0 tools]")
        except Exception as exc:
            print(f"ERROR: {exc}\nRun `python check_setup.py` to diagnose.")
            break
