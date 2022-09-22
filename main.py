import tweepy
import src.config as config

from pick import pick
from src.neoconnection import NeoConnection
from src.neomethods import extract_identifiers
from src.networkConstructors import buildTweetNetwork, buildUsernameNetwork
from os import system

'''
TO DO: tweepy client 'search_all_tweets(query, end_time, start_time, ...)' endpoint is only available
to those who have been approved for the Academic Research product track. Need bearer token for academic account.
'''

def main():
    system('clear')

    g_conn = NeoConnection(uri="bolt://127.0.0.1:7687", user="neo4j", pwd="testing123")
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    options = ["Usernames", "Tweet IDs"]
    option, index = pick(options , "Please select the data which will serve as input for the network constructor: ", indicator=">")
    identifiers = []

    # Debugging
    # base_usernames  = ['TenchiNFT', 'BillClinton']
    # base_tweets     = ['1567933780635144194', '1568630126752964608'] 
    # Debugging 
    
    print("[+] Extracting data and building network. This may take some time...")

    if(option == options[0]):           # Build network from usernames
        extract_identifiers(path='./data/usernames.txt', data=identifiers)
        buildUsernameNetwork(client, identifiers, g_conn)
    else:                               # Build network from tweet id's
        extract_identifiers(path='./data/tweets.txt', data=identifiers)
        buildTweetNetwork(client, identifiers, g_conn)

    options = ["Yes", "No"]
    option, index = pick(options, "Network successfully created.\nDo you wish to run the page rank centrality algorithm on the network: ", indicator=">")
    
    if(option == options[0]):
        g_conn.run_pageRank(name='annotatedOrganizations', entities=['Organization','Tweet'], rel='ANNOTATES', attribute='description')
        g_conn.run_pageRank(name='mentionedUsers', entities=['User','Tweet'], rel='MENTIONS', attribute='username')

    g_conn.close()
    print("\n[+] Program finished.")
    return 0

if __name__ == "__main__":
    main()