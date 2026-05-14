"""
示例 4: ReAct 推理 Agent
演示 Agent 使用 ReAct（Reasoning + Acting）方法解决复杂问题
ReAct 是当前 Agent 系统最主流的推理框架
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import Agent
from src.tools.calculator import CalculatorTool
from src.tools.weather import WeatherTool
from src.tools.web_search import WebSearchTool
from config import AgentConfig


def main():
    print("=" * 60)
    print("  SmartAgent - ReAct 推理示例")
    print("=" * 60)
    print("""
ReAct（Reasoning + Acting）推理流程：
  Thought → Action → Observation → Thought → Action → ... → Answer

Agent 会自主决定使用哪些工具、以什么顺序来解决复杂问题。
""")

    # 创建 ReAct 模式的 Agent
    agent = Agent(
        config=AgentConfig(verbose=True, max_iterations=8),
        use_react=True,
        system_prompt="""你是一个使用 ReAct 方法解决问题的智能助手。

工作流程：
1. 思考用户的问题，分析需要什么信息
2. 选择合适的工具来获取信息
3. 分析工具返回的结果
4. 如果信息不够，继续使用工具
5. 当你有足够信息时，给出最终答案

你可以使用以下工具：
- calculator: 数学计算
- weather: 查询天气
- web_search: 搜索互联网

回答要准确、有条理。
""",
    )

    # 注册工具
    agent.register_tool(CalculatorTool())
    agent.register_tool(WeatherTool())
    agent.register_tool(WebSearchTool())

    print(f"已注册 {agent.tools.count} 个工具: {agent.tools.list_tools()}\n")

    # 复杂问题演示
    complex_questions = [
        "帮我算一下，如果我有 10000 元，年利率 3.5%，存 5 年后本息合计多少？",
        "北京和上海哪个城市更适合今天出行？帮我查一下天气对比一下。",
    ]

    for question in complex_questions:
        print("=" * 60)
        print(f"👤 问题: {question}")
        print("=" * 60)

        response = agent.chat(question)

        print(f"\n🤖 最终回答: {response}\n")

        # 打印推理步骤摘要
        steps = agent.get_steps()
        print(f"📊 推理过程: 共 {len(steps)} 步")
        for step in steps:
            if step.tool_name:
                print(f"   Step {step.iteration}: 调用 {step.tool_name}")
            elif step.response:
                print(f"   Step {step.iteration}: 生成回答")

        # 清空历史，准备下一个问题
        agent.clear_history()
        print()

    print("✅ ReAct 推理演示完成！")


if __name__ == "__main__":
    main()
