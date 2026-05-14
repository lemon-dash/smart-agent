"""
SmartAgent - 配置管理模块
集中管理所有配置项，支持环境变量覆盖
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMConfig:
    """LLM 相关配置"""
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", "YOUR_API_KEY"))
    base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    model: str = field(default_factory=lambda: os.getenv("SMART_AGENT_MODEL", "gpt-3.5-turbo"))
    temperature: float = field(default_factory=lambda: float(os.getenv("SMART_AGENT_TEMPERATURE", "0.7")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("SMART_AGENT_MAX_TOKENS", "2048")))


@dataclass
class MemoryConfig:
    """记忆系统配置"""
    chroma_persist_dir: str = field(default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"))
    collection_name: str = "smart_agent_memory"
    embedding_model: str = "embedding-3"
    max_short_term_messages: int = 20  # 短期记忆最大消息数


@dataclass
class AgentConfig:
    """Agent 全局配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    max_iterations: int = 10  # ReAct 最大迭代次数
    verbose: bool = True  # 是否打印推理过程


# 全局配置单例
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """获取全局配置"""
    global _config
    if _config is None:
        _config = AgentConfig()
    return _config


def set_config(config: AgentConfig) -> None:
    """设置全局配置"""
    global _config
    _config = config
