import os

from openai import OpenAI
from dotenv import load_dotenv
from log.custom_log import custom_logger

load_dotenv()

class QwenLLM:
    def __init__(self):
        qwen_url = os.getenv("QWEN_BASE_URL")
        qwen_api_key = os.getenv("QWEN_API_KEY")
        self.qwen_client = OpenAI(
            api_key=qwen_api_key,
            base_url=qwen_url,
        )
    
    def chat(self, messages,tools=[]):

        if len(tools) > 0:
            res = self.qwen_client.chat.completions.create(
                model="qwen-max",
                messages=messages,
                tools=tools,
            )
        else:
            res = self.qwen_client.chat.completions.create(
                model="qwen-max",
                messages=messages,
            )
    
        custom_logger.info(res)
        return res
        


    