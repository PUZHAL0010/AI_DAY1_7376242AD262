"""Run the four standard questions through all three systems.

Prints a side-by-side summary and saves Output/results.md, which you can use
to fill in the observation table in analysis.md. The Correct? column is an
automatic hint only; always read the answers yourself.

Usage:
    python run_all.py
"""
import os

import chatbot
import workflow
from agent import run_agent
from config import QUESTIONS, looks_correct, timed


def one_line(text: str, limit: int = 110) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def run_system(name, fn, question):
    try:
        out, secs = timed(fn, question["text"])
        text = out["answer"] if isinstance(out, dict) else out
        extra = ""
        if isinstance(out, dict):
            extra = f"{out['steps']} LLM calls, {out['tool_calls']} tool calls"
        return {"system": name, "answer": text, "secs": secs,
                "correct": looks_correct(question, text), "extra": extra}
    except Exception as exc:
        return {"system": name, "answer": f"ERROR: {exc}", "secs": 0.0,
                "correct": False, "extra": ""}


def main() -> None:
    systems = [
        ("Chatbot", chatbot.ask),
        ("Workflow", workflow.answer),
        ("Agent", lambda q: run_agent(q, verbose=False)),
    ]
    rows = []
    for q in QUESTIONS:
        print(f"\n{q['id']} ({q['kind']}): {q['text']}")
        for name, fn in systems:
            r = run_system(name, fn, q)
            r["qid"] = q["id"]
            rows.append(r)
            mark = "PASS" if r["correct"] else "FAIL"
            print(f"  {name:<9} {mark}  {r['secs']:.3f}s  {one_line(r['answer'])}")

    os.makedirs("Output", exist_ok=True)
    with open(os.path.join("Output", "results.md"), "w", encoding="utf-8") as f:
        f.write("| Question | System | Auto-check | Time (s) | Answer |\n")
        f.write("|---|---|---|---|---|\n")
        for r in rows:
            mark = "correct" if r["correct"] else "incorrect"
            f.write(f"| {r['qid']} | {r['system']} | {mark} | {r['secs']:.3f} | "
                    f"{one_line(r['answer'], 90).replace('|', '/')} |\n")
    print("\nSaved Output/results.md")


if __name__ == "__main__":
    main()
