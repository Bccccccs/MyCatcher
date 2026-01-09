import argparse
from pathlib import Path

from src.llm_utils import get_client, only_code

PROMPT_TMPL = """You are a programming contest expert.

Task: Generate a *semantically equivalent* Python program variant of the given solution for the following problem.
- Keep input/output format identical.
- Keep the algorithm correct.
- You may refactor, rename variables, restructure control flow, or change implementation details.
- Output ONLY the full Python code.

[PROBLEM SPEC]
{spec}

[REFERENCE PROGRAM (PUT)]
{put_code}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path to spec.txt")
    ap.add_argument("--put", required=True, help="Path to put.py")
    ap.add_argument("--out", required=True, help="Output dir for variants")
    ap.add_argument("--k", type=int, default=3, help="Number of variants")
    args = ap.parse_args()

    spec = Path(args.spec).read_text(encoding="utf-8")
    put_code = Path(args.put).read_text(encoding="utf-8")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = get_client()
    model = ( __import__("os").getenv("MODEL_NAME") or "deepseek-chat" )

    for i in range(1, args.k + 1):
        prompt = PROMPT_TMPL.format(spec=spec, put_code=put_code)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        content = resp.choices[0].message.content or ""
        code = only_code(content)
        if not code:
            raise RuntimeError("LLM returned empty code.")

        path = out_dir / f"variant_{i:03d}.py"
        path.write_text(code, encoding="utf-8")
        print(f"[OK] wrote {path}")

if __name__ == "__main__":
    main()