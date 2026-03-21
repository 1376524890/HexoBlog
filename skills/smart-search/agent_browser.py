"""
Agent Browser for SmartSearch
==============================
使用 agent-browser 进行浏览器自动化抓取

Agent Browser 是 Vercel 官方的无头浏览器自动化 CLI，支持：
- 原生 Rust 二进制，性能优秀
- Chrome/Chromium CDP 直接连接
- JavaScript 渲染页面
- 交互式操作（点击、填充、滚动等）
- 访问树快照（accessibility tree）
- 语义定位器（semantic locators）

使用方法：
  # 命令行
  python agent_browser.py "https://example.com" --action snapshot
  
  # Python 模块
  from agent_browser import AgentBrowser
  browser = AgentBrowser()
  result = await browser.snapshot()
"""

import asyncio
import subprocess
import json
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BrowserResult:
    """浏览器操作结果"""
    success: bool
    command: str
    output: str
    error: str = ""
    return_code: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转为字典"""
        return {
            "success": self.success,
            "command": self.command,
            "output": self.output,
            "error": self.error,
            "return_code": self.return_code,
            "timestamp": self.timestamp.isoformat()
        }


class AgentBrowser:
    """
    Agent Browser 封装类
    
    提供高级 API 包装原生 CLI 命令
    """
    
    def __init__(self, executable: str = "agent-browser", profile: str = "openclaw"):
        """
        初始化 Agent Browser
        
        Args:
            executable: CLI 可执行文件名或路径
            profile: 浏览器配置配置文件
        """
        self.executable = executable
        self.profile = profile
        self.session = f"smartsess-{profile}"
        self.download_path = os.path.expanduser("~/.openclaw/workspace/browser-downloads")
        
        # 确保下载目录存在
        os.makedirs(self.download_path, exist_ok=True)
    
    async def run_command(self, *args, timeout: int = 60) -> BrowserResult:
        """
        运行 agent-browser 命令
        
        Args:
            *args: 命令参数
            timeout: 超时时间（秒）
            
        Returns:
            BrowserResult
        """
        cmd = [self.executable] + list(args)
        cmd_str = " ".join(cmd)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')
            
            return BrowserResult(
                success=process.returncode == 0,
                command=cmd_str,
                output=output,
                error=error,
                return_code=process.returncode
            )
            
        except asyncio.TimeoutError:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            
            return BrowserResult(
                success=False,
                command=cmd_str,
                output="",
                error="Timeout after {} seconds".format(timeout),
                return_code=-1
            )
        except Exception as e:
            return BrowserResult(
                success=False,
                command=cmd_str,
                output="",
                error=str(e),
                return_code=-1
            )
    
    async def open(self, url: str, wait: str = "networkidle") -> BrowserResult:
        """
        打开页面
        
        Args:
            url: 目标 URL
            wait: 等待策略 (load/domcontentloaded/networkidle)
            
        Returns:
            BrowserResult
        """
        args = [
            "--session", self.session,
            "--download-path", self.download_path,
            "open", url
        ]
        
        if wait:
            args.extend(["wait", f"--load {wait}"])
        
        return await self.run_command(*args)
    
    async def snapshot(self, interactive: bool = True, json_output: bool = False) -> BrowserResult:
        """
        获取页面快照
        
        Args:
            interactive: 是否显示交互式元素
            json_output: 是否返回 JSON 格式
            
        Returns:
            BrowserResult
        """
        args = ["--session", self.session, "snapshot"]
        
        if interactive:
            args.append("-i")
        
        if json_output:
            args.append("--json")
        
        return await self.run_command(*args)
    
    async def click(self, selector: str, new_tab: bool = False) -> BrowserResult:
        """
        点击元素
        
        Args:
            selector: 选择器（@ref 或 CSS 选择器）
            new_tab: 是否在新标签页打开
            
        Returns:
            BrowserResult
        """
        args = ["--session", self.session, "click", selector]
        
        if new_tab:
            args.append("--new-tab")
        
        return await self.run_command(*args)
    
    async def fill(self, selector: str, text: str) -> BrowserResult:
        """
        填充表单
        
        Args:
            selector: 选择器
            text: 填充文本
            
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "fill", selector, text
        )
    
    async def type(self, selector: str, text: str) -> BrowserResult:
        """
        输入文本（不清除原有内容）
        
        Args:
            selector: 选择器
            text: 输入文本
            
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "type", selector, text
        )
    
    async def get_text(self, selector: str) -> BrowserResult:
        """
        获取元素文本
        
        Args:
            selector: 选择器
            
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "get", "text", selector
        )
    
    async def get_url(self) -> BrowserResult:
        """
        获取当前 URL
        
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "get", "url"
        )
    
    async def get_title(self) -> BrowserResult:
        """
        获取页面标题
        
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "get", "title"
        )
    
    async def screenshot(self, path: Optional[str] = None, full: bool = False) -> BrowserResult:
        """
        截图
        
        Args:
            path: 输出路径
            full: 是否全屏截图
            
        Returns:
            BrowserResult
        """
        args = ["--session", self.session, "screenshot"]
        
        if full:
            args.append("--full")
        
        if path:
            args.append(path)
        
        return await self.run_command(*args)
    
    async def wait(self, *args) -> BrowserResult:
        """
        等待
        
        Args:
            *args: 等待条件
            
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "wait", *args
        )
    
    async def close(self) -> BrowserResult:
        """
        关闭浏览器
        
        Returns:
            BrowserResult
        """
        return await self.run_command(
            "--session", self.session,
            "close"
        )
    
    async def batch(self, commands: List[List[str]], bail: bool = False) -> BrowserResult:
        """
        批处理命令
        
        Args:
            commands: 命令列表
            bail: 遇到错误是否停止
            
        Returns:
            BrowserResult
        """
        import sys
        from io import StringIO
        
        # 准备 JSON 输入
        json_input = json.dumps(commands)
        
        args = ["batch", "--json"]
        
        if bail:
            args.append("--bail")
        
        try:
            process = await asyncio.create_subprocess_exec(
                self.executable, *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=json_input.encode()),
                timeout=300  # 批处理给更长超时
            )
            
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')
            
            return BrowserResult(
                success=process.returncode == 0,
                command=f"batch {len(commands)} commands",
                output=output,
                error=error,
                return_code=process.returncode
            )
            
        except asyncio.TimeoutError:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            
            return BrowserResult(
                success=False,
                command=f"batch {len(commands)} commands",
                output="",
                error="Timeout after 300 seconds",
                return_code=-1
            )
    
    async def find(self, locator_type: str, value: str, action: str, 
                   extra: Optional[str] = None) -> BrowserResult:
        """
        使用语义定位器查找并操作元素
        
        Args:
            locator_type: 定位器类型 (text/role/label/placeholder/alt/title/testid)
            value: 定位值
            action: 操作 (click/fill/type/hover/focus/check/uncheck/text)
            extra: 额外参数（如 fill 的文本）
            
        Returns:
            BrowserResult
        """
        args = [
            "--session", self.session,
            "find", locator_type, value, action
        ]
        
        if extra:
            args.append(extra)
        
        return await self.run_command(*args)


# 全局实例
_agent_browser_instance: Optional[AgentBrowser] = None


def get_agent_browser_instance(profile: str = "openclaw") -> AgentBrowser:
    """获取 Agent Browser 实例"""
    global _agent_browser_instance
    
    if _agent_browser_instance is None:
        _agent_browser_instance = AgentBrowser(profile=profile)
    
    return _agent_browser_instance


if __name__ == "__main__":
    import argparse
    
    async def main():
        parser = argparse.ArgumentParser(
            description="Agent Browser CLI Wrapper",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  # 打开页面并快照
  python agent_browser.py https://example.com --action snapshot
  
  # 批量操作
  python agent_browser.py batch --commands '[[\"open\", \"https://example.com\"], [\"snapshot\", \"-i\"]]'
            """
        )
        
        parser.add_argument("url", nargs="?", help="目标 URL")
        parser.add_argument("--action", "-a", choices=["open", "snapshot", "click", "fill", "text", "url", "title", "screenshot", "batch"],
                          default="snapshot", help="操作类型")
        parser.add_argument("--selector", "-s", help="选择器")
        parser.add_argument("--text", "-t", help="文本")
        parser.add_argument("--profile", "-p", default="openclaw", help="浏览器配置")
        parser.add_argument("--wait", "-w", default="networkidle", help="等待策略")
        parser.add_argument("--output", "-o", help="输出文件")
        
        args = parser.parse_args()
        
        browser = get_agent_browser_instance(profile=args.profile)
        
        if args.action == "open":
            result = await browser.open(args.url or "about:blank", wait=args.wait)
        elif args.action == "snapshot":
            result = await browser.snapshot(interactive=True)
        elif args.action == "click":
            result = await browser.click(args.selector or "@e1")
        elif args.action == "fill":
            result = await browser.fill(args.selector or "@e1", args.text or "")
        elif args.action == "text":
            result = await browser.get_text(args.selector or "@e1")
        elif args.action == "url":
            result = await browser.get_url()
        elif args.action == "title":
            result = await browser.get_title()
        elif args.action == "screenshot":
            result = await browser.screenshot(path=args.output)
        else:
            result = BrowserResult(
                success=False,
                command="unknown",
                output="",
                error="Unknown action"
            )
        
        print(result.output if result.success else f"Error: {result.error}")
        
        await browser.close()
    
    asyncio.run(main())
