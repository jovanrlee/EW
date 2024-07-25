class InstagramSendMessage:
    thread_id: str
    response: str

class Sendable:
    thread_id: str

class TextMessage(Sendable):
    content: str

class MediaMessage(Sendable):
    media_url: str
    media_type: str  # e.g., 'photo', 'video', 'audio'