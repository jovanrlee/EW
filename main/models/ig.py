class InstagramSendMessage:
    thread_id: str
    response: str

# Define the InstagramSendMessage class
class InstagramSendMessage:
    thread_id: str
    response: str

# Define the Sendable class
class Sendable:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id

# Define the TextMessage class, inheriting from Sendable
class TextMessage(Sendable):
    def __init__(self, thread_id: str, content: str):
        super().__init__(thread_id)
        self.content = content

# Define the MediaMessage class, inheriting from Sendable
class MediaMessage(Sendable):
    def __init__(self, thread_id: str, media_type: str, media_genre: str, media_path: str):
        super().__init__(thread_id)
        self.media_type = media_type  # audio, video, photo
        self.media_genre = media_genre  # sexy, flirty, etc
        self.media_path = media_path
