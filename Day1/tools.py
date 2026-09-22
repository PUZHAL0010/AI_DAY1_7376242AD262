"""Tools available to the AI agent: fee lookup, course listing, calculator."""
import ast
import json
import operator

from config import COURSE_DB


# --------------------------------------------------------------------------
# Tool implementations
# --------------------------------------------------------------------------
def get_course_fee(course_code: str) -> str:
    """Look up the fee for one course code in the private database."""
    code = course_code.strip().upper()
    course = COURSE_DB.get(code)
    if course is None:
        known = ", ".join(COURSE_DB)
        return f"ERROR: course '{code}' not found. Known courses: {known}"
    return f"{code} ({course['title']}): fee = {course['fee']} INR"


def list_courses() -> str:
    """List every course with its code and fee."""
    lines = [f"{code} ({c['title']}): {c['fee']} INR" for code, c in COURSE_DB.items()]
    return "\n".join(lines)


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand)
    raise ValueError("only numbers and + - * / // % are allowed")


def calculator(expression: str) -> str:
    """Safely evaluate an arithmetic expression (no eval())."""
    try:
        cleaned = expression.replace(",", "").strip()
        result = _eval(ast.parse(cleaned, mode="eval").body)
        return str(result)
    except ZeroDivisionError:
        return "ERROR: division by zero"
    except Exception as exc:  # bad syntax, disallowed operation, etc.
        return f"ERROR: could not evaluate '{expression}' ({exc})"


# --------------------------------------------------------------------------
# Registry + schemas (OpenAI-compatible function-calling format)
# --------------------------------------------------------------------------
TOOL_REGISTRY = {
    "get_course_fee": get_course_fee,
    "list_courses": list_courses,
    "calculator": calculator,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_course_fee",
            "description": "Get the fee (in INR) of one college course from the private fee database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_code": {"type": "string", "description": "Course code such as CS101"}
                },
                "required": ["course_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_courses",
            "description": "List every course in the database with its code, title and fee.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate an arithmetic expression, e.g. '12000 + 15000'. Use for ALL arithmetic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Arithmetic expression"}
                },
                "required": ["expression"],
            },
        },
    },
]


def run_tool(name: str, arguments_json: str) -> str:
    """Execute a tool by name with JSON-encoded arguments; never raises."""
    func = TOOL_REGISTRY.get(name)
    if func is None:
        return f"ERROR: unknown tool '{name}'"
    try:
        args = json.loads(arguments_json or "{}")
        return func(**args)
    except Exception as exc:
        return f"ERROR: tool '{name}' failed ({exc})"
