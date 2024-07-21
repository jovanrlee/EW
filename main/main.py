import ollama
from instagrapi import Client
from typing import List, Dict, TypedDict
from uuid import UUID, uuid4

from instagrapi.types import DirectThread, Note, DirectMessage
from instagrapi.exceptions import LoginRequired
import logging
import uuid

logger = logging.getLogger()
MODEL = "moondream-test"
ACCOUNT_USERNAME = "jgrxl"
USERNAME = "jgrxl"
ACCOUNT_PASSWORD = "BushDiode251???"
PASSWORD= "BushDiode251???"

# Ollama Client
def ollama_respond(previous_messages:List[Dict[str, str]]) -> str:
        try:
            response = ollama.chat(
                 model=MODEL, 
                 messages=previous_messages,
                 stream=False)
            print("Response: ", response)
            #print(response['message']['content'])
            return response['message']['content']   
        except Exception as e:
            print(f"An error occurred: {e}")



def get_messages_by_thread_id(cl: Client, thread_id: str, amount:int=20):
    direct_thread_by_users: DirectThread = cl.direct_thread(thread_id, amount=amount)
    # print("Direct Thread: ", direct_thread_by_users)
    messages = direct_thread_by_users.messages
    return messages
# Instagram Client
############

def show_last_connected_users(cl: Client, amount=5) -> Dict[str, Dict[str, str]]:
    #We have to get all the threads, we'll only get the last messages though
    # This means that we can send no more than 5 messages to the same user at a time
    # Huge bug but watever
    threads: List[DirectThread] = cl.direct_threads(amount)
    # print("Retrieved threads:", threads)
    
    users_dict = {}
    for thread in threads:
        thread_id = thread.id
        thread_pk = thread.pk

        for user in thread.users:
            users_dict[user.username] = {
                "account_id": user.pk,
                "thread_id": thread_id,
                "thread_pk": thread_pk  # Assuming thread.pk is the same as thread_id
            }
    
    #print("Users dictionary:", users_dict)
    return users_dict

def send_message_to_user(cl:Client, text, user_id:str):
    cl.direct_send(text, user_ids=[user_id])
     
def instagram_show_feed(cl: Client):
        feed = cl.timeline_feed()
        return feed
              

def instagram_show_media(cl: Client):
        user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
        #print(f"User ID: {user_id}")
        medias = cl.user_medias(user_id, 20)
        return medias

def instagram_show_threads(cl: Client):
    threads = cl.direct_threads( amount = 2, 
                        selected_filter = "",
                        thread_message_limit = 2)
    return threads
    

def instagram_login_user():
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    print("Preparing instagram client")


    cl = Client()
    cl.delay_range = [1, 3] # Add random 1-3 second delay between each request

    login_via_session = False
    login_via_pw = False
    
    try: 
        session = cl.load_settings("session.json")

        if session:
            try:
                cl.set_settings(session)
                cl.login(USERNAME, PASSWORD)

                # check if session is valid
                try:
                    cl.get_timeline_feed()
                    print("Logged in using previous session details")

                except LoginRequired:
                    logger.info("Session is invalid, need to login via username and password")

                    old_session = cl.get_settings()

                    # use the same device uuids across logins
                    cl.set_settings({})
                    cl.set_uuids(old_session["uuids"])

                    cl.login(USERNAME, PASSWORD)
                login_via_session = True
                print("Instagram client ready")

                return cl

            except Exception as e:
                print("Couldn't login user using session information: %s" % e)
                logger.info("Couldn't login user using session information: %s" % e)
    except Exception as e:
                ("Couldn't login user using session information: %s" % e)
                logger.info("Couldn't login user using session information: %s" % e)


    print ("Unable to login via session")
    if not login_via_session:
        try:
            print ("Attempting to login via username and password. username: %s" % USERNAME)
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                login_via_pw = True
                print("Logged in via password")
                print("Saving session for later - to not login using user/pass")
                cl.dump_settings('session.json')

                return cl
        except Exception as e:
            
            print("Couldn't login user using username and password: %s" % e)
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        print("Couldn't login user with either password or session")
        raise Exception("Couldn't login user with either password or session")


def publish_notes(cl:Client):
    # Working
    note : Note= cl.create_note("Buenos dias!", 0)
    return note
    #print("Note created: ", note.text)

     
def main():
    cl: Client = instagram_login_user()
    user_id = cl.user_id_from_username(ACCOUNT_USERNAME)

    last_con = show_last_connected_users(cl)
    # print("Last contacted users: ", last_con)

    thread_ids = [user_info['thread_id'] for user_info in last_con.values()]

   # print("Thread Ids to search")
    # Go through all the simps
    for thread_id in thread_ids:
        context_graph_per_simp = []
        #Get the message thread we've had with them
        messages : List[DirectMessage]= get_messages_by_thread_id(cl,
                                             thread_id=thread_id,
                                             amount=10)
        for message in messages:
            # Create a message context tree   
            #print(f"Messages for thread {thread_id}: ", messages)
            
            
            # Full Message = Message
            if message.text is not None:
                message_ctx_graph = {
                "role": "assistant" if message.user_id == user_id else "user",
                "context": message.text,
            }
                context_graph_per_simp.append(message_ctx_graph)
            #Empty Message == Share Memees
            else:
                 # We need to like the posts
                 print()
        # Now we can use the context graph to generate a response

        if context_graph_per_simp.__len__() != 0:
            print(f"Context graph: {context_graph_per_simp}")
            print(f"Generating response...")
            response = ollama_respond(previous_messages= context_graph_per_simp)
            # Send the response to the simp of THAT thread ID
            print(f"Create response: {response}")
        else:
             print("No messages to respond to")
        pass




    





if __name__ == "__main__":
    main()
