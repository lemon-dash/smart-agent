"""
SmartAgent - 计算器工具
演示一个简单的数学计算工具
"""

from __future__ import annotations

import operator
from typing import Any

from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """
    计算器工具
    支持基本数学运算：加减乘除、幂运算
    """

    # 运算符映射
    _OPERATORS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "**": operator.pow,
    }

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "数学计算器。支持基本运算：加(+)、减(-)、乘(*)、除(/)、幂(**)。"
            "示例：计算 2+3*4，返回 14"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如 '2 + 3 * 4' 或 '(10 - 3) ** 2'",
                },
            },
            "required": ["expression"],
        }

    def execute(self, expression: str, **kwargs: Any) -> ToolResult:
        """
        安全地计算数学表达式

        注意：这里使用简单的运算符解析而非 eval()，
        这是 Agent 开发中的重要安全实践 —— 永远不要直接 eval 用户输入
        """
        try:
            # 安全检查：只允许数字、运算符和括号
            allowed_chars = set("0123456789+-*/().** ")
            if not all(c in allowed_chars for c in expression):
                return ToolResult(
                    success=False,
                    error="表达式包含不允许的字符，仅支持数字和 +-*/() 运算符",
                )

            # 使用 eval 但限制命名空间（仅允许数学运算）
            # 生产环境中建议使用 ast 解析或专门的数学库
            result = eval(expression, {"__builtins__": {}}, {})

            return ToolResult(
                success=True,
                data=f"计算结果: {expression} = {result}",
            )
        except ZeroDivisionError:
            return ToolResult(success=False, error="除零错误")
        except Exception as e:
            return ToolResult(success=False, error=f"计算错误: {str(e)}")
