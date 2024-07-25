from client.ig_client import IGClient,DirectThread
from client.llm_client import LLMClient
import logging
import datetime
from models.llm import LLMContext, LLMMessage
from models.contexts import ThreadContext,Message
from models.ig import TextMessage, MediaMessage, Sendable
from typing import Dict,List
import time
from random import random

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


#Code is optimzied to hit the instagram API the least amount of times possible
# Constants
# USERNAME = "luisamariagonzalez617" #no emails allowed
# PASSWORD = "1qaz2wsx3edc$RFV"

#TODO AI Internal Name
USERNAME = "jgrxl"
PASSWORD = "BushDiode251???"

def context_to_llm_context(context: Dict[str, 'ThreadContext']) -> List[LLMContext]:
    messages_as_llm_context = []
    
    for thread_id, thread_context in context.items():
        context_graph_per_simp = []

        for message in thread_context.messages:
            # If it is a text message
            if message.text is not None:
                role = "assistant" if message.sent_by == USERNAME else "user" #issue here
                context_graph_per_simp.append(LLMMessage(
                    role=role,
                    timestamp=message.timestamp,
                    content=message.text
                ))
            # Media Message
            elif message.media is not None:
                if message.media.media_type == 11 and hasattr(message.media, 'audio_url'):
                    # Handle audio message
                    pass
                elif message.media.media_type == 1 and hasattr(message.media, 'thumbnail_url'):
                    # Handle photo message
                    pass
                elif message.media.media_type == 2 and hasattr(message.media, 'video_url'):
                    # Handle video message
                    pass
                else:
                    logging.error(f"Unknown media type: 1 {message.media}")
            
            # Visual Media
            elif message.visual_media is not None:
                # TODO: Handle visual media logic
                pass
            
            # Clip
            elif message.clip is not None:
                # TODO: Handle clip logic
                pass
            elif message.reactions is not None:
                # role = "assistant" if message.sent_by == USERNAME else "user" #issue here
                # context_graph_per_simp.append(LLMMessage(
                #     role=role,
                #     timestamp=message.timestamp,
                #     content=message.reactions['emoji']
                # ))
                pass
            elif message.xma_share is not None:
                pass
            else:
                logging.error(f"Unknown media type: 2 {message.media}")


        # Add system message to the context graph
        if context_graph_per_simp:
            context_graph_per_simp.append(LLMMessage(
                role="system",
                timestamp="",
                content="Your name is Luisa Maria, a 19-year-old Colombian girl from Antioquia. You are currently studying architecture at the University of Baja California. You were born on May 15, 2004. You have one brother named Miguel and no pets. You have a flirty personality and are looking for a boyfriend. You don't know much about the United States. Despite being shy and introverted, you always try to be friendly and offer a genuine girlfriend experience. You will respond only in English and will never respond in Spanish, because you are trying to learn English. You may use emojis. Please avoid generating any content that includes actions or emotions enclosed in asterisks (e.g., giggles, blushes). You are poor and would love to accept money and gifts. Do not send any code or anything related to llm. Do not send \\commands. Respond only with clear, straightforward text without any role-playing elements."
            ))
            context_graph_per_simp = context_graph_per_simp[::-1]  # Reverse the context for LLM processing
            
            messages_as_llm_context.append(LLMContext(
                thread_id=thread_id,
                messages=context_graph_per_simp
            ))
    
    return messages_as_llm_context


def generate_responses(llm_client: LLMClient, context_graphs: List[LLMContext]) -> List[Sendable]:
    """
    Generate and print responses for each context graph.
    """
    sendables = []
    for context in context_graphs:
        thread_id = context.thread_id
        context_graph_per_simp = context.messages
        logging.debug(f"Context graph for thread {thread_id}: {context_graph_per_simp}")
        logging.info("Checking the necessity to generate responses for thread: " + thread_id)

        # Flipping context to oldest -> newest
        context_graph_per_simp = context_graph_per_simp[::-1]
        
        # Move the system instruction back to the beginning
        system_message = next((msg for msg in context_graph_per_simp if msg.role == 'system'), None)
        if system_message:
            context_graph_per_simp.remove(system_message)
            context_graph_per_simp.insert(0, system_message)

        # Extract the last message and its timestamp that isn't system
        last_message = context_graph_per_simp[0]
        if last_message.role == 'system':
            if len(context_graph_per_simp) > 1:
                last_message = context_graph_per_simp[1]
            else:
                logging.error("THIS SHOULDN'T HAPPEN")

        last_message_time = datetime.datetime.fromisoformat(last_message.timestamp)
        current_time = datetime.datetime.now()

        response = None

        # Logic A: If the last message is from me (assistant)
        if last_message.role == 'assistant':
            time_diff = current_time - last_message_time

            # If the client hasn't responded in over 1 hour
            if datetime.timedelta(hours=1) < time_diff <= datetime.timedelta(hours=5):
                response = "hola, cómo estás?"
                sendables.append(TextMessage(thread_id=thread_id, content=response))
            
            # If the client hasn't responded in over 5 days
            elif datetime.timedelta(days=5) < time_diff <= datetime.timedelta(days=7):
                response = "hola?"
                sendables.append(TextMessage(thread_id=thread_id, content=response))
            
            # If the client hasn't responded in 7 days, block the client
            elif time_diff > datetime.timedelta(days=7):
                logging.info(f"Blocking user for thread {thread_id} due to no response in 7 days.")
                # Unimplemented: ig_client.block_user(thread_id)
                continue  # Move to the next context graph
            else:
                continue  # If none of the above conditions are met, do not send a message

        # Logic B: If the last message is from the client
        elif last_message.role == 'user':
            # If I haven't responded yet
            logging.info("Response necessary. Generating...")
            response = llm_client.generate_response(chat_history=[msg.__dict__ for msg in context_graph_per_simp])
            logging.info("Response generated. Sending... " + response)
            sendables.append(TextMessage(thread_id=thread_id, content=response))

    return sendables

def create_context(threads: List[DirectThread]) -> Dict[str, ThreadContext]:
    """
    Create a context dictionary from the retrieved threads.
    """
    context = {}
    for thread in threads:
        victim_username = thread.users[0].username
        victim_id = thread.users[0].pk
        messages = [
            Message(
                assistant=USERNAME,
                victim=victim_username,
                sent_by= victim_username if message.user_id == victim_id else USERNAME,
                timestamp=message.timestamp.isoformat(),

                text=message.text,
                media = message.media,
                reactions=message.reactions['emojis'][0] if message.reactions and 'emojis' in message.reactions and message.reactions['emojis'] else None,
                visual_media = message.visual_media,
                clip = message.clip,
                xma_share = message.xma_share

            )
            for message in thread.messages
        ]
        
        thread_context = ThreadContext(
            thread_id=thread.id,
            assistant=USERNAME,
            victim=thread.users[0].username,
            messages=messages
        )
        
        context[thread.id] = thread_context

    return context
def send_messages(ig_client:IGClient, sendables:List[Sendable]):
    for sendable in sendables:
        if isinstance(sendable, TextMessage):
            ig_client.send_message_to_user(sendable.thread_id, sendable.content)
        # elif isinstance(sendable, MediaMessage):
        #     if sendable.media_type == "photo":
        #         available_photo = grab_first_unsent_media()
        #         ig_client.send_photo_to_user(path=available_photo,
        #                                      user_id=sendable.thread_id, #TODO fix
        #                                      )
        #     elif sendable.media_type == "video":
        #         available_photo = grab_first_unsent_media()
        #         ig_client.send_video_to_user(user_id=sendable.thread_id, #TODO fix
        #                                      video_type='video/mp4')
        #     elif sendable.media_type == "audio":
        #         available_audio = grab_first_unsent_media()
        #         ig_client.send_audio_to_user()
        else:
                logging.warning(f"Unsupported media type: {sendable.media_type}")
        time.sleep(5 + random.uniform(1, 3))  # Adjust the sleep duration to prevent overwhelming the server

def main():
    # Initialize LLM client
    logging.info("Initializing LLM client...")
    llm_client = LLMClient(api_key="92cac53e-9ad8-4fae-ace5-de7f22855c0f")  # Replace 'YOUR_API_KEY' with your actual API key
    logging.info("Finished initializing LLM client...")

    # Initialize Instagram client and login
    logging.info("Initializing IG Client")
    ig_client = IGClient(username=USERNAME, password=PASSWORD)
    logging.info("Finished initializing IG Client")

    # Get messages
    logging.info("Getting threads")
    threads = ig_client.get_all_threads()
    logging.info("Got all threads")
    
    # Prettify it
    logging.info("Creating context")
    context = create_context(threads) # Thread Id + Thread Content
    logging.info("Context created")


    # Thread to ML Thread
    logging.info("Converting Threads to ML Thread")
    thread_as_llm_contexts= context_to_llm_context(context)
    logging.info("Converted Threads to ML Thread")

    #Generate the responses to send
    sendables = generate_responses(
                                                 llm_client=llm_client, 
                                                 context_graphs=thread_as_llm_contexts)
    #Send Responses
    send_messages(ig_client,sendables)
    
if __name__ == "__main__":
    main()
