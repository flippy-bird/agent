## A2A

> [Agent2Agent (A2A) Protocol](https://github.com/a2aproject/A2A)
>
> 官方demo:[Agent2Agent (A2A) Samples](https://github.com/a2aproject/a2a-samples)
> 也可以参考OpenManus的具体实践: https://github.com/FoundationAgents/OpenManus/tree/main/protocol/a2a/app

### 1. A2A 与MCP的关系

是互补关系,A2A协议是MCP协议的补充，MCP关心的是LLM与Tools之间的通信，A2A关心的是Agent与Agent之间的通信

<img src="https://raw.githubusercontent.com/nashpan/image-hosting/main/image-20250827100804431.png" alt="image-20250827100804431" style="zoom:67%;" />

### 2. A2A的python实现

#### 实现服务端的基本模块

在实现A2A的过程中，需要掌握两个概念：Agent Skills 和 Agent Card，

- **Agent Skills**: 描述了这个Agent的能力和功能

```python
# id: skill唯一标识符
# name：起个容易理解的名字
# description：功能的详细描述
# tags: skill关键词，方便后续归类和查找
# examples: 示例

skill = AgentSkill(
    id='hello_world',
    name='Returns hello world',
    description='just returns hello world',
    tags=['hello world'],
    examples=['hi', 'hello world'],
)
```

- **Agent Card** :我暂时理解成服务站的概念，指定了服务的url，服务站具备哪些能力(Agent Skills)

```python
# This will be the public-facing agent card
public_agent_card = AgentCard(
    name='Hello World Agent',         
    description='Just a hello world agent',
    url='http://localhost:9999/',                                        # 服务器的地址
    version='1.0.0',
    default_input_modes=['text'],
    default_output_modes=['text'],
    capabilities=AgentCapabilities(streaming=True),
    skills=[skill],  # Only the basic skill for the public card          # 具备的能力列表 list[AgentSkills]
    supports_authenticated_extended_card=True,
)
```

- **Agent Executor**

A2A agent 如何处理请求和响应，是通过 Agent Executor的部分来实现的，在python中，需要继承一个基类：

```
a2a.server.agent_execution.AgentExecutor
```

主要是两个方法：

```python
async def execute(self, context: RequestContext, event_queue: EventQueue):
# Handles incoming requests that expect a response or a stream of events. It processes the user's input (available via context) and uses the event_queue to send back Message, Task, TaskStatusUpdateEvent, or TaskArtifactUpdateEvent objects.

async def cancel(self, context: RequestContext, event_queue: EventQueue): 
# Handles requests to cancel an ongoing task.
```

我们来看示例Hello world Agent的实现

```python
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        return 'Hello World'
```

对应的执行器实现是：

```python
class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = HelloWorldAgent()
        
    async def execute(
        self,
        context: RequestContext,                        ## 接受请求，包含请求的信息
        event_queue: EventQueue,                        ## 将处理的结果放到这个地方，然后发送给client
    ) -> None:
        result = await self.agent.invoke()                               ## 这里类似处理逻辑
        await event_queue.enqueue_event(new_agent_text_message(result))   ## 这里返回结果
```

**AgentExecutor** 充当了一个桥梁的作用,相当于决定了 Agent服务的内部逻辑，就是当一个请求来了之后，如果处理这个请求

#### 组装启动服务

```python
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)

if __name__ == '__main__':
    skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='just returns hello world',
        tags=['hello world'],
        examples=['hi', 'hello world'],
    )

    extended_skill = AgentSkill(
        id='super_hello_world',
        name='Returns a SUPER Hello World',
        description='A more enthusiastic greeting, only for authenticated users.',
        tags=['hello world', 'super', 'extended'],
        examples=['super hi', 'give me a super hello'],
    )

    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Hello World Agent',
        description='Just a hello world agent',
        url='http://localhost:9999/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],  # Only the basic skill for the public card
        supports_authenticated_extended_card=True,
    )

    # This will be the authenticated extended agent card
    # It includes the additional 'extended_skill'
    specific_extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
            'description': 'The full-featured hello world agent for authenticated users.',
            'version': '1.0.1',  # Could even be a different version
            # Capabilities and other fields like url, default_input_modes, default_output_modes,
            # supports_authenticated_extended_card are inherited from public_agent_card unless specified here.
            'skills': [
                skill,
                extended_skill,
            ],  # Both skills for the extended card
        }
    )

    request_handler = DefaultRequestHandler(       # 他会路由到executor或cancel
        agent_executor=HelloWorldAgentExecutor(),  # 请求来的时候的处理逻辑
        task_store=InMemoryTaskStore(),            # 用来管理任务的生命周期,类似session
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,              # 这个agent card很重要，需要通过他来展示这个agent的能力和用法
        http_handler=request_handler,
        extended_agent_card=specific_extended_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
```

#### 客户端

官方hello world demo实现包括三部分

1. 从服务器获取Agent Card来了解server具备哪些能力；
2. 创建一个A2AClient 实例；
3. 发送请求；

获取Agent card信息

```python
base_url = 'http://localhost:9999'

async with httpx.AsyncClient() as httpx_client:
    # Initialize A2ACardResolver
    resolver = A2ACardResolver(
        httpx_client=httpx_client,
        base_url=base_url,
        # agent_card_path uses default, extended_agent_card_path also uses default
    )
```

创建一个A2AClient实例

```python
client = A2AClient(
    httpx_client=httpx_client, agent_card=final_agent_card_to_use
)
logger.info('A2AClient initialized.')
```

发送请求和获取响应

```python
send_message_payload: dict[str, Any] = {
    'message': {
        'role': 'user',
        'parts': [
            {'kind': 'text', 'text': 'how much is 10 USD in INR?'}
        ],
        'messageId': uuid4().hex,
    },
}
request = SendMessageRequest(
    id=str(uuid4()), params=MessageSendParams(**send_message_payload)
)

response = await client.send_message(request)
print(response.model_dump(mode='json', exclude_none=True))
```





