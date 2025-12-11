"""FastMCP server implementation for the Gemini MCP project."""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Annotated, Any, Dict, Generator, List, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BeforeValidator, Field
import shutil

mcp = FastMCP("Gemini MCP Server-from guda.studio")


def run_shell_command(cmd: list[str]) -> Generator[str, None, None]:
    """Execute a command and stream its output line-by-line.

    Args:
        cmd: Command and arguments as a list (e.g., ["gemini", "-o", "stream-json", "--", "prompt"])

    Yields:
        Output lines from the command
    """
    popen_cmd = cmd

    gemini_path = shutil.which("gemini") or cmd[0]
    popen_cmd[0] = gemini_path

    # if os.name == "nt" and gemini_path.lower().endswith((".cmd", ".bat")):
    #     from subprocess import list2cmdline
    #     popen_cmd = ["cmd.exe", "/s", "/c", list2cmdline(cmd)]

    process = subprocess.Popen(
        popen_cmd,
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',
    )

    output_queue: queue.Queue[str | None] = queue.Queue()
    GRACEFUL_SHUTDOWN_DELAY = 0.3

    def is_turn_completed(line: str) -> bool:
        """Check if the line indicates turn completion via JSON parsing."""
        try:
            data = json.loads(line)
            return data.get("type") == "turn.completed"
        except (json.JSONDecodeError, AttributeError, TypeError):
            return False

    def read_output() -> None:
        """Read process output in a separate thread."""
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                stripped = line.strip()
                output_queue.put(stripped)
                if is_turn_completed(stripped):
                    time.sleep(GRACEFUL_SHUTDOWN_DELAY)
                    process.terminate()
                    break
            process.stdout.close()
        output_queue.put(None)

    thread = threading.Thread(target=read_output)
    thread.start()

    # Yield lines while process is running
    while True:
        try:
            line = output_queue.get(timeout=0.5)
            if line is None:
                break
            yield line
        except queue.Empty:
            if process.poll() is not None and not thread.is_alive():
                break

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    thread.join(timeout=5)

    while not output_queue.empty():
        try:
            line = output_queue.get_nowait()
            if line is not None:
                yield line
        except queue.Empty:
            break


def windows_escape(prompt):
    """
    Windows 风格的字符串转义函数。
    把常见特殊字符转义成 \\ 形式，适合命令行、JSON 或路径使用。
    比如：\n 变成 \\n，" 变成 \\"。
    """
    # 先处理反斜杠，避免它干扰其他替换
    result = prompt.replace("\\", "\\\\")
    # 双引号，转义成 \"，防止字符串边界乱套
    result = result.replace('"', '\\"')
    # 换行符，Windows 常用 \r\n，但我们分开转义
    result = result.replace("\n", "\\n")
    result = result.replace("\r", "\\r")
    # 制表符，空格的“超级版”
    result = result.replace("\t", "\\t")
    # 其他常见：退格符（像按了后退键）、换页符（打印机跳页用）
    result = result.replace("\b", "\\b")
    result = result.replace("\f", "\\f")
    # 如果有单引号，也转义下（不过 Windows 命令行不那么严格，但保险起见）
    result = result.replace("'", "\\'")

    return result


@mcp.tool(
    name="gemini",
    description="""
    Invokes the Gemini CLI to execute AI-driven tasks, returning structured JSON events and a session identifier for conversation continuity. 
    
    **Return structure:**
        - `success`: boolean indicating execution status
        - `SESSION_ID`: unique identifier for resuming this conversation in future calls
        - `agent_messages`: concatenated assistant response text
        - `all_messages`: (optional) complete array of JSON events when `return_all_messages=True`
        - `error`: error description when `success=False`

    **Best practices:**
        - Always capture and reuse `SESSION_ID` for multi-turn interactions
        - Enable `sandbox` mode when file modifications should be isolated
        - Use `return_all_messages` only when detailed execution traces are necessary (increases payload size)
        - Only pass `model` when the user has explicitly requested a specific model
    """,
    meta={"version": "0.0.0", "author": "guda.studio"},
)
async def gemini(
    PROMPT: Annotated[str, "Instruction for the task to send to gemini."],
    sandbox: Annotated[
        bool,
        Field(description="Run in sandbox mode. Defaults to `False`."),
    ] = False,
    SESSION_ID: Annotated[
        str,
        "Resume the specified session of the gemini. Defaults to empty string, start a new session.",
    ] = "",
    return_all_messages: Annotated[
        bool,
        "Return all messages (e.g. reasoning, tool calls, etc.) from the gemini session. Set to `False` by default, only the agent's final reply message is returned.",
    ] = False,
    model: Annotated[
        str,
        "The model to use for the gemini session. This parameter is strictly prohibited unless explicitly specified by the user.",
    ] = "",
) -> Dict[str, Any]:
    """Execute a gemini CLI session and return the results."""

    if os.name == "nt":
        PROMPT = windows_escape(PROMPT)
    else:
        PROMPT = PROMPT

    cmd = ["gemini", "--prompt", PROMPT, "-o", "stream-json"]

    if sandbox:
        cmd.extend(["--sandbox"])

    if model:
        cmd.extend(["--model", model])

    if SESSION_ID:
        cmd.extend(["--resume", SESSION_ID])

    all_messages = []
    agent_messages = ""
    success = True
    err_message = ""
    thread_id: Optional[str] = None

    for line in run_shell_command(cmd):
        try:
            line_dict = json.loads(line.strip())
            all_messages.append(line_dict)
            item_type = line_dict.get("type", "")
            item_role = line_dict.get("role", "")
            if item_type == "message" and item_role == "assistant":
                if (
                    "The --prompt (-p) flag has been deprecated and will be removed in a future version. Please use a positional argument for your prompt. See gemini --help for more information.\n"
                    in line_dict.get("content", "")
                ):
                    continue
                agent_messages = agent_messages + line_dict.get("content", "")
            if line_dict.get("session_id") is not None:
                thread_id = line_dict.get("session_id")
            # if "fail" in line_dict.get("type", ""):
            #     success = False
            #     err_message = "gemini error: " + line_dict.get("error", {}).get("message", "")
            #     break
            # if "error" in line_dict.get("type", ""):
            #     success = False
            #     err_message = "gemini error: " + line_dict.get("message", "")
        except json.JSONDecodeError as error:
            # Improved error handling: include problematic line
            err_message += "\n\n[json decode error] " + line
            continue
        except Exception as error:
            err_message += "\n\n[unexpected error] " + f"Unexpected error: {error}. Line: {line!r}"
            break


    if thread_id is None:
        success = False
        err_message = (
            "Failed to get `SESSION_ID` from the gemini session. \n\n" + err_message
        )

    if success and len(agent_messages) == 0:
        success = False
        err_message = (
            "Failed to retrieve `agent_messages` data from the Gemini session. This might be due to Gemini performing a tool call. You can continue using the `SESSION_ID` to proceed with the conversation. \n\n "
            + err_message
        )

    if success:
        result: Dict[str, Any] = {
            "success": True,
            "SESSION_ID": thread_id,
            "agent_messages": agent_messages,
            # "PROMPT": PROMPT,
        }
    else:
        result = {"success": False, "error": err_message}
    
    if return_all_messages:
        result["all_messages"] = all_messages

    return result


def run() -> None:
    """Start the MCP server over stdio transport."""
    mcp.run(transport="stdio")
