"""
SmartAgent - 工具注册中心
管理所有可用工具，支持注册、查找、获取 OpenAI 格式定义
"""

from __future__ import annotations

from typing import Any

from .base import BaseTool


class ToolRegistry:
    """
    工具注册中心

    设计模式：注册表模式（Registry Pattern）
    - 集中管理所有工具实例
    - 提供按名称查找的能力
    - 自动生成 OpenAI function calling 格式的工具列表
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        注册工具

        Args:
            tool: 工具实例

        Raises:
            ValueError: 工具名称已存在时抛出
        """
        if tool.name in self._tools:
            raise ValueError(f"工具 '{tool.name}' 已注册，请勿重复注册")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """取消注册工具"""
        self._tools.pop(name, None)

    def get(self, name: str) -> BaseTool | None:
        """根据名称获取工具"""
        return self._tools.get(name)

    def execute(self, name: str, **kwargs: Any):
        """
        执行指定工具

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            ToolResult 执行结果
        """
        tool = self.get(name)
        if tool is None:
            from .base import ToolResult
            return ToolResult(success=False, error=f"工具 '{name}' 不存在")
        return tool.execute(**kwargs)

    def list_tools(self) -> list[str]:
        """列出所有已注册工具名称"""
        return list(self._tools.keys())

    def to_openai_tools(self) -> list[dict[str, Any]]:
        """
        获取所有工具的 OpenAI function calling 格式
        Agent 将此列表传给 LLM，让 LLM 知道可以使用哪些工具
        """
        return [tool.to_openai_tool() for tool in self._tools.values()]

    @property
    def count(self) -> int:
        """已注册工具数量"""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:
        tools = ", ".join(self._tools.keys())
        return f"<ToolRegistry: [{tools}]>"
