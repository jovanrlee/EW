# ig_client.py

from instagrapi import Client
from instagrapi.types import DirectThread, Note, DirectMessage,Story
from instagrapi.exceptions import LoginRequired, ClientError 
from typing import List, Dict
import logging
import os

logger = logging.getLogger()

class IGClient:
    def __init__(self, username: str, password: str, session_file: str = "session.json"):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()
        #self.client.set_proxy()
        self.client.delay_range = [1, 3]  # Add random 1-3 second delay between each request
        self.account_id = None
        self._login()

    def _login(self):
        login_via_session = False
        login_via_pw = False

        if os.path.exists(self.session_file):
            try:
                session = self.client.load_settings(self.session_file)
                if session:
                    try:
                        self.client.set_settings(session)
                        self.client.login(self.username, self.password)
                        try:
                            self.client.account_info()
                            logging.info("Logged in using previous session details")
                        except ClientError:
                            logging.info("Session is invalid, need to login via username and password")
                            old_session = self.client.get_settings()
                            self.client.set_settings({})
                            self.client.set_uuids(old_session["uuids"])
                            self.client.login(self.username, self.password)
                        login_via_session = True
                        logging.info("Instagram client ready")
                    except Exception as e:
                        logging.info(f"Couldn't login user using session information: {e}")
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

    def get_all_threads(self, num_threads: int = 5, messages_per_thread:int = 10 ) -> List[DirectThread]:
        
        # Text Chats
        threads: List[DirectThread] = self.client.direct_threads(amount=num_threads,
                                                                 thread_message_limit=messages_per_thread)
        
        for thread in threads:
            if thread.is_group:
                # Delete all group chats
                self.client.direct_thread_hide(thread.id)
        
        return threads
        


    def send_message_to_user(self, text: str, user_id: str = None, thread_id: str = None) -> bool:
        """
        Returns True if message was sent successfully, False otherwise
        """
        if user_id and thread_id:
            raise Exception("Only one of user_id or thread_id should be provided")
        
        if not user_id and not thread_id:
            raise Exception("Either user_id or thread_id should be provided")
        
        if thread_id:
            logging.info(f"Sendig message {text} to user {thread_id}")
            self.client.direct_send(text, thread_ids=[thread_id])
            return True
        
        if user_id:
            logging.info(f"Sendig message {text} to user {user_id}")
            self.client.direct_send(text, user_ids=[user_id])
            return True
        
        return False
        


    def send_video_to_user(self, path, user_id: str,thread_id:str) -> bool:
        """
        Returns True if message was sent successfully, False otherwise
        """
        if user_id and thread_id:
            raise Exception("Only one of user_id or thread_id should be provided")
        
        if not user_id and not thread_id:
            raise Exception("Either user_id or thread_id should be provided")
        
        if thread_id:
            self.client.direct_send_video(path, thread_ids=[thread_id])
            logging.info(f"Sent video to thread {thread_id}")
            return True
        
        if user_id:
            self.client.direct_send_video(path, user_ids=[user_id])
            logging.info(f"Sent video to user {user_id}")
            return True
        return False
    
    def send_audio_to_user(self,path, thread_id:str, user_id: str) -> bool:
        """
        Returns True if message was sent successfully, False otherwise
        """
        
        if user_id and thread_id:
            raise Exception("Only one of user_id or thread_id should be provided")
        
        if not user_id and not thread_id:
            raise Exception("Either user_id or thread_id should be provided")
        
        if thread_id:
            self.client.direct_send_audio(path, thread_ids=[thread_id])
            logging.info(f"Sent audio to thread {thread_id}")
            return True
        
        if user_id:
            self.client.direct_send_audio(path, user_ids=[user_id])
            logging.info(f"Sent audio to user {user_id}")
            return True
        return False
    
    
    def send_photo_to_user(self, path: str, user_id: str, thread_id =None) -> bool:
        """
        Returns True if message was sent successfully, False otherwise
        """
        if user_id and thread_id:
            raise Exception("Only one of user_id or thread_id should be provided")
        
        if not user_id and not thread_id:
            raise Exception("Either user_id or thread_id should be provided")
        
        if thread_id:
            self.client.direct_send_photo(path, thread_ids=[thread_id])
            logging.info(f"Sent photo to thread {thread_id}")
            return True

        if user_id:
            self.client.direct_send_photo(path, user_ids=[user_id])
            logging.info(f"Sent photo to user {user_id}")
            return True
        return False


    
    
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
        user_id = self.client.user_follow(user_id)

        
    # def show_media(self):
    #     user_id = self.client.user_id_from_username(self.username)
    #     return self.client.user_medias(user_id, 20)

    # def show_threads(self):
    #     return self.client.direct_threads(amount=2, selected_filter="", thread_message_limit=2)
