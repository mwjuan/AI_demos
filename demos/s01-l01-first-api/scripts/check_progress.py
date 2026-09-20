from pathlib import Path
import re


source_path = Path(__file__).parents[1] / "src" / "s01_l01_first_api" / "model.py"
source = source_path.read_text(encoding="utf-8")
pending = re.findall(r"TODO\s*\d*", source)

if pending or "练习尚未完成" in source:
    details = "\n".join(f"- {item}" for item in pending)
    raise SystemExit(
        f"第一课核心练习尚未完成：\n{details}\n"
        "请实现 src/s01_l01_first_api/model.py，然后再次运行检查和测试。"
    )

print("进度检查通过：没有遗留 TODO。接下来运行 pytest。")
