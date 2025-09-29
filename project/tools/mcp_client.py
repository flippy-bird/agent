import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession
from typing import Optional
from contextlib import AsyncExitStack
from mcp.client.streamable_http import streamablehttp_client
import gc

class MCPClient:
    def __init__(self, url):
        self.server_url = url
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self.connected = False
        self._cleanup_done = False

    async def connect_server(self):
        try:
            # 使用AsyncExitStack进行快速连接
            self.exit_stack = AsyncExitStack()
            read_stream, write_stream, _ = await self.exit_stack.enter_async_context(streamablehttp_client(self.server_url))
            self.session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            await self.session.initialize()
            self.connected = True
        except Exception as e:
            # 如果连接失败，确保清理资源
            await self._cleanup_on_error()
            raise e
    async def _cleanup_on_error(self):
        """连接失败时的清理方法"""
        try:
            if self.session:
                self.session = None
            if self.exit_stack:
                self.exit_stack = None
            self.connected = False
        except Exception:
            pass  # 忽略清理错误

    async def get_tools(self):
        if not self.session:
            raise ValueError("please connect to server first")
        
        response = await self.session.list_tools()
        tools = response.tools
        self.tools = [tool.name for tool in tools]
        avaliable_tools = [
            {
                "type":"function",
                "function": {
                    "name":tool.name,
                    "description":tool.description,
                    "parameters": tool.inputSchema 
                } 
            } for tool in tools
        ]

        return avaliable_tools
    
    async def call_tool(self, tool_name:str, tool_args:dict):
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        tool_result = await self.session.call_tool(tool_name, tool_args)
        return tool_result.content[0].text

    async def cleanup(self):
        if self._cleanup_done:
            return
            
        if self.connected:
            try:
                # 先关闭session
                if self.session:
                    try:
                        # 尝试优雅关闭session
                        if hasattr(self.session, 'close'):
                            await self.session.close()
                    except Exception as e:
                        pass  # 忽略session关闭错误
                    finally:
                        self.session = None
                
                # 关闭exit_stack，使用静默处理避免错误显示
                if self.exit_stack:
                    try:
                        await self.exit_stack.aclose()
                    except Exception as e:
                        # 静默处理所有清理错误，包括取消作用域错误
                        pass
                    finally:
                        self.exit_stack = None
                        
            except Exception as e:
                # 静默处理清理错误
                pass
            finally:
                self.connected = False
                self._cleanup_done = True
                # 强制垃圾回收
                gc.collect()