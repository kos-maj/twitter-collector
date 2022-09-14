import tweepy
import src.config as config

from pick import pick
from src.neoconnection import NeoConnection
from src.neomethods import extract_identifiers
from src.networkConstructors import buildTweetNetwork, buildUsernameNetwork

'''
TO DO: Add functionality for use case 2 (get tweets from users within a set time range)

-> tweepy client 'search_all_tweets(query, end_time, start_time, ...)' endpoint is only available
to those who have been approved for the Academic Research product track.
'''

def main():

    g_conn = NeoConnection(uri="bolt://127.0.0.1:7687", user="neo4j", pwd="testing123")
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    options = ["Usernames", "Tweet IDs"]
    option, index = pick(options , "Please select the data which will serve as input for the network constructor: ")
    identifiers = []
    extract_identifiers(data=identifiers)

    # Debugging
    # base_usernames  = ['TenchiNFT', 'BillClinton']
    # base_tweets     = ['1567933780635144194', '1568630126752964608'] 
    # Debugging 

    if(option == options[0]):           # Build network from usernames
        buildUsernameNetwork(client, identifiers, g_conn)
    else:                               # Build network from tweet id's
        buildTweetNetwork(client, identifiers, g_conn)
        # return -1

    print("[+] Program finished.")
    return 0

if __name__ == "__main__":
    main()