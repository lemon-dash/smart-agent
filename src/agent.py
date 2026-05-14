"""
SmartAgent - 核心 Agent 引擎
实现 ReAct（Reasoning + Acting）推理循环
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import AgentConfig
from src.llm import LLMClient, LLMResponse
from src.memory import MemoryManager
from src.prompts import DEFAULT_SYSTEM_PROMPT, REACT_SYSTEM_PROMPT
from src.tools.base import ToolResult
from src.tools.registry import ToolRegistry

console = Console()


@dataclass
class AgentStep:
    """Agent 推理步骤记录"""
    iteration: int
    thought: str | None = None
    tool_name: str | None = None
    tool_args: dict[str, Any] = field(default_factory=dict)
    tool_result: ToolResult | None = None
    response: str | None = None


class Agent:
    def __init__(
        self,
        config: AgentConfig | None = None,
        system_prompt: str | None = None,
        use_react: bool = False,
    ):
        self.config = config or AgentConfig()
        self.system_prompt = system_prompt or (
            REACT_SYSTEM_PROMPT if use_react else DEFAULT_SYSTEM_PROMPT
        )
        self.use_react = use_react

        # 初始化组件
        self.llm = LLMClient(self.config.llm)
        self.memory = MemoryManager(self.config.memory)
        self.tools = ToolRegistry()
        print(self.llm)
        # 推理历史（用于调试和展示）
        self._steps: list[AgentStep] = []
       

    def register_tool(self, tool: Any) -> None:
        """注册工具"""
        self.tools.register(tool)

    def chat(self, user_input: str) -> str:
        """
        与 Agent 对话（主入口）

        Args:
            user_input: 用户输入

        Returns:
            Agent 回复
        """
        # 记录用户消息
        self.memory.add_message("user", user_input)

        # 获取对话上下文
        messages = self.memory.get_context(self.system_prompt)

        # 获取工具定义
        tool_definitions = self.tools.to_openai_tools() if self.tools.count > 0 else None

        # ReAct 推理循环
        response = self._react_loop(messages, tool_definitions)

        # 记录助手回复
        self.memory.add_message("assistant", response)

        return response

    def _react_loop(
        self,
        messages: list[Any],
        tool_definitions: list[dict[str, Any]] | None,
    ) -> str:
        """
        ReAct 推理循环

        这是 Agent 的核心 —— 让 LLM 通过多轮工具调用来解决复杂问题

        流程：
        用户问题 → LLM 思考 → 调用工具 → 观察结果 → 继续思考 → ... → 最终回答
        """
        max_iterations = self.config.max_iterations

        for iteration in range(1, max_iterations + 1):
            step = AgentStep(iteration=iteration)

            if self.config.verbose:
                console.print(f"\n[bold cyan]--- 推理步骤 {iteration} ---[/bold cyan]")

            # 1. 调用 LLM
            llm_response: LLMResponse = self.llm.chat(
                messages=messages,
                tools=tool_definitions,
            )

            # 2. 检查是否有工具调用
            if not llm_response.has_tool_calls:
                # 没有工具调用 → LLM 给出了最终回答
                step.response = llm_response.content
                self._steps.append(step)

                if self.config.verbose:
                    console.print(Panel(
                        llm_response.content or "(无内容)",
                        title="[bold green]最终回答[/bold green]",
                        border_style="green",
                    ))

                return llm_response.content or ""

            # 3. 处理工具调用
            for tool_call in llm_response.tool_calls:
                step.tool_name = tool_call.name
                step.tool_args = tool_call.arguments

                if self.config.verbose:
                    console.print(f"[yellow]🔧 调用工具: {tool_call.name}[/yellow]")
                    console.print(f"[dim]   参数: {json.dumps(tool_call.arguments, ensure_ascii=False)}[/dim]")

                # 执行工具
                tool_result = self.tools.execute(
                    tool_call.name, **tool_call.arguments
                )
                step.tool_result = tool_result

                # 将工具调用和结果添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.arguments, ensure_ascii=False),
                        },
                    }],
                })
                messages.append(
                    self.llm.create_tool_message(
                        tool_call_id=tool_call.id,
                        content=tool_result.to_string(),
                    )
                )

                if self.config.verbose:
                    result_text = tool_result.to_string()
                    console.print(f"[blue]📋 结果: {result_text[:200]}{'...' if len(result_text) > 200 else ''}[/blue]")

            self._steps.append(step)

        # 达到最大迭代次数
        if self.config.verbose:
            console.print(f"[red]⚠️ 达到最大迭代次数 ({max_iterations})[/red]")

        return "抱歉，我在尝试解决这个问题时达到了最大推理步骤，无法给出完整回答。请尝试简化您的问题。"

    def get_steps(self) -> list[AgentStep]:
        """获取推理步骤历史"""
        return self._steps

    def clear_history(self) -> None:
        """清空对话历史"""
        self.memory.short_term.clear()
        self._steps.clear()

    def reset(self) -> None:
        """完全重置 Agent"""
        self.memory.clear()
        self._steps.clear()
