"""Verify that Python packages, LLM connection, and tool calling all work."""
import sys

from config import LLM_BASE_URL, LLM_MODEL, get_client


def main() -> int:
    print(f"Endpoint : {LLM_BASE_URL}")
    print(f"Model    : {LLM_MODEL}\n")

    try:
        import openai  # noqa: F401
        print("[OK] openai package installed")
    except ImportError:
        print("[FAIL] openai package missing -> run: pip install -r requirements.txt")
        return 1

    client = get_client()

    try:
        reply = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "Reply with the single word: OK"}],
            temperature=0,
        ).choices[0].message.content
        print(f"[OK] LLM responded: {reply.strip()!r}")
    except Exception as exc:
        print(f"[FAIL] Could not reach the LLM: {exc}")
        print("       Check LLM_BASE_URL / LLM_MODEL / LLM_API_KEY in your .env file.")
        print("       For Ollama: is `ollama serve` running and the model pulled?")
        return 1

    # The agent needs a model that supports tool calling
    try:
        from tools import TOOL_SCHEMAS

        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "Use the tool to get the fee of CS101."}],
            tools=TOOL_SCHEMAS,
            temperature=0,
        )
        if resp.choices[0].message.tool_calls:
            print("[OK] Model supports tool calling")
        else:
            print("[WARN] Model answered without calling a tool. It may not support "
                  "tool calling well; try llama3.1, qwen2.5, or a hosted model.")
    except Exception as exc:
        print(f"[FAIL] Tool-calling request failed: {exc}")
        print("       Choose a model that supports function calling.")
        return 1

    print("\nAll checks passed. You are ready to run the three systems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
