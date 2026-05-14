"""
SmartAgent - 记忆管理系统
实现短期记忆（对话历史）和长期记忆（向量存储）
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from config import MemoryConfig


@dataclass
class Message:
    """对话消息"""
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_openai(self) -> ChatCompletionMessageParam:
        """转换为 OpenAI 消息格式"""
        msg: ChatCompletionMessageParam = {
            "role": self.role,  # type: ignore
            "content": self.content,
        }
        return msg


class ShortTermMemory:
    """
    短期记忆 - 对话历史管理

    设计要点：
    - 维护最近的对话上下文
    - 自动裁剪过长的历史（防止超出 token 限制）
    - 保留系统消息（始终在最前面）
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._messages: list[Message] = []

    def add(self, role: str, content: str, **metadata: Any) -> None:
        """添加消息"""
        self._messages.append(Message(role=role, content=content, metadata=metadata))
        self._trim()

    def _trim(self) -> None:
        """裁剪消息历史，保留系统消息"""
        system_msgs = [m for m in self._messages if m.role == "system"]
        non_system = [m for m in self._messages if m.role != "system"]

        # 保留最近的非系统消息
        max_non_system = self.max_messages - len(system_msgs)
        if len(non_system) > max_non_system:
            non_system = non_system[-max_non_system:]

        self._messages = system_msgs + non_system

    def get_messages(self) -> list[ChatCompletionMessageParam]:
        """获取所有消息（OpenAI 格式）"""
        return [m.to_openai() for m in self._messages]

    def clear(self) -> None:
        """清空记忆"""
        self._messages.clear()

    @property
    def message_count(self) -> int:
        return len(self._messages)

    def get_recent(self, n: int = 5) -> list[Message]:
        """获取最近 n 条消息"""
        return self._messages[-n:]


class LongTermMemory:
    """
    长期记忆 - 基于向量数据库的 RAG 记忆

    核心概念：
    - 将重要信息存储为向量嵌入
    - 查询时通过语义相似度检索相关记忆
    - 实现 RAG（Retrieval-Augmented Generation）

    技术选型：
    - ChromaDB：轻量级向量数据库，适合本地开发
    - OpenAI Embeddings：高质量的文本向量化
    """

    def __init__(self, config: MemoryConfig | None = None):
        self.config = config or MemoryConfig()
        from config import LLMConfig
        self.memconfig = LLMConfig()
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.config.chroma_persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.config.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._embedding_client = OpenAI(api_key=self.memconfig.api_key,base_url=self.memconfig.base_url)
        
            self._available = True
        except ImportError:
            print("⚠️  ChromaDB 未安装，长期记忆功能不可用。运行: pip install chromadb")
            self._available = False
        except Exception as e:
            print(f"⚠️  长期记忆初始化失败: {e}")
            self._available = False

    def _get_embedding(self, text: str) -> list[float]:
        """获取文本的向量嵌入"""
        response = self._embedding_client.embeddings.create(
            model=self.config.embedding_model,
            input=text,
        )
        return response.data[0].embedding

    def store(self, content: str, metadata: dict[str, Any] | None = None) -> bool:
        """
        存储记忆

        Args:
            content: 记忆内容
            metadata: 附加元数据（如来源、时间等）

        Returns:
            是否存储成功
        """
        if not self._available:
            return False

        try:
            import uuid
            embedding = self._get_embedding(content)
            self._collection.add(
                ids=[str(uuid.uuid4())],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}],
            )
            return True
        except Exception as e:
            print(f"存储记忆失败: {e}")
            return False

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        检索相关记忆

        Args:
            query: 查询文本
            top_k: 返回最相关的 k 条记忆

        Returns:
            相关记忆列表，按相似度排序
        """
        if not self._available:
            return []

        try:
            query_embedding = self._get_embedding(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count()),
            )

            memories = []
            if results and results["documents"]:
                for doc, metadata, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ):
                    memories.append({
                        "content": doc,
                        "metadata": metadata,
                        "distance": distance,
                    })

            return memories
        except Exception as e:
            print(f"检索记忆失败: {e}")
            return []

    def clear(self) -> None:
        """清空所有记忆"""
        if self._available:
            try:
                self._client.delete_collection(self.config.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.config.collection_name,
                )
            except Exception:
                pass


class MemoryManager:
    """
    记忆管理器 - 统一管理短期和长期记忆

    使用策略：
    - 每次对话使用短期记忆维护上下文
    - 重要信息自动存入长期记忆
    - 查询时从长期记忆检索相关上下文补充
    """

    def __init__(self, config: MemoryConfig | None = None):
        self.config = config or MemoryConfig()
        self.short_term = ShortTermMemory(
            max_messages=self.config.max_short_term_messages
        )
        self.long_term = LongTermMemory(self.config)

    def add_message(self, role: str, content: str) -> None:
        """添加消息到短期记忆"""
        self.short_term.add(role, content)

    def remember(self, content: str, metadata: dict[str, Any] | None = None) -> bool:
        """存储重要信息到长期记忆"""
        return self.long_term.store(content, metadata)

    def recall(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """从长期记忆检索相关信息"""
        return self.long_term.retrieve(query, top_k)

    def get_context(self, system_prompt: str) -> list[ChatCompletionMessageParam]:
        """
        获取完整对话上下文（含系统提示）
        """
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(self.short_term.get_messages())
        return messages

    def clear(self) -> None:
        """清空所有记忆"""
        self.short_term.clear()
        self.long_term.clear()
