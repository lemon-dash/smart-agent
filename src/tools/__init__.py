"""
SmartAgent - 工具系统
定义工具基类、注册中心和内置工具
"""

from .base import BaseTool, ToolResult
from .registry import ToolRegistry

__all__ = ["BaseTool", "ToolResult", "ToolRegistry"]
