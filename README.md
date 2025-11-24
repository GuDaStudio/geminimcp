![这是图片](./images/title.png)

<div align="center">

**让 Claude Code 与 Gemini CLI 无缝协作**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io) [![Share](https://img.shields.io/badge/share-000000?logo=x&logoColor=white)](https://x.com/intent/tweet?text=GeminiMCP：让%20Claude%20Code%20与%20Gemini%20无缝协作%20https://github.com/GuDaStudio/geminimcp%20%23AI%20%23Coding%20%23MCP) [![Share](https://img.shields.io/badge/share-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/GuDaStudio/geminimcp) [![Share](https://img.shields.io/badge/share-FF4500?logo=reddit&logoColor=white)](https://www.reddit.com/submit?title=GeminiMCP：让%20Claude%20Code%20与%20Gemini%20无缝协作&url=https://github.com/GuDaStudio/geminimcp) [![Share](https://img.shields.io/badge/share-0088CC?logo=telegram&logoColor=white)](https://t.me/share/url?url=https://github.com/GuDaStudio/geminimcp&text=GeminiMCP：让%20Claude%20Code%20与%20Gemini%20无缝协作)

⭐ 在GitHub上给我们点星~您的支持对我们意义重大！ 🙏😊

[English](./docs/README_EN.md) | 简体中文

</div>

---
## 零、效果示例

**1.** 本次测评使用**完全相同**的提示词。使用 / 不使用本项目的效果如下所示，可以看到，使用了Gemini-MCP后的前端网页无论是在审美布局还是在动画特效上都明显优于仅使用claude code进行前端编码的版本。
  <details>
  <summary>点击查看提示词详情。</summary>

  ```
  设计一张极致精美的天气卡片，用于超高清大屏海报展示。

  整体氛围：深冬雪景，中国风水墨意境，画面要有「静」与「远」的诗意，仿佛一眼望去就能听见雪落的声音。

  背景：远景是连绵起伏的山脉，采用中国水墨山水的笔触，层层叠叠，虚实相间，有 atmospheric perspective 的层次感；山间有薄雾与云气缭绕，隐约可见几棵苍松或一座小亭，增加东方韵味和故事感。

  色调：以冷青蓝、墨灰、苍白为主，局部点缀一点温暖的灯光或朱红印章，让画面在寒意中有一点人间烟火。

  天气卡片本体：

  作为画面主体，布局偏中间略右或略左，大小适合大屏阅读，留足呼吸感与留白。
  不是毛玻璃风格，避免玻璃态、磨砂玻璃、强烈模糊效果。
  采用更高级的卡片质感：类似宣纸、细腻磨砂金属或温润玉石，一侧有柔和高光和细微阴影，边缘略带中国传统窗格、回纹或细线描边，整体极简、干净。
  信息排版克制且有节奏：城市名与当前温度可用带有行书/楷书气质的中文字体或与之相匹配的优雅英文字体，小号文字用于日期、天气描述和空气质量等，中英混排自然协调。
  雪花效果（WebGL）：

  雪花不是简单粒子点，而是用 WebGL 创建的精致雪花：具有六角对称的晶体结构，边缘细腻，带微光反射。
  雪花分前景、中景、远景多层深度，大小、透明度与锐度随距离变化，营造强烈空间感。
  飘落轨迹带有轻微旋转与摆动，有缓慢加速和微随机的风向变化，整体运动优雅、克制，不喧宾夺主。
  部分雪花掠过天气卡片边缘，形成轻微遮挡关系，加强「卡片在雪中」的沉浸感。
  风格要求：

  整体中国风现代化融合：水墨山水 + 极简 UI 设计。
  画面高分辨率、适配 16:9 大屏海报。
  构图讲究留白与平衡，富有东方韵味与时间流逝的宁静感。
  体现「最高水准」的精细度、质感和氛围，而非普通界面截图。
  ```

  </details>

**2.** 在Claude Code中**使用Gemini-MCP**，您可以通过[该链接](https://codepen.io/Studio-Guda/full/yyOpBVZ)进行在线预览！

https://github.com/user-attachments/assets/1996980b-da6a-43cf-8c02-6c008f54ed18


**3.** 仅使用Claude Code，您可以通过[该链接](https://codepen.io/Studio-Guda/full/ogxpvGY)进行在线预览！

https://github.com/user-attachments/assets/18d59123-e972-410e-824a-7462d3d95dd5


---

## 一、项目简介

**Gemini-MCP** 是一个 MCP 服务器，将 Google 的 Gemini CLI 工具封装为标准 MCP 协议接口，让 Claude Code 能够调用 Gemini 执行 AI 辅助编程任务。

🍟 本项目围绕**gemini强大的前端设计**能力[提供了prompt](#2-配置claude-code提示词可选)，以丰富您的使用场景，我们十分推荐您进行配置！


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

![](./images/image.png)

### 2. 配置claude code提示词（可选）

为使claude code更好完成与gemini的协同工作，我们**极力推荐您在 `~/.claude/CLAUDE.md`中添加以下内容**

<details>
<summary>展开查看prompt</summary>


```
## Core Instruction for Gemini MCP

在任何时刻，你必须思考当前过程可以如何与 gemini 进行协作，如何调用 gemini 为你提供的MCP工具作为你**客观全面分析**的保障。

其中你**务必执行**以下几个步骤：

**1** 在你对用户需求**形成初步分析后**，
（1）首先将用户**原始需求（一字不差，严禁转述）**、以及你的初始思路告知gemini；
（2）与gemini进行**充分讨论、辩驳**，以完善需求分析和实施计划。这一步的结束标志为，**必须**确保对用户需求的透彻理解，并**生成切实可行的行动计划**。

**2** 在实施具体编码任务前，你**必须向gemini索要代码实现原型**（要求gemini仅给出unified diff patch，严禁对代码做任何真实修改）。在获取代码原型后，你**只能以此为逻辑参考，再次对代码修改进行重写**，形成企业生产级别、可读性极高、可维护性极高的代码后，才能实施具体编程修改任务。
  - **注意：** Gemini 十分擅长前端代码，并精通样式、UI组件设计。在涉及前端代码时，你必须向其索要代码原型（CSS/React/Vue/HTML等前端代码），任何时刻，你**必须以gemini的前端设计（原型代码）为最终的前端代码基点**。
  - 例如，当你识别到用户给出了前端设计需求，你的首要行为必须自动调整为，将用户需求原封不动转发给gemini，并让其出具代码示例（此阶段严禁对用户需求进行任何改动、简写等等）。即你必须从gemini获取代码基点，才可以进行接下来的各种行为。

## Gemini Tool Invocation Specification

 1. 工具概述

  gemini MCP 提供了一个工具 `gemini`，用于调用 Google Gemini 模型执行 AI 任务。该工具拥有极强的前端审美、任务规划与需求理解能力，但在**上下文长度（Effective 32k）**上有限制。

2. 使用方式与规范

  **必须遵守的限制**：
  - **会话管理**：捕获返回的 `SESSION_ID` 用于多轮对话。
  - **后端避让**：严禁让 Gemini 编写复杂的后端业务逻辑代码。

  **擅长场景（必须优先调用 Gemini）**：
  - **需求清晰化**：在任务开始阶段辅助生成引导性问题。
  - **任务规划**：生成 Step-by-step 的实施计划。
  - **前端原型**：编写 CSS、HTML、UI 组件代码，调整样式风格。

```

</details>


---

## 三、工具说明

<details>

<summary>展开查看gemini 工具详情</summary>

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


</details>

---



## 四、FAQ

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

---
<div align="center">

## 用 🌟 为本项目助力~

</div>

[![Star History Chart](https://api.star-history.com/svg?repos=GuDaStudio/geminimcp&type=date&legend=top-left)](https://www.star-history.com/#GuDaStudio/geminimcp&type=date&legend=top-left)
