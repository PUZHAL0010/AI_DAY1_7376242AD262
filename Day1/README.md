# Day 1: Plain Chatbot vs Rule-Based Workflow vs AI Agent

Agentic AI: Foundations and Open-Source Practice, Unit 1 (Agent = LLM + Tools + Loop).

The same private-data problem, answering questions about **college course fees**
(CS101 = 12,000, AI202 = 18,000, DS303 = 15,000 INR), solved three ways:

| System | File | How it works |
|---|---|---|
| 1. Plain chatbot | `chatbot.py` | Question goes straight to the LLM. No data, no tools. |
| 2. Rule-based workflow | `workflow.py` | Python if/else + regex. No LLM at all. |
| 3. AI agent | `agent.py` + `tools.py` | LLM + tools (fee lookup, calculator) in a reason, act, observe loop. |

**The written analysis is in [`analysis.md`](analysis.md).** Read that first.

## Setup

```bash
cd Day1
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit .env (see options inside)
python check_setup.py             # confirms LLM connection + tool calling
```

Any OpenAI-compatible endpoint works: Ollama (local, open-source), Groq, OpenRouter,
LM Studio, vLLM. The model must support **tool calling** for the agent
(for example `llama3.1`, `qwen2.5`, `llama-3.3-70b-versatile`).

## Run

```bash
python tests_offline.py   # no LLM needed: checks tools, workflow, and the agent loop logic
python chatbot.py         # System 1 on the 4 standard questions
python workflow.py        # System 2
python agent.py           # System 3 (prints every act/observe step)
python challenge.py       # harder budget question: workflow vs agent
python run_all.py         # all systems side by side, saves Output/results.md
```

Any script also accepts a custom question: `python agent.py "Which course is cheapest?"`.

## Files

```
config.py         shared settings, the private course-fee data, test questions
tools.py          tools for the agent: get_course_fee, list_courses, calculator
chatbot.py        system 1
workflow.py       system 2
agent.py          system 3 (the loop)
check_setup.py    connection and tool-calling check
challenge.py      harder multi-step question
run_all.py        runs everything and writes Output/results.md
tests_offline.py  tests that need no LLM
analysis.md       written analysis (submission document)
Output/           screenshots of all three systems running
```

## Pushing to GitHub

This folder is `Day1/` inside the repository `AI-Fluency-Training-<Roll Number>`.
The repo-level `.gitignore` (which contains `.env`) is in the repository root, one level up.
See the root README for the push commands.
