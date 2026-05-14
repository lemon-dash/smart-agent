"""
SmartAgent - LLM 客户端封装
统一封装 OpenAI API 调用，支持流式输出和工具调用
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from openai import OpenAI, Stream
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
)

from config import LLMConfig


@dataclass
class ToolCall:
    """工具调用请求"""
    id: str
    name: str
    arguments: dict[str, Any]

    @classmethod
    def from_openai(cls, tc: Any) -> "ToolCall":
        """从 OpenAI 格式转换"""
        return cls(
            id=tc.id,
            name=tc.function.name,
            arguments=json.loads(tc.function.arguments),
        )


@dataclass
class LLMResponse:
    """LLM 响应封装"""
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMClient:
    """
    LLM 客户端
    封装 OpenAI API，提供统一的调用接口
    """

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()
        self._client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

    def chat(
        self,
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息历史
            tools: 可用工具定义（OpenAI function calling 格式）
            temperature: 采样温度
            max_tokens: 最大生成 token 数

        Returns:
            LLMResponse 封装响应
        """
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        completion: ChatCompletion = self._client.chat.completions.create(**kwargs)
        choice = completion.choices[0]
        message = choice.message

        # 解析工具调用
        tool_calls = []
        if message.tool_calls:
            tool_calls = [ToolCall.from_openai(tc) for tc in message.tool_calls]

        # 解析用量
        usage = {}
        if completion.usage:
            usage = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage=usage,
        )

    def chat_stream(
        self,
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[str]:
        """
        流式聊天（占位，可扩展）
        """
        raise NotImplementedError("流式输出将在后续版本实现")

    def create_tool_message(
        self, tool_call_id: str, content: str
    ) -> ChatCompletionToolMessageParam:
        """创建工具结果消息"""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        }
