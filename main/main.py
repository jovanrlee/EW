# main_script.py

from ig_client import IGClient
from llm_client import LLMClient, create_prompt_template
from langchain_core.messages import HumanMessage, AIMessage
import logging
import random

logger = logging.getLogger()
logging.basicConfig(level = logging.INFO)

# Constants
MODEL = "moondream-test"
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
                    context_graph_per_simp.append(AIMessage(content=message.text))
                else:
                    context_graph_per_simp.append(HumanMessage(content=message.text))
            # Media Message
            elif message.media is not None:
                #Audio Message
                if message.media.media_type == 11 and message.media.audio_url is not None:
                    pass
                    audio_url = message.media.audio_url
                    # Need speech reconigiton
                    # pip install SpeechRecognition

                # Photo Message
                elif message.media.media_type == 1 and message.media.thumbnail_url is not None:
                    #TODO
                    pass

                # Video Message
                elif message.media.media_type == 2 and message.media.video_url is not None:
                    #TODO
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

def respond_to_context_graphs(ig_client: IGClient,llm_client: LLMClient, context_graphs):
    """
    Generate and print responses for each context graph.
    """
    for context in context_graphs:
        thread_id = context['thread_id']
        context_graph_per_simp = context['context_graph']
        
        # Check if there are any AI messages
        ai_message_indices = [
            idx for idx, message in enumerate(context_graph_per_simp)
            if isinstance(message, AIMessage)
        ]
        
        if ai_message_indices:
            # Find the index of the last message sent by the account
            last_ai_index = max(ai_message_indices)
            
            # Concatenate all messages from the other person after the last AI message
            input_text = ' '.join(
                message.content for message in context_graph_per_simp[last_ai_index+1:]
                if isinstance(message, HumanMessage)
            )
        else:
            # If no AI messages, use all human messages
            input_text = ' '.join(
                message.content for message in context_graph_per_simp
                if isinstance(message, HumanMessage)
            )
        
        logging.debug(f"Context graph for thread {thread_id}: {context_graph_per_simp}")
        logging.info("Generating responses...")
        # random_number = random.random() * 100  # Generate a random number between 0 and 100

        # #TODO implement what media type to send
        # #TODO fix this logic
        # if random_number < 10:  # 10% chance of photo response
        #     response = llm_client.generate_response(input_text=input_text, chat_history=context_graph_per_simp)
        #     ig_client.send_photo_to_user(response, thread_id)
        # elif random_number < 15:  # 5% chance of video response
        #     response = llm_client.generate_response(input_text=input_text, chat_history=context_graph_per_simp)
        #     ig_client.send_video_to_user(response, thread_id)
        # elif random_number < 25:  # 10% chance of sharing a post
        #     ig_client.send_media_to_user(user_id=thread_id)
        # else:  # 75% chance of text response
        response = llm_client.generate_response(input_text=input_text, chat_history=context_graph_per_simp)
        logger.debug("Response" + response)
        ig_client.send_message_to_user(response, thread_id)
 

def main():
    """
    Main function to orchestrate Instagram and LLM interactions.
    """

     # Initialize LLM client
    logging.info("Initializing LLM client...")
    llm_client = LLMClient()
    logging.info("Finished initializing LLM client Initialzed...")

    # Initialize Instagram client and login
    logging.info("Initializing IG Client")
    ig_client = IGClient(username=USERNAME, password=PASSWORD)
    logging.info("Finished initializing IG Client")

    # Retrieve last connected users and their thread IDs
    last_con = ig_client.show_last_connected_users()
    logging.debug(f"Last connected users: {last_con}")
    message_thread_ids = [user_info['thread_id'] for user_info in last_con.values()]

    # Build context graphs -- not the most efficient but easy to understsand
    context_graphs = build_context_graphs(ig_client, message_thread_ids)
    logging.debug(f"Context graphs: {context_graphs}")

    # Generate responses for each context graph
    respond_to_context_graphs(ig_client= ig_client,
                              llm_client=llm_client, 
                              context_graphs=context_graphs, 
                              )

if __name__ == "__main__":
    main()
