import cmd
import tweepy
import config
import sys

from neo4j import GraphDatabase
from neomethods import *
from neoconnection import NeoConnection

'''
TO DO: Add functionality for use case 2 (get tweets from users within a set time range)

-> tweepy client 'search_all_tweets(query, end_time, start_time, ...)' endpoint is only available
to those who have been approved for the Academic Research product track.
'''

def main():

    g_conn = NeoConnection(uri="bolt://127.0.0.1:7687", user="neo4j", pwd="testing123")
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    ### Extract usernames from file provided
    # base_usernames = []
    # if(extract_users(base_usernames)):
        # return -1

    base_usernames = ['BarlieFt', 'seobigwin', 'TenchiNFT', 'BillClinton']
    for username in base_usernames:
        user      = client.get_user(
                        username=username, 
                        user_fields=['created_at', 'description', 'location', 'protected', 'public_metrics']
                    )
        
        if user.data is None:
            continue;

        # Import user into Neo4j
        g_conn.add_transactions(
            f'''CREATE (:User{{\
                    username: "{username}",\
                    user_id: "{user.data['id']}",\
                    name: "{user.data['name']}",\
                    follower_count: "{user.data['public_metrics']['followers_count']}",\
                    following_count: "{user.data['public_metrics']['following_count']}",\
                    tweet_count: "{user.data['public_metrics']['tweet_count']}",\
                    protected: "{user.data['protected']}",\
                    created_on: "{str(user.data['created_at'])[0:10]}"}})'''
        )

        # Import followers
        followers = client.get_users_followers(id=user.data['id'])
        for follower in followers.data:
            create_follows_relation(follower, username, g_conn)
    
        # Import recent tweets (if existent)
        recent_tweets = client.search_recent_tweets(query=f'from:{username}')

        if recent_tweets.data:
            for tweet in recent_tweets.data:
                # Add tweet and authored by relation in neo4j
                tweet_id = tweet['id']
                text     = str(tweet['text']).replace('"', "'")
                g_conn.add_transactions(
                    f'''MERGE (u:User{{username: "{username}"}})\
                        MERGE (t:Tweet{{id: "{tweet_id}", text: "{text}"}})\
                        CREATE (u)-[:AUTHORED]->(t)'''
                )

                # Add likes/retweets in neo4j 
                likes    = client.get_liking_users(id=tweet['id'])
                retweets = client.get_retweeters(id=tweet['id'])
                if likes.data: 
                    for tmp_user in likes.data:
                        create_tweet_relation(tmp_user, tweet_id, 'LIKED', g_conn)
                if retweets.data:
                    for tmp_user in retweets.data:
                        create_tweet_relation(tmp_user, tweet_id, 'RETWEETED', g_conn)

        g_conn.exec_transactions()
             
    print("[+] Program finished.")
    return 0;

def user_input():
    ''' Re-name this function to 'main' if you wish to extract follower count of a file with usernames '''

    from os.path import exists
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    # Error handling
    if(len(sys.argv) != 2):
        print('Error: must provide a file of usernames as input.');
        return -1;

    path = './' + sys.argv[1];
    if(exists(path)):
        usernames = [];
        
        # Read all usernames from file
        with open(path) as fin:
            while(1):
                line = fin.readline();
                if not line:
                    break;
                else:
                    usernames.append(line.rstrip());

        # Get public metrics of each user
        user_data = client.get_users(usernames=usernames, user_fields='public_metrics');

        # Output each user's up-to-date follower count
        path = './followers.txt';
        with open(path, 'w') as fout:
            for user in user_data.data:
               fout.write(f'{user.username}:{user.public_metrics["followers_count"]}\n') 

        print('[+] Finished. Program exiting...'); 
    else:
        print('Error: input file does not exist.');
        return -1;

    return 0;

'''
def alt_main():
    # This function is not used (for now), but left here just for reference
    usr_choice = None;

    while (1):
        usr_choice  = input("\nTwitter Tool Options:\n1. Get retweeters\n2. Get likers\n3. Date range\n> ");

        if (not usr_choice.isdecimal() or usr_choice not in ['1','2','3']):
            print("\nError: must pick option '1', '2', or '3'");
        else:
            break;

    # Pull tweets from a user within a given time frame
    if (usr_choice == '3'): 
        usr_id = input("Username/ID: ");

        print("format: 'MM/DD/YYYY'");
        start = input("start date: ").split(sep='/');
        end   = input("end date: ").split(sep='/');
        
        # Convert to integers for datetime
        start = [int(i) for i in start];
        end   = [int(i) for i in end];

        query = f'from:{usr_id}';

        # Make request to API
        from datetime import datetime
        tweets = client.search_recent_tweets(
            query = query,
            start_time = datetime(year=start[2], month=start[0], day=start[1]),
            end_time = datetime(year=end[2], month=end[0], day=end[1])
        );

        # Error handling
        if (tweets.data is None):
            print("\nError: invalid author ID or username... exiting...");
            return -1;
        
        # Print retrieved tweets
        # printTweetInfo(tweets.data);
    else:
        tw_id = None;
        while(1):
            tw_id = input("Tweet ID: ");

            if(tw_id.isdecimal()):
                break;
            else:
                print("Error: Tweet ID must be decimal...");

        # Get retweeters / likers (depending on user input)
        users = client.get_retweeters(id=tw_id) if usr_choice == '1' else client.get_liking_users(id=tw_id);
        if (users.data is None):
            print("\nError: invalid tweet ID... exiting...");
            return -1;

        # Print retrieved users 
        # printUserInfo(users.data);

    return 0;
    '''

if __name__ == "__main__":
    main();