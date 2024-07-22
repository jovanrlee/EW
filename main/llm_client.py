from openai import OpenAI
import logging
class LLMClient:

    def __init__(self, 
                 api_key: str, 
                 model: str = "jondurbin/airoboros-l2-70b", 
                 base_url: str = "https://api.novita.ai/v3/openai",
                 max_tokens: int = 512,
                 stream: bool = False):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.stream = stream

    def generate_response(self, chat_history):
        chat_completion_res = self.client.chat.completions.create(
            model=self.model,
            messages=chat_history,
            stream=self.stream,
            max_tokens=self.max_tokens,
            temperature= 0.8,
        )

        response = ""
        if self.stream:
            for chunk in chat_completion_res:
                print(chunk.choices[0].delta.content or "", end="")
                response += chunk.choices[0].delta.content or ""
        else:
            response = chat_completion_res.choices[0].message.content
            logging.info(response)

        return response
