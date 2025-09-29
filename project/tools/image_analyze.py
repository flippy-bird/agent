import os
from openai import OpenAI

class ImageLLM:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("QWEN_BASE_URL"),
            api_key=os.getenv("QWEN_API_KEY"),
        )

    def image_analyze(self, image_url_list:list):
        res = self.client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url_list[0],
                            },
                        },
                        {
                            "type": "text",
                            "text": "Can you tell me what is in this image?",
                        },
                    ],
                }
            ],
        )