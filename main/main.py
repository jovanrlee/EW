from client.ig_client import IGClient, DirectThread
from client.llm_client import LLMClient
import logging
import datetime
from models.llm import LLMContext, LLMMessage
from models.contexts import ThreadContext, Message
from models.ig import TextMessage, MediaMessage, Sendable
from typing import Dict, List
import time
import random
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

USERNAME = "jgrxl"
PASSWORD = "BushDiode251???"

USERNAME = "luisamariagonzalez617"
PASSWORD = "1qaz2wsx3edc$RFV"

def context_to_llm_context(context: Dict[str, 'ThreadContext']) -> List[LLMContext]:
    messages_as_llm_context = []
    
    for thread_id, thread_context in context.items():
        context_graph_per_simp = []

        for message in thread_context.messages:
            if message.text is not None:
                role = "assistant" if message.sent_by == USERNAME else "user"
                context_graph_per_simp.append(LLMMessage(
                    role=role,
                    timestamp=message.timestamp,
                    content=message.text
                ))
            elif message.media is not None:
                if message.media.media_type == 11 and hasattr(message.media, 'audio_url'):
                    pass
                elif message.media.media_type == 1 and hasattr(message.media, 'thumbnail_url'):
                    pass
                elif message.media.media_type == 2 and hasattr(message.media, 'video_url'):
                    pass
                else:
                    logging.error(f"Unknown media type: 1 {message.media}")
            elif message.visual_media is not None:
                pass
            elif message.clip is not None:
                pass
            elif message.reactions is not None:
                pass
            elif message.xma_share is not None:
                pass
            else:
                logging.error(f"Unknown media type: 2 {message.media}")

        if context_graph_per_simp:
            context_graph_per_simp.append(LLMMessage(
                role="system",
                timestamp="",
                content="Your name is Luisa Maria, a 19-year-old Colombian girl from Antioquia. You are currently studying architecture at the University of Baja California. You were born on May 15, 2004. You have one brother named Miguel and no pets. You have a flirty personality and are looking for a boyfriend. You don't know much about the United States. Despite being shy and introverted, you always try to be friendly and offer a genuine girlfriend experience. You will respond only in English and will never respond in Spanish, because you are trying to learn English. You may use emojis. Please avoid generating any content that includes actions or emotions enclosed in asterisks (e.g., giggles, blushes). You are poor and would love to accept money and gifts. Do not send any code or anything related to llm. Do not send \\commands. Respond only with clear, straightforward text without any role-playing elements."
            ))
            context_graph_per_simp = context_graph_per_simp[::-1]
            messages_as_llm_context.append(LLMContext(
                thread_id=thread_id,
                messages=context_graph_per_simp
            ))
    
    return messages_as_llm_context

def __generate_media_response(thread_id:str, sendables: List[Sendable], media_type:str = None, media_genre:str = None) -> MediaMessage:
    logging.info("Media has been sent today... Sending selfie")
    
    if not media_type:
        media_type = ["photo", "video", "audio"]
        media_type = random.choices(media_type, weights=[80, 15, 5], k=1)[0]

    if not media_genre:
        confidence = None
        media_genre = "selfie"

    from service.image_sent_tracker_service import grab_first_unsent_media
    media_path = grab_first_unsent_media(thread_id=thread_id, media_directory=f".media/julianna/{media_type}/{media_genre}")
    
    return MediaMessage(
        thread_id=thread_id,
        media_path=media_path,
        media_genre="",
        media_type="photo"
    )

def generate_responses(llm_client: LLMClient, context_graphs: List[LLMContext]) -> List[Sendable]:
    sendables = []
    for context in context_graphs:
        thread_id = context.thread_id
        context_graph_per_simp = context.messages
        logging.debug(f"Context graph for thread {thread_id}: {context_graph_per_simp}")
        logging.info("Checking the necessity to generate responses for thread: " + thread_id)

        if not context_graph_per_simp:
            logging.warning(f"Context graph for thread {thread_id} is empty.")
            continue
        
        context_graph_per_simp = context_graph_per_simp[::-1]
        
        system_message = next((msg for msg in context_graph_per_simp if msg.role == 'system'), None)
        if system_message:
            context_graph_per_simp.remove(system_message)
            context_graph_per_simp.insert(0, system_message)

        last_message = next((msg for msg in context_graph_per_simp if msg.role != 'system'), None)
        if not last_message:
            logging.error(f"No valid last message found in the context graph for thread {thread_id}.")
            continue

        last_message = context_graph_per_simp[0]
        if last_message.role == 'system':
            if len(context_graph_per_simp) > 1:
                last_message = context_graph_per_simp[1]
            else:
                logging.error("THIS SHOULDN'T HAPPEN")

        last_message_time = datetime.datetime.fromisoformat(last_message.timestamp)
        current_time = datetime.datetime.now()

        response = None
        if last_message.role == 'assistant':
            time_diff = current_time - last_message_time
            checkup_responses = ["hola, cómo estás?", "hola?", "holi?", "hello", "todo está bien?", "todo bien?","como estas"]

            # TODO double text logic
            # if datetime.timedelta(hours=1) < time_diff:
            response = random.choice(checkup_responses)
            sendables.append(TextMessage(thread_id=thread_id, content=response))

            #TODO block user logic if last n messages all assistant
            # logging.info(f"Blocking user for thread {thread_id} due to no response in 7 days.")
            # continue
        
    return sendables

def create_context(threads: List[DirectThread]) -> Dict[str, ThreadContext]:
    context = {}
    for thread in threads:
        victim_username = thread.users[0].username
        victim_id = thread.users[0].pk
        messages = [
            Message(
                assistant=USERNAME,
                victim=victim_username,
                sent_by=victim_username if message.user_id == victim_id else USERNAME,
                timestamp=message.timestamp.isoformat(),
                text=message.text,
                media=message.media,
                reactions=message.reactions['emojis'][0] if message.reactions and 'emojis' in message.reactions and message.reactions['emojis'] else None,
                visual_media=message.visual_media,
                clip=message.clip,
                xma_share=message.xma_share
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
    from service.image_sent_tracker_service import grab_first_unsent_media, mark_media_as_sent

    for sendable in sendables:
        if isinstance(sendable, TextMessage):
            ig_client.send_message_to_user(text=sendable.content, thread_id=sendable.thread_id)
        elif isinstance(sendable, MediaMessage):
            if sendable.media_type == "photo":
                available_photo = grab_first_unsent_media(thread_id=sendable.thread_id, media_directory=".media/julianna/photo/")
                ig_client.send_photo_to_user(path=available_photo, thread_id=sendable.thread_id)
            elif sendable.media_type == "video":
                available_video_path = grab_first_unsent_media(thread_id=sendable.thread_id, media_directory=".media/julianna/video/")
                sent = ig_client.send_video_to_user(path=available_video_path, thread_id=sendable.thread_id)
                if sent:
                    mark_media_as_sent(thread_id=sendable.thread_id, media_path=available_photo)
            elif sendable.media_type == "audio":
                available_audio = grab_first_unsent_media(thread_id=sendable.thread_id, media_directory=".media/julianna/audio/")
                ig_client.send_audio_to_user(path=available_audio, thread_id=sendable.thread_id)
        else:
            logging.warning(f"Unsupported media type: {sendable.media_type}")
        time.sleep(5 + random.uniform(1, 3))

def main():
    logging.info("Initializing LLM client...")
    llm_client = LLMClient(api_key="92cac53e-9ad8-4fae-ace5-de7f22855c0f")
    logging.info("Finished initializing LLM client...")

    logging.info("Initializing IG Client")
    ig_client = IGClient(username=USERNAME, password=PASSWORD)
    logging.info("Finished initializing IG Client")



    # Get all of the threads
    logging.info("Getting threads")
    threads = ig_client.get_all_threads()
    logging.info("Got all threads")
    if not threads:
        logging.info("No threads to process. Exiting...")
        return
    
    # Get all of the context
    logging.info("Creating context")
    context = create_context(threads)
    logging.info("Context created")
    if not context:
        logging.info("No threads to process. Exiting...")
        return

    # Convert threads to ML Thread
    logging.info("Converting Threads to ML Thread")
    thread_as_llm_contexts = context_to_llm_context(context)
    logging.info("Converted Threads to ML Thread")
    if not thread_as_llm_contexts:
        logging.info("No threads to process. Exiting...")
        return
    

    #Generate Responses
    logging.info("Generating responses")
    sendables = generate_responses(llm_client=llm_client, context_graphs=thread_as_llm_contexts)
    logging.info("Responses generated")
    if not sendables:
        logging.info("No responses to send. Exiting...")
        return
    
    logging.info("Sending messages")
    if not sendables:
        logging.info("No messages to send. Exiting...")
        return
    send_messages(ig_client, sendables)
    logging.info("Messages sent")
    
if __name__ == "__main__":
    main()