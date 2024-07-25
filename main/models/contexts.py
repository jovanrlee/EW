from typing import List, Optional
from instagrapi.types import DirectThread, Note, DirectMessage,Story

class Message:
    def __init__(self, assistant: str, victim: str, sent_by:str, text: str, timestamp: str, media, reactions,visual_media, clip,xma_share):
        self.assistant = assistant
        self.victim = victim
        self.sent_by = sent_by
        self.timestamp = timestamp

        # Variety of of media types
        self.text = text
        self.media = media
        self.reactions = reactions
        self.visual_media = visual_media
        self.clip = clip
        self.xma_share = xma_share

class ThreadContext:
    def __init__(self, thread_id: str, assistant: Optional[str], victim: Optional[str], messages: List[DirectMessage]):
        self.thread_id = thread_id
        self.assistant = assistant
        self.victim = victim
        self.messages = messages