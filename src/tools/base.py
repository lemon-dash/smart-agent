"""
SmartAgent - 工具基类
所有自定义工具都需要继承 BaseTool 并实现 execute 方法
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: str | None = None

    def to_string(self) -> str:
        """转换为字符串，用于反馈给 LLM"""
        if self.success:
            if isinstance(self.data, str):
                return self.data
            return str(self.data)
        return f"工具执行失败: {self.error}"


class BaseTool(ABC):
    """
    工具抽象基类

    设计模式：模板方法模式
    - name/description 定义工具元信息（供 LLM 理解工具用途）
    - parameters 定义工具参数 schema（JSON Schema 格式）
    - execute 实现具体逻辑
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称（唯一标识符）"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述（LLM 用此判断何时使用该工具）"""
        ...

    @property
    def parameters(self) -> dict[str, Any]:
        """
        工具参数定义（JSON Schema 格式）
        子类可覆盖此方法定义参数
        """
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """
        执行工具逻辑

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult 执行结果
        """
        ...

    def to_openai_tool(self) -> dict[str, Any]:
        """
        转换为 OpenAI Function Calling 格式
        这是 Agent 框架与 LLM 之间的桥梁
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
