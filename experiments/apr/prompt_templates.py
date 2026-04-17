from __future__ import annotations


def build_apr_prompt(*, spec: str, put_code: str, language_name: str) -> str:
    return f"""You are repairing a buggy {language_name} program.

Requirements:
- Return only the full repaired program source code.
- Do not add explanations.
- Preserve the original input/output protocol from the specification.

Problem specification:
{spec}

Buggy program:
```{language_name.lower()}
{put_code}
```
"""
