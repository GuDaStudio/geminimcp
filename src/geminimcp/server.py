"""FastMCP server implementation for the Gemini MCP project."""

from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import Annotated, Any, Dict, Generator, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import shutil

mcp = FastMCP("Gemini MCP Server-from guda.studio")

# Default timeout for gemini CLI execution (5 minutes)
DEFAULT_TIMEOUT = 300


class GeminiAuthError(Exception):
    """Raised when Gemini CLI is not authenticated."""
    pass


class GeminiTimeoutError(Exception):
    """Raised when Gemini CLI execution times out."""
    pass


def check_gemini_auth() -> tuple[bool, str]:
    """Check if Gemini CLI is authenticated.

    Returns:
        Tuple of (is_authenticated, status_message)
    """
    try:
        # Try a quick command to check auth status
        result = subprocess.run(
            ["gemini", "--version"],
            capture_output=True,
            timeout=10,
            text=True,
        )
        # If gemini runs without prompting for auth, we're good
        # The actual auth check happens when we try to use it
        return (result.returncode == 0, result.stdout.strip())
    except subprocess.TimeoutExpired:
        return (False, "Gemini CLI timed out during auth check")
    except FileNotFoundError:
        return (False, "Gemini CLI not found in PATH")
    except Exception as e:
        return (False, f"Auth check failed: {e}")


def run_shell_command(
    cmd: list[str],
    cwd: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Generator[str, None, None]:
    """Execute a command and stream its output line-by-line.

    Args:
        cmd: Command and arguments as a list
        cwd: Working directory for the command
        timeout: Maximum execution time in seconds

    Yields:
        Output lines from the command

    Raises:
        GeminiTimeoutError: If execution exceeds timeout
    """
    popen_cmd = cmd.copy()  # Don't mutate the original list

    gemini_path = shutil.which("gemini") or cmd[0]
    popen_cmd[0] = gemini_path

    process = subprocess.Popen(
        popen_cmd,
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',
        cwd=cwd,
    )

    output_queue: queue.Queue[str | None] = queue.Queue(maxsize=10000)  # Bounded queue
    GRACEFUL_SHUTDOWN_DELAY = 0.3
    start_time = time.time()

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
            try:
                for line in iter(process.stdout.readline, ""):
                    stripped = line.strip()
                    try:
                        output_queue.put(stripped, timeout=1)
                    except queue.Full:
                        # Queue is full, skip this line to prevent memory issues
                        continue
                    if is_turn_completed(stripped):
                        time.sleep(GRACEFUL_SHUTDOWN_DELAY)
                        process.terminate()
                        break
            finally:
                process.stdout.close()
        output_queue.put(None)

    thread = threading.Thread(target=read_output, daemon=True)
    thread.start()

    # Yield lines while process is running, with timeout check
    while True:
        # Check for timeout
        elapsed = time.time() - start_time
        if elapsed > timeout:
            process.kill()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            raise GeminiTimeoutError(
                f"Gemini CLI execution timed out after {timeout} seconds. "
                "This may indicate the CLI is waiting for authentication or is stuck."
            )

        try:
            line = output_queue.get(timeout=0.5)
            if line is None:
                break
            yield line
        except queue.Empty:
            if process.poll() is not None and not thread.is_alive():
                break

    # Cleanup
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass  # Process is truly stuck, nothing we can do

    # Wait for thread with timeout
    thread.join(timeout=5)
    if thread.is_alive():
        # Thread is stuck, but it's a daemon thread so it will be cleaned up on exit
        pass

    # Drain remaining queue items
    while not output_queue.empty():
        try:
            line = output_queue.get_nowait()
            if line is not None:
                yield line
        except queue.Empty:
            break


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
    meta={"version": "0.1.1", "author": "guda.studio"},
)
async def gemini(
    PROMPT: Annotated[str, "Instruction for the task to send to gemini."],
    cd: Annotated[Path, "Set the workspace root for gemini before executing the task."],
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
    timeout: Annotated[
        int,
        Field(description="Maximum execution time in seconds. Defaults to 300 (5 minutes)."),
    ] = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """Execute a gemini CLI session and return the results."""

    # Check if workspace exists
    if not cd.exists():
        return {
            "success": False,
            "error": f"The workspace root directory `{cd.absolute().as_posix()}` does not exist."
        }

    # Pre-flight auth check
    auth_ok, auth_msg = check_gemini_auth()
    if not auth_ok:
        return {
            "success": False,
            "error": f"Gemini CLI authentication check failed: {auth_msg}. "
                     "Please run 'gemini auth login' manually in your terminal."
        }

    cmd = ["gemini", "--prompt", PROMPT, "-o", "stream-json"]

    if sandbox:
        cmd.extend(["--sandbox"])

    if model:
        cmd.extend(["--model", model])

    if SESSION_ID:
        cmd.extend(["--resume", SESSION_ID])

    all_messages: list[dict] = []
    agent_messages = ""
    success = True
    err_message = ""
    thread_id: Optional[str] = None

    try:
        for line in run_shell_command(cmd, cwd=cd.absolute().as_posix(), timeout=timeout):
            try:
                line_dict = json.loads(line.strip())
                all_messages.append(line_dict)
                item_type = line_dict.get("type", "")
                item_role = line_dict.get("role", "")

                if item_type == "message" and item_role == "assistant":
                    content = line_dict.get("content", "")
                    # Skip deprecation warnings
                    if "The --prompt (-p) flag has been deprecated" in content:
                        continue
                    agent_messages += content

                if line_dict.get("session_id") is not None:
                    thread_id = line_dict.get("session_id")

            except json.JSONDecodeError:
                # Limit error message accumulation
                if len(err_message) < 2000:
                    err_message += f"\n[json decode error] {line[:200]}"
                continue
            except Exception as error:
                err_message += f"\n[unexpected error] {error}"
                break

    except GeminiTimeoutError as e:
        return {
            "success": False,
            "error": str(e),
            "all_messages": all_messages if return_all_messages else None,
        }

    # Validate results
    if thread_id is None:
        success = False
        err_message = "Failed to get `SESSION_ID` from the gemini session.\n" + err_message

    if success and len(agent_messages) == 0:
        success = False
        err_message = (
            "Failed to retrieve `agent_messages` from the Gemini session. "
            "This might be due to Gemini performing a tool call. "
            "You can continue using the `SESSION_ID` to proceed.\n" + err_message
        )

    # Build result
    if success:
        result: Dict[str, Any] = {
            "success": True,
            "SESSION_ID": thread_id,
            "agent_messages": agent_messages,
        }
    else:
        result = {"success": False, "error": err_message.strip()}

    if return_all_messages:
        result["all_messages"] = all_messages

    return result


def run() -> None:
    """Start the MCP server over stdio transport."""
    mcp.run(transport="stdio")
