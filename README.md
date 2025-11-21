![这是图片](./images/title.png)

<div align="center">

**让 Claude Code 与 Gemini CLI 无缝协作**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io) [![Share](https://img.shields.io/badge/share-000000?logo=x&logoColor=white)](https://x.com/intent/tweet?text=GeminiMCP：让%20Claude%20Code%20与%20Gemini%20无缝协作%20https://github.com/GuDaStudio/geminimcp%20%23AI%20%23Coding%20%23MCP) [![Share](https://img.shields.io/badge/share-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/GuDaStudio/geminimcp) [![Share](https://img.shields.io/badge/share-FF4500?logo=reddit&logoColor=white)](https://www.reddit.com/submit?title=GeminiMCP：让%20Claude%20Code%20与%20Gemini%20无缝协作&url=https://github.com/GuDaStudio/geminimcp) [![Share](https://img.shields.io/badge/share-0088CC?logo=telegram&logoColor=white)](https://t.me/share/url?url=https://github.com/GuDaStudio/geminimcp&text=GeminiMCP：让%20Claude%20Code%20与%20Gemini%20无缝协作)

⭐ 在GitHub上给我们点星~您的支持对我们意义重大！ 🙏😊

[English](./docs/README_EN.md) | 简体中文

</div>

---

## 一、项目简介

**GeminiMCP** 是一个 MCP 服务器，将 Google 的 Gemini CLI 工具封装为标准 MCP 协议接口，让 Claude Code 能够调用 Gemini 执行 AI 辅助编程任务。

核心特性：
- **会话持久化**：通过 `SESSION_ID` 支持多轮对话
- **流式输出**：实时获取 Gemini CLI 的响应
- **沙箱模式**：可选的安全隔离执行环境
- **完整追踪**：可选返回完整的推理过程和工具调用记录

---

## 二、快速开始

### 0. 前置要求

- 已安装并配置 [Claude Code](https://docs.claude.com/docs/claude-code)
- 已安装并配置 [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- 已安装 [uv 工具](https://docs.astral.sh/uv/getting-started/installation/)

**uv 安装方式：**

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> **注意：强烈推荐 Windows 用户在 WSL 中运行本项目！**

### 1. 安装步骤

**1.1** 安装 GeminiMCP

```bash
claude mcp add gemini -s user --transport stdio -- uvx --from git+https://github.com/GuDaStudio/geminimcp.git geminimcp
```

**1.2** 验证安装

```bash
claude mcp list
```

> 看到 `gemini: ... - ✓ Connected` 说明安装成功

**1.3** 可选：配置自动允许

在 `~/.claude/settings.json` 的 allow 项中添加 `mcp__gemini__gemini`

### 2. 配置claude code提示词（可选）

为使claude code更好完成与codex的协同工作，我们**极力推荐您在 `~/.claude/CLAUDE.md`中添加以下内容**

<details>
<summary>展开查看prompt</summary>


```
## Core Instruction for Gemini MCP

在任何时刻，你必须思考当前过程可以如何与codex进行协作，如何调用Codex 为你提供的MCP工具作为你客观全面分析的保障。
其中你**务必执行**以下几个步骤：
**1** 在你对用户需求形成初步分析后，将用户需求、初始思路告知codex，并要求其完善需求分析和实施计划。
**2** 在实施具体编码任务前，**必须向codex索要代码实现原型（要求codex仅给出unified diff patch，严禁对代码做任何真实修改）**。在获取代码原型后，你**只能以此为逻辑参考，再次对代码修改进行重写**，形成企业生产级别、可读性极高、可维护性极高的代码后，才能实施具体编程修改任务。
**3** 无论何时，只要完成切实编码行为后，**必须立即使用codex review代码改动和对应需求完成程度**。
**4** codex只能给出参考，你**必须有自己的思考，甚至需要对codex的回答提出置疑**。尽信书则不如无书，你与codex的最终使命都是达成统一、全面、精准的意见，所以你们必须不断争辩已找到通向真理的唯一途径。


## Codex Tool Invocation Specification

 1. 工具概述

  codex MCP 提供了一个工具 `codex`，用于执行 AI 辅助的编码任务。该工具**通过 MCP 协议调用**，无需使用命令行。

  2. 工具参数

  **必选**参数：
  - PROMPT (string): 发送给 codex 的任务指令
  - cd (Path): codex 执行任务的工作目录根路径

  可选参数：
  - sandbox (string): 沙箱策略，可选值：
    - "read-only" (默认): 只读模式，最安全
    - "workspace-write": 允许在工作区写入
    - "danger-full-access": 完全访问权限
  - SESSION_ID (UUID | null): 用于继续之前的会话以与codex进行多轮交互，默认为 None（开启新会话）
  - skip_git_repo_check (boolean): 是否允许在非 Git 仓库中运行，默认 False
  - return_all_messages (boolean): 是否返回所有消息（包括推理、工具调用等），默认 False
  - image (List[Path] | null): 附加一个或多个图片文件到初始提示词，默认为 None
  - model (string | null): 指定使用的模型，默认为 None（使用用户默认配置）
  - yolo (boolean | null): 无需审批运行所有命令（跳过沙箱），默认 False
  - profile (string | null): 从 `~/.codex/config.toml` 加载的配置文件名称，默认为 None（使用用户默认配置）

  返回值：
  {
    "success": true,
    "SESSION_ID": "uuid-string",
    "agent_messages": "agent回复的文本内容",
    "all_messages": []  // 仅当 return_all_messages=True 时包含
  }
  或失败时：
  {
    "success": false,
    "error": "错误信息"
  }

  3. 使用方式

  开启新对话：
  - 不传 SESSION_ID 参数（或传 None）
  - 工具会返回新的 SESSION_ID 用于后续对话

  继续之前的对话：
  - 将之前返回的 SESSION_ID 作为参数传入
  - 同一会话的上下文会被保留

  4. 调用规范

  **必须遵守**：
  - 每次调用 codex 工具时，必须保存返回的 SESSION_ID，以便后续继续对话
  - cd 参数必须指向存在的目录，否则工具会静默失败
  - 严禁codex对代码进行实际修改，使用 sandbox="read-only" 以避免意外，并要求codex仅给出unified diff patch即可

  推荐用法：
  - 如需详细追踪 codex 的推理过程和工具调用，设置 return_all_messages=True
  - 对于精准定位、debug、代码原型快速编写等任务，优先使用 codex 工具

  5. 注意事项

  - 会话管理：始终追踪 SESSION_ID，避免会话混乱
  - 工作目录：确保 cd 参数指向正确且存在的目录
  - 错误处理：检查返回值的 success 字段，处理可能的错误

```

</details>


---

## 三、工具说明

### gemini 工具

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `PROMPT` | `str` | ✅ | - | 发送给 Gemini 的任务指令 |
| `sandbox` | `bool` | ❌ | `False` | 是否启用沙箱模式 |
| `SESSION_ID` | `str` | ❌ | `""` | 会话 ID（空则开启新会话） |
| `return_all_messages` | `bool` | ❌ | `False` | 是否返回完整消息记录 |
| `model` | `str` | ❌ | `""` | 指定模型（默认使用 Gemini CLI 配置） |

### 返回值结构

**成功时：**
```json
{
  "success": true,
  "SESSION_ID": "session-uuid",
  "agent_messages": "Gemini 的回复内容..."
}
```

**启用 return_all_messages 时额外包含：**
```json
{
  "all_messages": [...]
}
```

**失败时：**
```json
{
  "success": false,
  "error": "错误信息描述"
}
```

---

## 四、使用示例

### 开启新会话
```
调用 gemini 工具，PROMPT 设为任务描述
```

### 继续对话
```
使用上次返回的 SESSION_ID 继续对话
```

---

## 五、FAQ

<details>
<summary>Q1: 与 Gemini CLI 直接使用有什么区别？</summary>

GeminiMCP 将 Gemini CLI 封装为 MCP 协议，使 Claude Code 可以程序化调用，支持会话管理和结构化返回。

</details>

<details>
<summary>Q2: 会话会冲突吗？</summary>

不会。每个会话使用独立的 `SESSION_ID`，完全隔离。

</details>

---

## 🤝 贡献指南

```bash
# 克隆仓库
git clone https://github.com/GuDaStudio/geminimcp.git
cd geminimcp

# 安装依赖
uv sync
```

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

Copyright (c) 2025 [guda.studio](mailto:gudaclaude@gmail.com)
