"""
示例 3: RAG 记忆 Agent
演示 Agent 如何使用长期记忆（向量数据库）来记住和检索信息
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent
from src.tools.calculator import CalculatorTool
from config import AgentConfig


def main():
    print("=" * 60)
    print("  SmartAgent - RAG 记忆示例")
    print("=" * 60)
    print("\n演示 Agent 的长期记忆能力\n")

    # 创建 Agent
    agent = Agent(
        config=AgentConfig(verbose=True),
        system_prompt="""你是一个拥有长期记忆的智能助手。

你可以记住用户告诉你的重要信息，并在后续对话中利用这些记忆。
当用户让你记住什么时，你会调用 remember 工具存储信息。
当用户问问题时，你会调用 recall 工具检索相关记忆。
""",
    )
    # 注册基础工具
    agent.register_tool(CalculatorTool())

    # ===== 演示 1: 存储记忆 =====
    print("演示 1: 存储信息到长期记忆\n")

    memories_to_store = [
        ("记住：我的名字叫小明", {"type": "personal_info"}),
        ("记住：我喜欢 Python 编程和机器学习", {"type": "preference"}),
        ("记住：我的生日是 5 月 15 日", {"type": "personal_info"}),
    ]

    for text, meta in memories_to_store:
        print(f"存储: {text}")
        success = agent.memory.remember(text, metadata=meta)
        print(f"   {'成功' if success else '失败'}")

    # ===== 演示 2: 检索记忆 =====
    print("\n\n演示 2: 从长期记忆检索信息\n")

    queries = [
        "用户叫什么名字？",
        "用户喜欢什么？",
        "用户的生日是什么时候？",
    ]

    for query in queries:
        print(f"查询: {query}")
        results = agent.memory.recall(query, top_k=2)
        if results:
            for r in results:
                print(f"   {r['content']} (相似度: {1 - r['distance']:.2f})")
        else:
            print("   未找到相关记忆")
        print()

    # ===== 演示 3: 对话中使用记忆 =====
    print("\n演示 3: 在对话中利用记忆\n")

    questions = [
        "你还记得我的名字吗？",
        "根据你对我的了解，推荐一个适合我的编程项目",
    ]

    for question in questions:
        print(f" 你: {question}")

        # 先检索相关记忆
        memories = agent.memory.recall(question, top_k=2)
        if memories:
            memory_context = "\n".join(
                f"- {m['content']}" for m in memories
            )
            enhanced_question = f"{question}\n\n[相关记忆]\n{memory_context}"
        else:
            enhanced_question = question

        response = agent.chat(enhanced_question)
        # print(f"助手: {response}")
        print("-" * 60)

    print("\n RAG 记忆演示完成！")


if __name__ == "__main__":
    main()
