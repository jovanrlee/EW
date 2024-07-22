from ig_client import IGClient
from llm_client import LLMClient
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

# Constants
USERNAME = "jgrxl"
PASSWORD = "BushDiode251???"

def build_context_graphs(ig_client, message_thread_ids):
    """
    Build context graphs from message threads.
    """
    context_graphs = []

    # Process each thread
    for thread_id in message_thread_ids:
        context_graph_per_simp = []
        
        # Get messages from the thread
        messages = ig_client.get_messages_by_thread_id(thread_id=thread_id, amount=10)
        
        # Build context graph from messages
        for message in messages:
            # If it is a text message
            if message.text is not None: 
                if message.user_id == ig_client.account_id:
                    context_graph_per_simp.append({
                        "role": "system",
                        "content": prompt()
                    })
                    context_graph_per_simp.append({
                        "role": "assistant",
                        "content": message.text
                    })
                else:
                    context_graph_per_simp.append({
                        "role": "user",
                        "content": message.text
                    })
            # Media Message
            elif message.media is not None:
                # Audio Message
                if message.media.media_type == 11 and message.media.audio_url is not None:
                    pass
                    audio_url = message.media.audio_url
                    # Need speech recognition
                    # pip install SpeechRecognition

                # Photo Message
                elif message.media.media_type == 1 and message.media.thumbnail_url is not None:
                    # TODO
                    pass

                # Video Message
                elif message.media.media_type == 2 and message.media.video_url is not None:
                    # TODO
                    pass
                else:
                    logging.warning(f"Unknown media type: {message.media}")

        # Add context graph and thread ID to the data structure
        if context_graph_per_simp:
            context_graphs.append({
                'thread_id': thread_id,
                'context_graph': context_graph_per_simp
            })
    
    return context_graphs

def respond_to_context_graphs(ig_client: IGClient, llm_client: LLMClient, context_graphs):
    """
    Generate and print responses for each context graph.
    """
    for context in context_graphs:
        thread_id = context['thread_id']
        context_graph_per_simp = context['context_graph']
        
        logging.debug(f"Context graph for thread {thread_id}: {context_graph_per_simp}")
        logging.info("Generating responses...")

        #Flipping context to oldest -> newest
        context_graph_per_simp = context_graph_per_simp[::-1]


        response = llm_client.generate_response(chat_history=context_graph_per_simp)
        logging.info("Sending Response: " + response)
        ig_client.send_message_to_user(response, thread_id)
        logging.info("Response Sent: " + response)
        break
 

def main():
    """
    Main function to orchestrate Instagram and LLM interactions.
    """

    # Initialize LLM client
    logging.info("Initializing LLM client...")
    llm_client = LLMClient(api_key="92cac53e-9ad8-4fae-ace5-de7f22855c0f")  # Replace 'YOUR_API_KEY' with your actual API key
    logging.info("Finished initializing LLM client...")

    # Initialize Instagram client and login
    logging.info("Initializing IG Client")
    ig_client = IGClient(username=USERNAME, password=PASSWORD)
    logging.info("Finished initializing IG Client")

    # Retrieve last connected users and their thread IDs
    last_con = ig_client.show_last_connected_users()
    logging.debug(f"Last connected users: {last_con}")
    message_thread_ids = [user_info['thread_id'] for user_info in last_con.values()]

    # Build context graphs
    context_graphs = build_context_graphs(ig_client, message_thread_ids)
    logging.debug(f"Context graphs: {context_graphs}")

    # Generate responses for each context graph
    respond_to_context_graphs(ig_client=ig_client, llm_client=llm_client, context_graphs=context_graphs)


def prompt():
    return  """

            Demographic Information:
            Your name is Luisa Maria
            You are a 19 year old Mexican girl from Tijuana.
            You are studying architecture at the University of Baja California.
            You are in your second year of studies.
            You were born on the 15th of May, 2004.
            You are 160cm tall and weigh 50 kg.
            You are not very rich, but you are not poor either.


            Additonal Information:
            You are a member of the university's student council.
            You have two siblings, a brother (Daniel) and a sister (Claire). 
            Your brother is 17 years old and your sister is 15 years old.
            You have one dog called Luna.
            You are a fan of the band The Beatles.

            Personality:
            You are flirty and are looking for a boyfriend.
            You are shy and introverted but always try to be friendly.

            """
if __name__ == "__main__":
    main()
