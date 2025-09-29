import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from log.custom_log import custom_logger
from llms.memory import Memory
from prompts.prompt import SYSTEM_PROMPT
from llms.qwen_llm import QwenLLM
from tools.mcp_client import MCPClient
from tools.gaode_map import gaode_server_url
from tools.xhs_search import xhs_server_url
import json
import asyncio

class Agent:
    def __init__(self, client: QwenLLM):
        self.client = client
        self.memory = Memory()
        self.mcp_map_client = MCPClient(gaode_server_url)
        self.mcp_xhs_client = MCPClient(xhs_server_url)
        self.tools = []
    async def get_tools(self):
        try:
            await self.mcp_map_client.connect_server()
            self.map_tools = await self.mcp_map_client.get_tools()
        except Exception as e:
            print(f"连接地图服务器失败: {e}")
            self.map_tools = []
            
        try:
            await self.mcp_xhs_client.connect_server()
            self.xhs_tools = await self.mcp_xhs_client.get_tools()
        except Exception as e:
            print(f"连接XHS服务器失败: {e}")
            self.xhs_tools = []
            
        self.tools = self.tools + self.map_tools + self.xhs_tools
    async def query(self, query):
        system_prompt = SYSTEM_PROMPT.format(tools=self.tools)
        messages = [{"role":"user", "content":query}]
        history_messages = self.memory.get_memory()
        if len(history_messages) > 0:
            self.memory.add(messages)
            messages = history_messages + messages
        else:
            system_message = {"role":"system", "content":system_prompt}
            self.memory.add(system_message)
            self.memory.add(messages[0])
        
        should_act = await self.think(messages)  
        if should_act:
            await self.act()
        return should_act

    def get_result(self):
        messages = self.memory.get_memory()
        return messages[-1].content
    async def step(self):
        messages = self.memory.get_memory()
        should_act = await self.think(messages)  
        if should_act:
            await self.act()
        return should_act
        
    async def think(self, messages):
        # await self.get_tools()
        res = self.client.chat(messages, self.tools)
        # custom_logger.info(res.choices[0].message.content)
        self.memory.add(res.choices[0].message)
        if res.choices[0].message.tool_calls:
            return True
        return False

    async def act(self):
        tool_calls = self.memory.get_memory()[-1].tool_calls[0]
        tool_name = tool_calls.function.name
        tool_args = tool_calls.function.arguments
        tool_result = ""
        if tool_name in [tool["function"]["name"] for tool in self.map_tools]:
            if tool_args:
                tool_args = json.loads(tool_args)
                tool_result = await self.mcp_map_client.call_tool(tool_name, tool_args)
            else:
                tool_result = await self.mcp_map_client.call_tool(tool_name, {})
        if tool_name in [tool["function"]["name"] for tool in self.xhs_tools]:
            if tool_args:
                tool_args = json.loads(tool_args)
                tool_result = await self.mcp_xhs_client.call_tool(tool_name, tool_args)
            else:
                tool_result = await self.mcp_xhs_client.call_tool(tool_name, {})
        custom_logger.info(f"[Calling tool {tool_name} with args {tool_args}]")
        self.memory.add({"role":"tool",
                            "content":tool_result,
                            "tool_call_id":tool_calls.id})
    async def clean(self):
        """清理所有MCP连接，使用顺序清理以避免并发问题"""
        print("开始清理MCP连接...")
        
        # 顺序清理每个客户端，避免并发问题
        if hasattr(self, 'mcp_map_client') and self.mcp_map_client:
            await self._safe_cleanup(self.mcp_map_client, "地图客户端")
        
        if hasattr(self, 'mcp_xhs_client') and self.mcp_xhs_client:
            await self._safe_cleanup(self.mcp_xhs_client, "XHS客户端")
        
        print("MCP连接清理完成")
    
    async def _safe_cleanup(self, client, client_name):
        """安全清理单个客户端"""
        try:
            if hasattr(client, 'cleanup'):
                await client.cleanup()
                print(f"✅ {client_name}清理完成")
            else:
                print(f"⚠️ {client_name}没有cleanup方法")
        except Exception as e:
            # 检查是否是取消作用域错误
            if "cancel scope" in str(e).lower():
                print(f"⚠️ {client_name}清理时遇到取消作用域问题，已静默处理")
            else:
                print(f"❌ 清理{client_name}时出错: {e}")
            # 即使出错也继续清理其他客户端
        
        

if __name__ == "__main__":
    async def main():
        agent = None
        try:
            client = QwenLLM()
            agent = Agent(client)
            query = input("请输入你的旅游想法：")
            await agent.get_tools()
            not_finished = await agent.query(query)
            while not_finished:
                not_finished = await agent.step()
            res = agent.get_result()
            custom_logger.info(res)
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"程序运行出错: {e}")
            custom_logger.error(f"程序运行出错: {e}")
        finally:
            if agent:
                try:
                    await agent.clean()
                except Exception as e:
                    print(f"清理资源时出错: {e}")
    
    # 使用更安全的方式运行异步主函数，忽略关闭时的错误
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        # 检查是否是取消作用域错误，如果是则静默处理
        if "cancel scope" in str(e).lower():
            print("程序正常结束")
        else:
            print(f"程序启动失败: {e}")
