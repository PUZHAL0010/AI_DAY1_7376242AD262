# Comparing a Plain Chatbot, a Rule-Based Workflow, and an AI Agent on a Course-Fee Scenario

## 1. The scenario

I chose a small private-data problem: answering questions about the tuition fees of courses at a college. The fee data lives in a private table with three entries: CS101 (Introduction to Programming) costs 12,000 INR, AI202 (Applied Machine Learning) costs 18,000 INR, and DS303 (Data Science Foundations) costs 15,000 INR. This data is stored only in my project (`config.py`), so no public language model has ever seen it. That makes the scenario a clean test: any correct answer must come from actually reaching the private data, not from what a model absorbed during training.

I built three systems for it and tested them on four questions. Q1 is a direct lookup ("What is the fee for CS101?"). Q2 is the same kind of lookup phrased differently ("What would I have to pay for AI202?"). Q3 needs a lookup and arithmetic ("What is the total fee if I take CS101 and DS303 together?"). Q4 asks about a course that does not exist ("What is the fee for ML404?"). I also wrote a harder challenge question: "I have 35000 rupees to spend. Which two of the courses could I afford together, and how much money would I have left over?" All code is in this repository, and screenshots of each system running are in the `Output` folder.

## 2. Explanation of each approach

### 2.1 The plain chatbot (`chatbot.py`)

The plain chatbot is the simplest of the three. It takes the user's question, sends it directly to the language model in a single call, and prints whatever text comes back. It uses no data of mine, no tools, and no rules. Its only source of knowledge is what the model learned during training, which means it cannot access my private fee table in any way. The request flows from start to finish in one step: question in, generated text out. There is no lookup, no checking, and no second step.

The limitation shows up immediately on this scenario. When asked for the fee of CS101, the model has nothing to look up, so it either admits it does not know or produces a plausible-sounding number that it has effectively invented. Language models generate the most likely-sounding continuation of the text, and a confident fee figure is a likely-sounding continuation, whether or not it is true. A hallucinated fee is worse than no answer, because a student could act on it. The chatbot is also unable to tell that ML404 does not exist in my database, because it has no database to consult. The chatbot is a fair demonstration of what an LLM alone provides: fluent language and general knowledge, but no access to private facts and no way to verify its own claims.

### 2.2 The rule-based workflow (`workflow.py`)

The rule-based workflow contains no language model at all. It is ordinary Python: a regular expression pulls course codes such as CS101 out of the question, and a fixed sequence of if/else rules decides what to do. If the question names a code that is not in the database, it reports that the course was not found. If the question asks to list courses, it prints the table. If it names two or more codes and contains a word like "total" or "together", it adds their fees. If it names exactly one code and contains a word like "fee" or "cost", it returns that course's fee. If no rule matches, it prints a fallback message explaining what it can handle. It reads the private data directly from the same table the other systems use, so it can be fully accurate on the questions it was designed for.

It needs rules but no tools in the agentic sense: the author decides every step in advance, and the program never chooses between alternatives. Its strengths are speed, zero cost per question, and complete repeatability, since the same input always gives the same output. Its limitations also appear clearly on this scenario. Q2 asks the same thing as Q1 but uses the word "pay", which my keyword list does not contain, so the workflow falls through to its fallback message even though a human would see the two questions as identical. On the challenge question there are no course codes and no matching rule at all, so the workflow cannot begin. The workflow cannot generalize beyond the phrasings and situations its author imagined. Every new kind of question needs a new rule written by a person.

### 2.3 The AI agent (`agent.py` and `tools.py`)

The AI agent combines three parts: an LLM, a set of tools, and a loop. The LLM is the reasoning component. The tools give it real access to the private data and to exact arithmetic: `get_course_fee` looks up one course in the fee table, `list_courses` returns the whole table, and `calculator` safely evaluates arithmetic expressions. The loop is what makes the system agentic. On each pass, the LLM sees the conversation so far and either asks to call a tool or gives a final answer. If it asks for a tool, the program runs that tool and appends the result to the conversation as an observation, then the LLM reasons again with that new information. The cycle of reason, act, observe repeats until the LLM answers without requesting another tool. I also capped the loop at eight steps so a confused model cannot run forever.

For Q3, for example, the agent can look up CS101, look up DS303, pass "12000 + 15000" to the calculator, and only then state the total, with each step chosen by the model rather than scripted by me. For the challenge question, no fixed rule exists, yet the agent can list the courses, compute the cost of each pair, compare them with the 35,000 INR budget, and report the leftover money. For Q4 it can call the lookup tool, see the "not found" error as an observation, and report honestly that ML404 does not exist. Because it reads its data through tools, it does not have to guess. Its limitations are different from the other two systems. It is slower, since each loop pass is a separate LLM call, and it costs more per question. Its behavior is less predictable, because the model chooses the steps: it might skip a needed lookup, call the wrong tool, or do arithmetic in its head despite instructions, which is why the system prompt insists on the calculator. The step limit and the plain error messages returned by the tools are there to keep those failures contained.

## 3. Comparison table

| Basis | Plain chatbot | Rule-based workflow | AI agent |
|---|---|---|---|
| Flexibility | High in language: understands any phrasing, but cannot use my data | Very low: only understands the phrasings its rules were written for (Q2 fails) | High: understands rephrased and unforeseen questions |
| Decision-making | The LLM generates text; makes no decision about data | Fixed if/else conditions written by the developer; no reasoning | The LLM decides what to do next at every step, based on observations |
| Tool usage | None | None as such; hard-coded lookup logic inside the rules | Chooses among fee lookup, course listing, and calculator |
| Private-data access | None: cannot see the fee table, so it guesses or admits ignorance | Direct: reads the table in code | Through tools: reads the table only when it calls a tool |
| Multi-step task handling | None: one call, one answer | Only steps pre-built into a rule (e.g. sum of two named courses); challenge question fails | Yes: chains lookups, arithmetic, and comparison until done |
| Automation | Answers text only; performs no actions | High for known cases: runs unattended, instantly, at no LLM cost | High for open-ended cases: plans and executes its own steps, at higher cost and latency |
| Reliability | Low on private facts: risks confident wrong answers | Very high inside its rules (deterministic); breaks outside them | Good but not guaranteed: grounded by tools, yet the model can still skip or misuse a step |

The table shows a trade-off. The chatbot is flexible in language but blind to my data. The workflow is dependable but brittle. The agent gets the flexibility of an LLM while staying grounded in real data, in exchange for speed, cost, and some predictability.

## 4. Observed results

> **TODO before submitting:** run `python run_all.py` and `python challenge.py` with your own model, then replace every "fill in" cell below with what you actually saw, and delete this note. The automatic check in `run_all.py` is only a hint, so read each answer yourself. Also update the paragraph beneath the table if your results differ from what I expected.

Model used: fill in (for example, llama3.1 via Ollama).

| Question | Chatbot | Workflow | Agent |
|---|---|---|---|
| Q1: fee of CS101 (correct: 12,000) | fill in: answer, correct?, time | fill in | fill in |
| Q2: rephrased, AI202 (correct: 18,000) | fill in | fill in | fill in |
| Q3: total of CS101 + DS303 (correct: 27,000) | fill in | fill in | fill in |
| Q4: ML404 does not exist | fill in | fill in | fill in |
| Challenge: 35,000 budget | not run | fill in | fill in |

Summary of what I observed: fill in two or three sentences on correctness, response time, and how many LLM and tool calls the agent needed.

## 5. Suitability analysis

For this scenario, the AI agent is the most suitable of the three, with the rule-based workflow as a close second for the simplest questions. The chatbot is ruled out first. The scenario is defined by private data, and the comparison table shows that a plain chatbot has no private-data access. Whatever it says about CS101 is a guess, and a wrong fee presented confidently is the most damaging failure in a system people rely on for money decisions.

Between the workflow and the agent, the deciding rows in the table are flexibility and multi-step handling. Students do not ask questions in the exact words a developer expected. Q2 shows a small rephrasing defeating the workflow, and the budget challenge question shows that a whole class of realistic questions, ones that need lookup, arithmetic, and comparison, cannot be answered without writing many new rules by hand. The agent handles both because it decides its own steps and reads the data through tools, so its answers stay grounded in the real fee table. The workflow's advantages, which are speed, zero cost, and deterministic behavior, are real, and for a fixed set of very common questions they would be enough. But for a scenario where questions vary in phrasing and complexity, the agent's ability to adapt outweighs its higher latency and cost. In a real deployment I would combine them: let the workflow answer exact, common queries cheaply and reliably, and hand everything else to the agent. Whatever the design, the agent's answers about money should be checked against tool outputs, since its reliability depends on the model behaving well.

## 6. Conclusion: when to choose each approach

A plain chatbot is the right choice when the task is about language and general knowledge rather than about specific, current, or private facts, and when a wrong or imperfect answer is cheap. Drafting an email, explaining a concept, brainstorming, summarizing text the user pastes in, or translating are good examples. The moment a correct answer depends on data the model was never trained on, or on something that changes over time, a chatbot alone becomes a liability, because it will answer fluently whether or not it knows.

A rule-based workflow is the right choice when the process is well understood, the inputs are structured and predictable, and the outcome must be consistent and auditable. Form validation, routing a support ticket by a dropdown category, calculating tax from fixed brackets, or sending a fee reminder when a due date passes are all cases where the steps can be written down once and must execute the same way every time. It is fast, cheap, and testable, and when it fails, it fails in a visible and diagnosable way. Its weakness is that it cannot cope with variation it was not built for, so it fits problems where variation is low or where a fallback to a human is acceptable.

An AI agent is the right choice when the task is open-ended, the input arrives in free-form language, and the path to the answer cannot be fully predicted in advance, so that the system must decide what to do next based on what it finds. Research that involves searching, reading, and following up, debugging code by running it and reading errors, or handling customer requests that need several lookups and a calculation are typical examples. The agent earns its extra cost and latency when the number and order of steps depends on intermediate results. It also needs guardrails: well-defined tools, a step limit, clear error messages, and human review when mistakes are costly. A useful rule of thumb is to use the simplest approach that solves the problem. If the steps can be written as rules, use a workflow. If the task is purely linguistic, use a chatbot. Reach for an agent when the problem needs both reasoning and access to tools, and when it is worth trading some predictability for flexibility.
