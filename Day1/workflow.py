"""System 2: Rule-based workflow.

Pure Python if/else + regex. NO LLM is involved anywhere in this file.
It reads the private data directly and follows fixed, predefined rules, so it
is fast and perfectly repeatable, but it only understands phrasings its
author anticipated.

Usage:
    python workflow.py                     # runs the 4 standard questions
    python workflow.py "your question"     # runs one custom question
"""
import re
import sys

from config import COURSE_DB, cli_questions, timed

CODE_PATTERN = re.compile(r"\b([A-Za-z]{2,3}\d{3})\b")
FEE_WORDS = ("fee", "cost", "price", "how much")
TOTAL_WORDS = ("total", "sum", "together", "combined", "both")
LIST_WORDS = ("list", "all courses", "available", "which courses are")


def answer(question: str) -> str:
    q = question.lower()
    codes = [c.upper() for c in CODE_PATTERN.findall(question)]

    # Rule 1: the question names a course code we do not have
    unknown = [c for c in codes if c not in COURSE_DB]
    if unknown:
        return f"Course {', '.join(unknown)} not found. Known courses: {', '.join(COURSE_DB)}."

    # Rule 2: asks to list courses
    if any(w in q for w in LIST_WORDS):
        return "\n".join(f"{c}: {d['fee']} INR" for c, d in COURSE_DB.items())

    # Rule 3: total for two or more named courses
    if len(codes) >= 2 and any(w in q for w in TOTAL_WORDS):
        total = sum(COURSE_DB[c]["fee"] for c in codes)
        return f"Total fee for {' + '.join(codes)} = {total} INR."

    # Rule 4: fee of exactly one named course
    if len(codes) == 1 and any(w in q for w in FEE_WORDS):
        code = codes[0]
        return f"{code} ({COURSE_DB[code]['title']}) fee = {COURSE_DB[code]['fee']} INR."

    # Default: no rule matched
    return ("Sorry, I did not understand that. Try: 'What is the fee for CS101?', "
            "'Total fee for CS101 and AI202', or 'List all courses'.")


if __name__ == "__main__":
    print("=== RULE-BASED WORKFLOW (no LLM) ===")
    for q in cli_questions(sys.argv):
        print(f"\nQ: {q}")
        result, secs = timed(answer, q)
        print(f"A: {result}")
        print(f"   [{secs * 1000:.2f} ms, 0 LLM calls, rules only]")
