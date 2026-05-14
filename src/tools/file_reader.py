"""
SmartAgent - 文件读取工具
演示如何让 Agent 读取本地文件
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class FileReaderTool(BaseTool):
    """
    文件读取工具

    安全设计：
    - 限制可读取的目录（防止路径遍历攻击）
    - 限制文件大小（防止内存溢出）
    - 支持指定行数范围
    """

    # 安全限制
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    ALLOWED_EXTENSIONS = {
        ".txt", ".md", ".py", ".js", ".ts", ".json",
        ".yaml", ".yml", ".csv", ".html", ".css",
        ".xml", ".log", ".env", ".toml", ".cfg",
    }

    def __init__(self, allowed_dirs: list[str] | None = None):
        """
        Args:
            allowed_dirs: 允许读取的目录列表，默认为当前目录
        """
        self._allowed_dirs = [
            Path(d).resolve() for d in (allowed_dirs or ["."])
        ]

    @property
    def name(self) -> str:
        return "file_reader"

    @property
    def description(self) -> str:
        return (
            "读取本地文件内容。支持文本文件（.txt, .md, .py, .json, .csv 等）。"
            "可以指定起始行和结束行来读取文件的部分内容。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径，例如 './README.md' 或 'src/agent.py'",
                },
                "start_line": {
                    "type": "integer",
                    "description": "起始行号（从 1 开始），默认为 1",
                    "default": 1,
                },
                "end_line": {
                    "type": "integer",
                    "description": "结束行号，默认读取到文件末尾",
                },
            },
            "required": ["file_path"],
        }

    def _validate_path(self, file_path: str) -> Path:
        """验证文件路径安全性"""
        path = Path(file_path).resolve()

        # 检查扩展名
        if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"不支持的文件类型: {path.suffix}，"
                f"允许的类型: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )

        # 检查是否在允许的目录内（防止路径遍历）
        is_allowed = any(
            str(path).startswith(str(allowed_dir))
            for allowed_dir in self._allowed_dirs
        )
        if not is_allowed:
            raise ValueError(f"文件路径不在允许的目录范围内")

        return path

    def execute(
        self,
        file_path: str,
        start_line: int = 1,
        end_line: int | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """读取文件内容"""
        try:
            path = self._validate_path(file_path)

            if not path.exists():
                return ToolResult(success=False, error=f"文件不存在: {file_path}")

            # 检查文件大小
            file_size = path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                return ToolResult(
                    success=False,
                    error=f"文件过大（{file_size} bytes），最大支持 {self.MAX_FILE_SIZE} bytes",
                )

            # 读取文件
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()

            # 应用行数范围
            start = max(0, start_line - 1)
            end = end_line if end_line else len(lines)
            selected_lines = lines[start:end]

            # 添加行号
            numbered_lines = [
                f"{i + start_line:4d} | {line}"
                for i, line in enumerate(selected_lines)
            ]

            result = "\n".join(numbered_lines)
            total_lines = len(lines)
            shown_lines = len(selected_lines)

            header = f"文件: {path.name} ({shown_lines}/{total_lines} 行)\n{'=' * 50}\n"

            return ToolResult(success=True, data=header + result)

        except ValueError as e:
            return ToolResult(success=False, error=str(e))
        except UnicodeDecodeError:
            return ToolResult(success=False, error="文件编码不支持，仅支持 UTF-8 文本文件")
        except Exception as e:
            return ToolResult(success=False, error=f"读取文件失败: {str(e)}")
