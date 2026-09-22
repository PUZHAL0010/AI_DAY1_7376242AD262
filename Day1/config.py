"""Shared configuration, private data, and helpers used by all three systems.

The LLM connection uses any OpenAI-compatible endpoint, so it works with
Ollama (local, open-source), Groq, OpenRouter, LM Studio, vLLM, etc.
Settings come from environment variables or a .env file (see .env.example).
"""
import os
import time

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

# --------------------------------------------------------------------------
# LLM connection
# --------------------------------------------------------------------------
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")  # Ollama ignores the key
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")


def get_client():
    """Return an OpenAI-compatible client pointed at the configured LLM."""
    from openai import OpenAI

    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


# --------------------------------------------------------------------------
# PRIVATE DATA: college course fees (no public LLM has ever seen this)
# --------------------------------------------------------------------------
COURSE_DB = {
    "CS101": {"title": "Introduction to Programming", "fee": 12000},
    "AI202": {"title": "Applied Machine Learning", "fee": 18000},
    "DS303": {"title": "Data Science Foundations", "fee": 15000},
}

# --------------------------------------------------------------------------
# The four test questions used for the observation table.
# "expected" is the correct numeric answer, or None if the right behaviour
# is to say the course does not exist.
# --------------------------------------------------------------------------
QUESTIONS = [
    {"id": "Q1", "text": "What is the fee for CS101?",
     "kind": "direct lookup", "expected": 12000},
    {"id": "Q2", "text": "What would I have to pay for AI202?",
     "kind": "rephrased lookup", "expected": 18000},
    {"id": "Q3", "text": "What is the total fee if I take CS101 and DS303 together?",
     "kind": "lookup + arithmetic", "expected": 27000},
    {"id": "Q4", "text": "What is the fee for ML404?",
     "kind": "course that does not exist", "expected": None},
]

# Harder question used by challenge.py
CHALLENGE_QUESTION = (
    "I have 35000 rupees to spend. Which two of the courses could I afford "
    "together, and how much money would I have left over?"
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def timed(fn, *args, **kwargs):
    """Run fn and return (result, elapsed_seconds)."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start


def cli_questions(argv):
    """Questions from the command line, or the four standard ones."""
    if len(argv) > 1:
        return [" ".join(argv[1:])]
    return [q["text"] for q in QUESTIONS]


def looks_correct(question, answer):
    """Rough automatic check used only to pre-fill the observation table.

    Always confirm by reading the answer yourself.
    """
    text = answer.lower().replace(",", "").replace("\u20b9", "")
    if question["expected"] is None:
        cues = ("not found", "no such", "does not exist", "doesn't exist",
                "not exist", "no record", "unknown course", "not a valid",
                "not in the")
        return any(cue in text for cue in cues)
    return str(question["expected"]) in text
