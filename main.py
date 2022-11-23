import tweepy
import src.config as config

from elasticsearch import Elasticsearch
from pick import pick
from src.neoconnection import NeoConnection
from src.neomethods import extract_identifiers
from src.networkConstructors import buildTweetNetwork, buildUsernameNetwork, buildHashtagNetwork
from os import system
from datetime import datetime
from dateutil.relativedelta import relativedelta

'''
TO DO: tweepy client 'search_all_tweets(query, end_time, start_time, ...)' endpoint is only available
to those who have been approved for the Academic Research product track. Need bearer token for academic account.
'''

def main():
    system('clear')
    '''
    es_client = Elasticsearch(
        "https://localhost:9200",
        ca_certs="./src/http_ca.crt",
        basic_auth=("elastic", config.ELASTIC_PASSWORD)
    )

    index = 'tweet-index'
    # DOES INDEX EXIST
    es_client.indices.exists(index=index)    # True

    # DOES TWEET EXIST
    es_client.exists(index='tweet-index', id=19213)      # True
    es_client.exists(index='tweet-index', id=19211)      # False

    # CREATE AN INDEX
    try:
        es_client.indices.create(index='users')
    except Exception  as e:
        print('error: index already exists')

    tweet_data = {
        "likes": 333,
        "retweets": 333,
    }

    # CREATE A TWEET DOC
    try:
        es_client.create(index=index, id=101, document=tweet_data)
    except Exception as e:
        print('error: doc already exists')

    # UPDATE A TWEET DOC
    es_client.update(index=index, id=101, doc=tweet_data)

    # DELETE AN INDEX
    try:
        es_client.indices.delete(index='users')
    except Exception as e:
        print('error: non-existent index')


    es_client.close();
    return
    ''' 

    connection = NeoConnection(uri="bolt://127.0.0.1:7687", user="neo4j", pwd="testing123")
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    data_options = ["Usernames", "Tweet IDs", "Hashtag", "Skip data extraction"]
    data_type, index = pick(data_options , "Please select the data which will serve as input for the network constructor: ", indicator=">")
    identifiers = []

    time_options = ["Day", "Week", "Month", "3 Months"]
    time_frame, index = pick(time_options , "Please select the desired time frame: ", indicator=">")
    start_date = None

    if(time_frame == time_options[0]):      # day
        start_date = datetime.today() - relativedelta(hours=12)
    elif(time_frame == time_options[1]):    # week
        start_date = datetime.today() - relativedelta(weeks=1)
    elif(time_frame == time_options[2]):    # month
        start_date = datetime.today() - relativedelta(months=1)
    elif(time_frame == time_options[3]):    # 3 months
        start_date = datetime.today() - relativedelta(months=3)
    else:                                   # other
        input('not implemented...')
        exit(0)

    # relation_options = ['follow', 'retweet', 'like', 'embed', 'mention']
    relation_options = ['follow', 'embed', 'mention']
    es_index_name = 'tweet-index'

    print("[+] Extracting data and building network. This may take some time...")
    if(data_type == data_options[0]):                                   # Build network from usernames
        extract_identifiers(path='./data/usernames.txt', data=identifiers)
        buildUsernameNetwork(connection, client, identifiers, start_date, relation_options, es_index_name)
    elif(data_type == data_options[1]):                                 # Build network from tweet id's
        extract_identifiers(path='./data/tweets.txt', data=identifiers)
        buildTweetNetwork(connection, client, identifiers, start_date, relation_options, es_index_name)
    elif(data_type == data_options[2]):                                 # Build network from hashtag(s)
        # hashtag = input("Enter the hashtag you wish to search for: ")
        hashtag = ['NATOPAMadrid', 'NATOSummit']
        buildHashtagNetwork(connection, client, hashtag, start_date, relation_options, es_index_name) 

    system('clear')

        # options = ["Yes", "No"]
        # option, index = pick(options, "\nDo you wish to run the page rank centrality algorithm on the network: ", indicator=">")
        # if(option == options[0]):
        #     g_conn.run_pageRank(name='annotatedOrganizations', entities=['Organization','Tweet'], rel='ANNOTATES', attribute='description')
        #     g_conn.run_pageRank(name='mentionedUsers', entities=['User','Tweet'], rel='MENTIONS', attribute='username')
        #     g_conn.run_pageRank(name='annotatedPlaces', entities=['Place','Tweet'], rel='ANNOTATES', attribute='description')
        #     input("\nPress enter to continue...")

        # options = ["User", "Tweet", "No"]
        # usernames = [record['username'] for record in g_conn.get_users()]
        # while True:
        #     system('clear')
        #     option, index = pick(options, "\nDo you wish to build a subgraph on one of the given entities: ", indicator=">")

        #     if(option == options[2]): 
        #         break   
        #     elif(option == options[0]):                 # User subgraph
        #         username = input("Enter the username of an entity in the graph: ")
        #         if username not in usernames:
        #             input("[-] Error: there is no existing user with the username '{}'. Press enter to continue...".format(username))
        #         else:
        #             print("Paste the following code in the neo4j browser to obtain the desired subgraph: ")
        #             input(f'''
        #             MATCH (n:User{{username:"{username}"}})
        #             CALL apoc.path.subgraphNodes(n, {{labelFilter:'-User'}}) YIELD node
        #             RETURN node\n\nPress enter to continue...''')
        #     elif(option == options[1]):                 # Tweet subgraph
        #         input("not implemented yet...\n\nPress enter to continue...") 
            
    connection.close()
    print("\n[+] Program finished.")
    return 0

if __name__ == "__main__":
    main()