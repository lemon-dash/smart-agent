# SmartAgent - 模块化 AI Agent 框架

> 一个轻量级、可扩展的 AI Agent 框架，符合现代 Agent 开发的核心设计模式。

## 项目亮点

- **工具调用系统**：基于 OpenAI Function Calling 的可扩展工具框架
- **记忆管理**：短期对话记忆 + 长期向量记忆（RAG）
- **多步推理**：支持 ReAct（Reasoning + Acting）推理链
- **模块化设计**：工具、记忆、LLM 解耦，可独立替换
- **类型安全**：完整的 Python 类型注解
- **生产就绪**：错误处理、日志、配置管理

## 技术栈

| 组件 | 技术 |
|------|------|
| 核心语言 | Python 3.10+ |
| LLM 接口 | OpenAI API / 兼容接口 |
| 向量存储 | ChromaDB |
| 向量嵌入 | OpenAI Embeddings |
| Web 框架 | FastAPI |
| 测试 | pytest |

## 项目结构


## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
export OPENAI_API_KEY="your-api-key"
# 或使用兼容接口
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### 3. 运行示例

```bash
# 基础对话
python examples/basic_chat.py

# 工具调用 Agent
python examples/tool_agent.py

# RAG 记忆 Agent
python examples/rag_agent.py

# ReAct 推理 Agent
python examples/react_agent.py
```

## 架构设计

```
┌─────────────────────────────────────────────┐
│                  SmartAgent                  │
│                                              │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  │
│  │   LLM   │  │  Memory  │  │   Tools    │  │
│  │ Client  │  │ Manager  │  │  Registry  │  │
│  └────┬────┘  └────┬─────┘  └─────┬──────┘  │
│       │            │              │          │
│       └────────────┼──────────────┘          │
│                    │                         │
│            ┌───────┴───────┐                 │
│            │  Agent Engine │                 │
│            │  (ReAct Loop) │                 │
│            └───────────────┘                 │
└─────────────────────────────────────────────┘
```

## 核心概念

### Agent 工作循环（ReAct）

```
用户输入 → 思考(Reason) → 选择工具(Act) → 观察结果(Observe) → 判断是否完成 → 输出
                ↑                                                    │
                └────────────────────────────────────────────────────┘
                              (循环直到得出最终答案)
```

### 工具调用流程

```
1. 用户提问 → LLM 分析意图
2. LLM 决定调用哪个工具 + 参数
3. Agent 执行工具，获取结果
4. 结果反馈给 LLM 继续推理
5. LLM 生成最终回答
```

## License

MIT
