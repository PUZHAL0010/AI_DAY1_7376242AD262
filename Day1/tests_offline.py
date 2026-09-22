"""Offline sanity tests. No LLM or network needed.

The agent loop is tested with a scripted fake LLM so you can confirm the
loop logic works before connecting a real model.

Usage:
    python tests_offline.py
"""
from types import SimpleNamespace as NS

import agent
from tools import calculator, get_course_fee
from workflow import answer


def test_tools():
    assert "12000" in get_course_fee("cs101")
    assert "not found" in get_course_fee("ML404")
    assert calculator("12000 + 15000") == "27000"
    assert calculator("35,000 - 33000") == "2000"
    assert calculator("__import__('os').system('ls')").startswith("ERROR")


def test_workflow():
    assert "12000" in answer("What is the fee for CS101?")
    assert "27000" in answer("What is the total fee if I take CS101 and DS303 together?")
    assert "not found" in answer("What is the fee for ML404?")
    # Rephrased and multi-step questions should FAIL: that is the point
    assert "did not understand" in answer("What would I have to pay for AI202?")
    assert "did not understand" in answer("I have 35000 rupees. What can I afford?")


def _tool_call(call_id, name, args):
    return NS(id=call_id, function=NS(name=name, arguments=args))


class FakeClient:
    """Scripted LLM: look up two fees, add them, then answer."""

    def __init__(self):
        script = [
            NS(content="", tool_calls=[_tool_call("1", "get_course_fee", '{"course_code": "CS101"}')]),
            NS(content="", tool_calls=[_tool_call("2", "get_course_fee", '{"course_code": "DS303"}')]),
            NS(content="", tool_calls=[_tool_call("3", "calculator", '{"expression": "12000 + 15000"}')]),
            NS(content="The total is 27000 INR.", tool_calls=None),
        ]
        self._script = iter(script)
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        return NS(choices=[NS(message=next(self._script))])


def test_agent_loop():
    agent.get_client = lambda: FakeClient()
    result = agent.run_agent("total for CS101 and DS303?", verbose=False)
    assert result["finished"] is True
    assert result["tool_calls"] == 3
    assert result["steps"] == 4
    assert "27000" in result["answer"]


def test_agent_step_limit():
    class LoopForever:
        def __init__(self):
            self.chat = NS(completions=NS(create=self._create))

        def _create(self, **kwargs):
            msg = NS(content="", tool_calls=[_tool_call("x", "list_courses", "{}")])
            return NS(choices=[NS(message=msg)])

    agent.get_client = lambda: LoopForever()
    result = agent.run_agent("anything", verbose=False, max_steps=3)
    assert result["finished"] is False and result["steps"] == 3


if __name__ == "__main__":
    for test in (test_tools, test_workflow, test_agent_loop, test_agent_step_limit):
        test()
        print(f"PASS  {test.__name__}")
    print("\nAll offline tests passed.")
