"""
SmartAgent - 网络搜索工具
演示如何封装外部 API 作为 Agent 工具
"""

from __future__ import annotations

from typing import Any

import httpx

from .base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """
    网络搜索工具

    实现说明：
    - 使用 DuckDuckGo Instant Answer API（免费，无需 API Key）
    - 生产环境中可替换为 SerpAPI、Tavily 等专业搜索 API
    - 演示了如何将外部 HTTP API 封装为 Agent 工具
    """

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "搜索互联网获取最新信息。适用于需要实时数据、新闻、事实核查等场景。"
            "输入搜索关键词，返回相关搜索结果摘要。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，例如 'Python 3.12 新特性'",
                },
            },
            "required": ["query"],
        }

    def execute(self, query: str, **kwargs: Any) -> ToolResult:
        """
        执行网络搜索

        Args:
            query: 搜索关键词

        Returns:
            搜索结果摘要
        """
        try:
            # 使用 DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            }

            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            # 提取摘要信息
            results = []

            # Abstract（主要摘要）
            if data.get("Abstract"):
                results.append(f"摘要: {data['Abstract']}")
                if data.get("AbstractSource"):
                    results.append(f"来源: {data['AbstractSource']}")

            # RelatedTopics（相关主题）
            if data.get("RelatedTopics"):
                for topic in data["RelatedTopics"][:5]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append(f"- {topic['Text']}")

            # Answer（直接回答）
            if data.get("Answer"):
                results.append(f"回答: {data['Answer']}")

            if not results:
                return ToolResult(
                    success=True,
                    data=f"未找到 '{query}' 的直接结果，建议尝试更具体的关键词。",
                )

            return ToolResult(
                success=True,
                data="\n".join(results),
            )

        except httpx.TimeoutException:
            return ToolResult(success=False, error="搜索请求超时，请稍后重试")
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"搜索请求失败: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"搜索出错: {str(e)}")
