"""System 3: AI agent = LLM + Tools + Loop.

The LLM decides what to do next. If it asks for a tool, we run the tool,
give the result back as an observation, and loop. When the LLM answers
without requesting a tool, the task is finished.

    reason  ->  act (tool call)  ->  observe (tool result)  ->  repeat

Usage:
    python agent.py                        # runs the 4 standard questions
    python agent.py "your question"        # runs one custom question
"""
import sys

from config import LLM_MODEL, cli_questions, get_client, timed
from tools import TOOL_SCHEMAS, run_tool

MAX_STEPS = 8  # safety limit so the loop can never run forever

SYSTEM_PROMPT = (
    "You are a fee assistant for a college. You do NOT know any course fees "
    "from memory. Always use the tools to get fee data, and use the calculator "
    "tool for every arithmetic operation. If a course does not exist, say it "
    "was not found. When you have everything you need, reply with a short "
    "final answer stating amounts in INR."
)


def run_agent(question: str, verbose: bool = True, max_steps: int = MAX_STEPS) -> dict:
    client = get_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    tool_calls_made = 0

    for step in range(1, max_steps + 1):
        # REASON: the LLM looks at everything so far and picks the next move
        response = client.chat.completions.create(
            model=LLM_MODEL, messages=messages, tools=TOOL_SCHEMAS, temperature=0
        )
        msg = response.choices[0].message

        # No tool requested -> the agent believes the task is complete
        if not msg.tool_calls:
            if verbose:
                print(f"  [step {step}] final answer")
            return {"answer": msg.content or "", "steps": step,
                    "tool_calls": tool_calls_made, "finished": True}

        # ACT: record the model's tool requests, then run each tool
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            result = run_tool(tc.function.name, tc.function.arguments)
            tool_calls_made += 1
            if verbose:
                print(f"  [step {step}] ACT     {tc.function.name}({tc.function.arguments})")
                print(f"  [step {step}] OBSERVE {result}")
            # OBSERVE: feed the tool result back so the next reasoning step sees it
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return {"answer": "Stopped: reached the maximum number of steps without finishing.",
            "steps": max_steps, "tool_calls": tool_calls_made, "finished": False}


if __name__ == "__main__":
    print(f"=== AI AGENT: LLM + Tools + Loop (model: {LLM_MODEL}) ===")
    for q in cli_questions(sys.argv):
        print(f"\nQ: {q}")
        try:
            result, secs = timed(run_agent, q)
            print(f"A: {result['answer'].strip()}")
            print(f"   [{secs:.2f}s, {result['steps']} LLM call(s), "
                  f"{result['tool_calls']} tool call(s), finished={result['finished']}]")
        except Exception as exc:
            print(f"ERROR: {exc}\nRun `python check_setup.py` to diagnose.")
            break
