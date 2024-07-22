# ig_client.py

from instagrapi import Client
from instagrapi.types import DirectThread, Note, DirectMessage,Story
from instagrapi.exceptions import LoginRequired
from typing import List, Dict
import logging

logger = logging.getLogger()

class IGClient:
    def __init__(self, username: str, password: str, session_file: str = "session.json"):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()
        self.client.delay_range = [1, 3]  # Add random 1-3 second delay between each request
        self.account_id = None
        self._login()

    def _login(self):
        login_via_session = False
        login_via_pw = False

        try:
            session = self.client.load_settings(self.session_file)
            if session:
                try:
                    self.client.set_settings(session)
                    self.client.login(self.username, self.password)
                    try:
                        self.client.get_timeline_feed()
                        logging.info("Logged in using previous session details")
                    except LoginRequired:
                        logger.info("Session is invalid, need to login via username and password")
                        old_session = self.client.get_settings()
                        self.client.set_settings({})
                        self.client.set_uuids(old_session["uuids"])
                        self.client.login(self.username, self.password)
                    login_via_session = True
                    logging.info("Instagram client ready")
                except Exception as e:
                    print(f"Couldn't login user using session information: {e}")
                    logger.info(f"Couldn't login user using session information: {e}")
        except Exception as e:
            logging.error(f"Couldn't login user using session information: {e}")

        if not login_via_session:
            try:
                logging.info(f"Attempting to login via username and password. username: {self.username}")
                if self.client.login(self.username, self.password):
                    login_via_pw = True
                    logging.info("Logged in via password")
                    logging.debug("Saving session for later - to not login using user/pass")
                    self.client.dump_settings(self.session_file)
            except Exception as e:
                logging.error(f"Couldn't login user using username and password: {e}")

        if not login_via_pw and not login_via_session:
            logging.error("Couldn't login user with either password or session")
            raise Exception("Couldn't login user with either password or session")

        self.account_id = self.client.user_id_from_username(self.username)
        if self.account_id is None:
            logging.error("Couldn't get account ID")
            raise Exception("Couldn't get account ID")

    def get_messages_by_thread_id(self, thread_id: str, amount: int = 20) -> List[DirectMessage]:
        direct_thread_by_users: DirectThread = self.client.direct_thread(thread_id, amount=amount)
        return direct_thread_by_users.messages

    def show_last_connected_users(self, amount: int = 5) -> Dict[str, Dict[str, str]]:
        threads: List[DirectThread] = self.client.direct_threads(amount)
        users_dict = {}
        for thread in threads:
            thread_id = thread.id
            thread_pk = thread.pk
            for user in thread.users:
                users_dict[user.username] = {
                    "account_id": user.pk,
                    "thread_id": thread_id,
                    "thread_pk": thread_pk
                }
        return users_dict


    def send_message_to_user(self, text: str, thread_id: str) -> DirectMessage:
        logger.info("Sending text" + text)
        direct_message: DirectMessage = self.client.direct_send(text, thread_ids=[thread_id])
        return direct_message


    def send_video_to_user(self, user_id: str, video_type: str = None):
        if video_type == "sexy":
            path = None # Sexy video path
            pass
        if video_type == "funny":
            path = None # Funny video path
            pass

        if video_type == "normal" or video_type == None:
            path = None # Normal video path
            pass

        if video_type == "meme":
            path = None

        self.client.direct_send_video(path, user_ids=[user_id])

    def send_media_to_user(self, user_id: str, media_type: str = None):
        if media_type == "sexy":
            media_id = None # Sexy video path
            pass
        if media_type == "funny":
            media_id = None # Funny video path
            pass

        if media_type == "normal" or media_type == None:
            media_id = None # Normal video path
            pass

        if media_type == "meme":
            media_id = None

        self.client.direct_media_share(media_id, user_ids=[user_id])

    def send_story_to_user(self, user_id: str, story_type: str = None):
        if story_type == "sexy":
            story = None # Sexy video path
            pass
        if story_type == "funny":
            story = None # Funny video path
            pass

        if story_type == "normal" or story_type == None:
            story = None # Normal video path
            pass

        if story_type == "meme":
            story = None

        self.client.direct_story_share(story, user_ids=[user_id])

    

    def send_photo_to_user(self, path: str, user_id: str, photo_type: str = None):
        if photo_type == "sexy":
            path = None
        if photo_type == "funny":
            path = None
        if photo_type == "normal" or photo_type == None:
            path = None
        if photo_type == "meme":
            path = None
 
        self.client.direct_send_photo(path, user_ids=[user_id])

    
    
    # NOTES  
    def publish_notes(self, note_text: str):
        note: Note = self.client.create_note(note_text, 0)
        return note
    


 
    # STORIES
    def publish_image_tostory(self, path: str):
        # JPG Only
        note: Story = self.client.photo_upload_to_story(path, 0)
        return note

    def publish_video_to_story(self, path: str):
        # MP4 Only
        note: Story = self.client.video_upload_to_story(path, 0)
        return note
    


#Following

    def follow_user(self, user_id: str):
        user_id = self.client.user_follow(self.user_id)

        pass
    # def show_media(self):
    #     user_id = self.client.user_id_from_username(self.username)
    #     return self.client.user_medias(user_id, 20)

    # def show_threads(self):
    #     return self.client.direct_threads(amount=2, selected_filter="", thread_message_limit=2)
