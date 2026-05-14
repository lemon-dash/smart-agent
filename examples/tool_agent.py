"""
示例 2: 工具调用 Agent
演示 Agent 如何使用工具来完成任务
注册了计算器、天气查询、文件读取等工具
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent
from src.tools.calculator import CalculatorTool
from src.tools.weather import WeatherTool
from src.tools.file_reader import FileReaderTool
from config import AgentConfig


def main():
    print("=" * 60)
    print("  SmartAgent - 工具调用示例")
    print("=" * 60)
    print("\n可用工具: 计算器、天气查询、文件读取")
    print("输入 'quit' 退出\n")

    # 创建 Agent
    agent = Agent(
        config=AgentConfig(verbose=True),
        system_prompt="""你是一个拥有多种工具的智能助手。

你可以：
- 使用计算器进行数学运算
- 查询城市天气
- 读取本地文件

根据用户的问题，选择合适的工具来获取信息，然后给出回答。
""",
    )

    # 注册工具
    agent.register_tool(CalculatorTool())
    agent.register_tool(WeatherTool())
    agent.register_tool(FileReaderTool())

    print(f"已注册 {agent.tools.count} 个工具: {agent.tools.list_tools()}\n")

    # 演示问题
    demo_questions = [
        "帮我算一下 (25 + 75) * 3 - 100 等于多少",
        "北京今天天气怎么样？",
        "帮我读取 README.md 文件的前 10 行",
    ]

    print("📝 运行演示问题...\n")

    for question in demo_questions:
        print(f"👤 你: {question}")
        response = agent.chat(question)
        print(f"🤖 助手: {response}")
        print("-" * 60)

    # 交互模式
    print("\n进入交互模式，输入 'quit' 退出\n")
    while True:
        try:
            user_input = input("👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        response = agent.chat(user_input)
        print(f"\n🤖 助手: {response}\n")


if __name__ == "__main__":
    main()
