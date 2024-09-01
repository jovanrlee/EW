
from instagrapi.exceptions import LoginRequired
import logging
from client.ig_client import IGClient

INFLUENCERS = ['followers1', 'followers2']  # Add the INFLUENCERS you want to target
USERNAME = "jgrxl"
PASSWORD = "BushDiode251???"


def follow_followers(client: IGClient, INFLUENCERS: list[str]):
    # Who am I currrently following
    # Get list of my followers
    my_followers = []
    try:
        my_followers = client.get_followers()
    except LoginRequired:
        logging.error("Login required to get followers")
        return

    for follower in INFLUENCERS:
        if follower not in my_followers:
            client.follow_user(follower)
            my_followers.append(follower)
        else:
            logging.info(f"Already following {follower}")

def main():
    logging.info("Initializing IG Client")
    ig_client = IGClient(followers=followers, password=PASSWORD)
    follow_followers(ig_client.client, INFLUENCERS)
    logging.info("Finished initializing IG Client")
