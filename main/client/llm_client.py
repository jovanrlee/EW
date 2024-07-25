from openai import OpenAI
import logging
class LLMClient:

#"meta-llama/llama-3-70b-instruct", 
# Wanna support NSFW? Give these a try.
# gryphe/mythomax-l2-13b
# microsoft/wizardlm-2-8x22b
# sophosympatheia/midnight-rose-70b


    def __init__(self, 
                 api_key: str, 
                 model: str = "sao10k/l3-70b-euryale-v2.1",
                 base_url: str = "https://api.novita.ai/v3/openai",
                 max_tokens: int = 512,
                 stream: bool = False):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.stream = stream

    def generate_text_response(self, chat_history) -> str:
        # Ensure messages are ordered from oldest to newest
        #TODO we prob can just revese it not necessary to sort on timestamp
        chat_history = sorted(chat_history, key=lambda x: x['timestamp'])

        # Clean the timestamps
        chat_history_cleaned = self.remove_timestamps(chat_history)

        chat_completion_res = self.client.chat.completions.create(
            model=self.model,
            messages=chat_history_cleaned,
            stream=self.stream,
            max_tokens=self.max_tokens,
            temperature=0.8,
        )

        response = ""
        if self.stream:
            for chunk in chat_completion_res:
                print(chunk.choices[0].delta.content or "", end="")
                response += chunk.choices[0].delta.content or ""
        else:
            response = chat_completion_res.choices[0].message.content

            # Lowercase the words
            response = response.lower()

            # Get rid of the upside down question mark (¿)
            response = response.replace('¿', '')

            # Get rid of the upside down exclamation mark (¡)
            response = response.replace('¡', '')

        return response

    def remove_timestamps(self, chat_history):
        # Implement the logic to remove timestamps if necessary
        return chat_history