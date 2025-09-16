## Agent

### 上下文工程

> [Context Engineering(上下文工程)——大模型Agent时代非常值得学习的概念](https://zhuanlan.zhihu.com/p/1926063515296315200)

<img src="https://raw.githubusercontent.com/nashpan/image-hosting/main/image-20250910110301410.png" alt="image-20250910110301410" style="zoom:55%;" /><img src="https://raw.githubusercontent.com/nashpan/image-hosting/main/image-20250910105518579.png" alt="image-20250910105518579" style="zoom:60%;" />

感觉就是技术的整合：RAG，Memory，Prompt Engineering等

上下文工程需要做好四类工作：“记录，选择，压缩，隔离”

![image-20250910105859662](https://raw.githubusercontent.com/nashpan/image-hosting/main/image-20250910105859662.png)

- Write Context: 确定哪些信息该进模型上下文。比如，把长期记忆（跨会话的历史知识）、临时记录（Scratchpad，单会话里的中间思考）、状态数据（State，会话内的任务状态），规整好喂给模型，相当于“给模型存信息” 。到需要的时候拿来使用。
- Select Context:从工具库、Scratchpad(临时记录）、长期记忆、知识库里，精准挑出和当前任务相关的内容 。像做数学题，就选解题工具、公式知识；写文案，就选文案模板、风格案例，避免模型被无关信息干扰 。
- Compress Context: 压缩上下文，因为模型上下文窗口有长度限制（比如token数限制），得“瘦身” 。要么总结关键信息（Summarize），要么直接删掉无关内容（Trim），保证重要信息留下，还不超模型“内存” 。
- Isolate Context: 分两种场景隔离 。一是单任务内，把不同状态的上下文分开存（比如环境沙箱里的临时数据、稳定状态数据）；二是多智能体（Multi - agent）场景，给不同智能体分配独立上下文，避免互相干扰，让协作更有序 。







### 参考资料

1. [Agent 架构综述：从 Prompt 到 Context](https://mp.weixin.qq.com/s/pIcZPDqYzXrE3i6Zh4sr-Q?poc_token=HLvaq2ijs8Enbbgxn77KPvE0R9XsK0enZn05rgVK)
1. [AI Agent工程化融合：分享我的实践经验和选型技巧](https://mp.weixin.qq.com/s/itQUn-rwxbccHOye8qeDlg?poc_token=HBdktWijDpGxkS5IXKp6WYZEnWCnkE6UxKn23z_e)
1. [构建可靠AI Agent：从提示词、工作流到知识库的实战指南](https://mp.weixin.qq.com/s?__biz=MzIzOTU0NTQ0MA==&mid=2247552381&idx=1&sn=966dfc91ab7e75d349fcc82f0713ab04&scene=21&poc_token=HDxltWij5OhQzlceE79xca5aMj_-vJrPCuUKZ-Bu)
1. [初探：从0开始的AI-Agent开发踩坑实录](https://mp.weixin.qq.com/s/7Lt3WKmHoQY5HifnPFjxoQ)