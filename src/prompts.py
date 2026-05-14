"""
SmartAgent - Prompt 模板管理
集中管理所有系统提示词和模板
"""

from __future__ import annotations

from typing import Any


# ============================================================
# 核心 Agent 系统提示词
# ============================================================

DEFAULT_SYSTEM_PROMPT = """你是一个智能助手，能够使用工具来帮助用户完成任务。

你的工作方式：
1. 仔细分析用户的问题
2. 判断是否需要使用工具来获取信息
3. 如果需要，选择合适的工具并执行
4. 基于工具返回的结果，给出准确的回答

注意事项：
- 如果不需要工具就能回答，直接回答即可
- 使用工具时要提供准确的参数
- 如果工具执行失败，尝试其他方法或告知用户
- 回答要简洁、准确、有帮助
"""

REACT_SYSTEM_PROMPT = """你是一个使用 ReAct（Reasoning + Acting）方法解决问题的智能助手。

你的工作流程：
1. **思考（Thought）**：分析当前情况，决定下一步行动
2. **行动（Action）**：选择并执行一个工具
3. **观察（Observation）**：分析工具返回的结果
4. 重复以上步骤，直到得出最终答案

规则：
- 每次只执行一个工具
- 仔细分析工具返回的结果
- 如果结果不够，继续使用工具获取更多信息
- 当你有足够信息时，给出最终答案
- 始终用中文回答
"""

RAG_SYSTEM_PROMPT = """你是一个拥有长期记忆的智能助手。

你的特点：
- 你可以记住用户告诉你的重要信息
- 在回答问题时，你会参考之前学到的知识
- 你能从记忆中检索相关信息来辅助回答

记忆策略：
- 当用户说"记住..."时，将信息存入长期记忆
- 当用户提问时，先检索相关记忆
- 结合记忆和你的知识来回答问题
"""


# ============================================================
# Prompt 构建器
# ============================================================

class PromptBuilder:
    """
    Prompt 构建器
    使用模板方法构建结构化的系统提示词
    """

    @staticmethod
    def build_agent_prompt(
        name: str = "SmartAgent",
        capabilities: list[str] | None = None,
        constraints: list[str] | None = None,
        base_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> str:
        """
        构建完整的 Agent 系统提示词

        Args:
            name: Agent 名称
            capabilities: Agent 能力列表
            constraints: 约束条件列表
            base_prompt: 基础提示词模板

        Returns:
            完整的系统提示词
        """
        sections = [f"你是 {name}。", ""]

        if capabilities:
            sections.append("你的能力：")
            for cap in capabilities:
                sections.append(f"- {cap}")
            sections.append("")

        if constraints:
            sections.append("约束条件：")
            for constraint in constraints:
                sections.append(f"- {constraint}")
            sections.append("")

        sections.append(base_prompt)

        return "\n".join(sections)

    @staticmethod
    def build_tool_aware_prompt(tools: list[str]) -> str:
        """
        构建包含工具信息的提示词

        Args:
            tools: 可用工具名称列表

        Returns:
            包含工具信息的提示词
        """
        tool_list = "\n".join(f"- {tool}" for tool in tools)
        return f"""你是一个智能助手，可以使用以下工具来帮助用户：

可用工具：
{tool_list}

使用规则：
1. 只有在需要时才使用工具
2. 仔细阅读工具描述，确保参数正确
3. 一次只使用一个工具
4. 根据工具结果给出准确回答
"""
