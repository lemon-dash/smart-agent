"""
示例 1: 基础对话
演示最简单的 Agent 使用方式 —— 纯对话，不使用工具
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent
from config import AgentConfig


def main():
    print("=" * 60)
    print("  SmartAgent - 基础对话示例")
    print("=" * 60)
    print("\n输入 'quit' 退出\n")

    # 创建 Agent（不使用 ReAct 模式，纯对话）
    agent = Agent(
        config=AgentConfig(verbose=True),
        system_prompt="你是一个友好的 AI 助手。用简洁的中文回答问题。",
    )

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
