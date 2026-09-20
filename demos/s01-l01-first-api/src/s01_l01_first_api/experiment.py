from __future__ import annotations

import json
from datetime import datetime, timezone
from time import perf_counter

from .client import create_model_client
from .config import load_config
from .model import call_model
from .prompts import PROMPTS
from .runtime import LESSON_DIRECTORY, load_lesson_environment


def main() -> None:
    load_lesson_environment()
    config = load_config()
    client = create_model_client(config)
    results = []

    try:
        for name, prompt in PROMPTS.items():
            print(f"正在运行 {name}...")
            started_at = perf_counter()
            result = call_model(prompt, client=client, model=config.model)
            results.append(
                {
                    "name": name,
                    "provider": config.provider,
                    "prompt": prompt,
                    **result,
                    "latency_ms": round((perf_counter() - started_at) * 1000),
                }
            )
    finally:
        client.close()

    results_directory = LESSON_DIRECTORY / "results"
    results_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    output_path = results_directory / f"{timestamp.replace(':', '-')}.json"
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"实验完成：{output_path}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        raise SystemExit(f"实验失败：{error}") from error

