from __future__ import annotations


def build_chat_prompt(*, spec: str, put_code: str, num_candidates: int) -> str:
    return f"""You are generating bug-revealing test inputs for a program under test.

Task:
- Read the problem specification and the candidate implementation.
- Produce exactly {num_candidates} candidate test inputs.
- Each candidate must be a complete stdin instance.
- Do not explain anything.
- Separate cases using a line that contains exactly <<<CASE>>>.

Problem specification:
{spec}

Program under test:
```code
{put_code}
```

Output format:
case1
<<<CASE>>>
case2
<<<CASE>>>
...
"""
