from types import MappingProxyType


PROMPTS = MappingProxyType(
    {
        "direct": "解释 Python 闭包。",
        "audience": (
            "向一位熟悉 Python、但刚开始学习 AI 的开发者解释 Python 闭包。"
            "使用清晰、简短的中文。"
        ),
        "example": (
            "向一位熟悉 Python、但刚开始学习 AI 的开发者解释 Python 闭包。"
            "使用清晰、简短的中文，并给出一个能直接运行的最小例子，"
            "说明闭包保留了什么状态。"
        ),
        "concise": "用不超过 100 个汉字解释 Python 闭包。",
    }
)


def get_prompt(name: str) -> str:
    try:
        return PROMPTS[name]
    except KeyError as error:
        choices = ", ".join(PROMPTS)
        raise ValueError(f"未知提示词版本“{name}”。可选值：{choices}") from error

