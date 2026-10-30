"""Interactive streaming test for dim mode against a local chat API."""

import argparse
import os
import sys

from openai import OpenAI

from markrender import MarkdownRenderer

DEFAULT_BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8642/v1")
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "deepseek-v4.1-flash-free")


def stream_reply(client, model, messages, dim_mode):
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

    renderer = MarkdownRenderer()
    parts = []

    for chunk in stream:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if not content:
            continue
        parts.append(content)
        renderer.render(content, dim_mode=dim_mode)

    renderer.finalize()
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--normal",
        action="store_true",
        help="Start with dim mode disabled",
    )
    args = parser.parse_args()

    client = OpenAI(
        base_url=args.base_url,
        api_key=os.environ.get("OPENAI_API_KEY", "local"),
    )
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Format answers in Markdown.",
        }
    ]
    dim_mode = not args.normal

    print(f"model: {args.model}")
    print(f"dim mode: {'on' if dim_mode else 'off'}")
    print("Type a prompt, /dim to toggle, /clear to reset, or exit to stop.\n")

    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break
        if prompt == "/clear":
            messages = messages[:1]
            print("history cleared\n")
            continue
        if prompt == "/dim":
            dim_mode = not dim_mode
            print(f"dim mode: {'on' if dim_mode else 'off'}\n")
            continue

        messages.append({"role": "user", "content": prompt})
        print("ai> ", end="", flush=True)

        try:
            reply = stream_reply(client, args.model, messages, dim_mode)
        except Exception as exc:
            print(f"\nrequest failed: {exc}\n", file=sys.stderr)
            messages.pop()
            continue

        if reply:
            messages.append({"role": "assistant", "content": reply})
        print("\n")


if __name__ == "__main__":
    main()
