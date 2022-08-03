import config
import sys
import json
from os.path import exists
from neo4j import GraphDatabase

'''
TO DO: Create network out of json data file (entities, relationships, etc.)
TO DO: Test centrality algorithms on the aforementioned networks
TO DO: Incorporate referenced tweets
'''

# client = tweepy.Client(bearer_token=config.BEARER_TOKEN);
transaction_commands = []

def exec_transactions(session):
    # Connect to neo4j db and execute commands

    # uri = "bolt://127.0.0.1:7687"
    # db_conn = GraphDatabase.driver(uri, auth=("neo4j", "test"), encrypted=False)
    # session = db_conn.session()
    for i in transaction_commands:
        session.run(i)
    
    # Clear commands
    transaction_commands.clear()

def create_tweet_relation(user, tweet_id, relation):
    username = str(user['username']).replace('"', '')
    name     = str(user['name']).replace('"', '')
    cmd_1    = f'''MERGE (:Follower{{\
                    username: "{username}",\
                    user_id: "{user['id']}",\
                    name: "{name}"\
                }})'''
    cmd_2   = f'''MATCH (p:Follower{{username: "{username}"}}), (t:Tweet{{id: "{tweet_id}"}})\
                CREATE (p)-[:{relation}]->(t)'''
    cmd_3   = f'''MATCH (p:User{{username: "{username}"}}), (t:Tweet{{id: "{tweet_id}"}})\
                CREATE (p)-[:{relation}]->(t)'''
    
    transaction_commands.extend([cmd_1, cmd_2, cmd_3])

def create_follows_relation(user, main_username):
    username = str(user['username']).replace('"', '')
    name     = str(user['name']).replace('"', '')
    cmd_1    = f'''MERGE (:Follower{{\
                    username: "{username}",\
                    user_id: "{user['id']}",\
                    name: "{name}"\
                }})'''            
    cmd_2   = f'''MATCH (p1:Follower{{username: "{username}"}}), (p2:User{{username: "{main_username}"}})\
                CREATE (p1)-[:FOLLOWS]->(p2)'''
    cmd_3   = f'''MATCH (p1:User{{username: "{username}"}}), (p2:User{{username: "{main_username}"}})\
                CREATE (p1)-[:FOLLOWS]->(p2)'''

    transaction_commands.extend([cmd_1, cmd_2, cmd_3])

def extract_users(users: list):
    # Extracts the usernames provided at the given path. Assumes each username is seperated by a newline character.
    # 
    # Args:     path - path to file containing user(s)
    #           users - list in which to store the extracted user(s)
   
    #           exits() application if unsuccessful
    if(len(sys.argv) != 2):
        print('Error: must provide a file of base username network as input.')
        exit()

    path = str(sys.argv[1])
    if(exists(path)):
        # Read all usernames from file
        with open(path) as fin:
            while(1):
                line = fin.readline()
                if not line:
                    break
                else:
                    users.append(line.rstrip())
    else:
        print('Error: input file does not exist.');
        exit();

def format_json(path, newpath):
    with open(path) as f:
        data = json.load(f)
    
    with open(newpath, 'w') as f:
        json.dump(data, f, indent=2)

def main():

    uri = "bolt://127.0.0.1:7687"
    db_conn = GraphDatabase.driver(uri, auth=("neo4j", "testing123"), encrypted=False)
    session = db_conn.session()
    
    with open('tweets_2021-10-13T04_41_13.json') as f:
        data = json.load(f)
    
    i = 0;
    for tweet in data['data']:
        tid  = tweet['id']

        # Format text bodies
        text = str(tweet['text']).replace('"', "'")
        auth_description = str(tweet['author']['description']).replace('"', "'")

        # Push tweet and author data
        transaction_commands.append(
            f'''MERGE (t:Tweet{{\
                    created_at: "{tweet['created_at']}", \
                    author_id: "{tweet['author_id']}", \
                    retweets: "{tweet['public_metrics']['retweet_count']}", \
                    replies: "{tweet['public_metrics']['reply_count']}", \
                    likes: "{tweet['public_metrics']['like_count']}", \
                    quotes: "{tweet['public_metrics']['quote_count']}", \
                    text: "{text}", \
                    id: "{tid}"}})
                MERGE (a:Author{{\
                    id: "{tweet['author']['id']}", \
                    name: "{tweet['author']['name']}", \
                    username: "{tweet['author']['username']}", \
                    location: "{tweet['author']['location']}", \
                    description: "{auth_description}", \
                    followers: "{tweet['author']['public_metrics']['followers_count']}", \
                    following: "{tweet['author']['public_metrics']['following_count']}", \
                    tweet_count: "{tweet['author']['public_metrics']['tweet_count']}", \
                    listed_count: "{tweet['author']['public_metrics']['listed_count']}"}})
                CREATE (a)-[:AUTHORED]->(t)'''
        )

        # Push data regarding mentioned users/people/places
        if 'entities' in tweet: 
            if 'mentions' in tweet['entities']:
                for user in tweet['entities']['mentions']:
                    uid = user['id']
    
                    # Add the following transaction to the queue
                    transaction_commands.append(
                        f'''MERGE (u:User {{username: "{user['username']}", id: "{uid}"}}) \
                            MERGE (t:Tweet {{id: "{tid}"}}) \
                            CREATE (t)-[:MENTIONS]->(u)'''
                    )
            
            if 'annotations' in tweet['entities']:
                for annotation in tweet['entities']['annotations']:
                    
                    # Add the following transcations to the queue
                    transaction_commands.append(
                        f'''MERGE (a:{annotation['type']} {{description: "{annotation['normalized_text']}"}}) \
                            MERGE (t:Tweet {{id: "{tid}"}}) \
                            CREATE (t)-[:ANNOTATES {{probability: "{annotation['probability']}"}}]->(a)'''
                    )        




        if i >= 3:
            exec_transactions(session)
            break
        
        i+=1

    print("[+] Program finished.")
    return 0;

'''
    base_usernames = ['BarlieFt', 'seobigwin', 'TenchiNFT']
    for username in base_usernames:
        user      = client.get_user(
                        username=username, 
                        user_fields=['created_at', 'description', 'location', 'protected', 'public_metrics']
                    )
        
        if user.data is None:
            continue;

        ### Import data into Neo4j
        transaction_commands.append(
            # id, name, username, follower count, location, protected
            f''CREATE (:User{{\
                username: "{username}",\
                user_id: "{user.data['id']}",\
                name: "{user.data['name']}",\
                follower_count: "{user.data['public_metrics']['followers_count']}",\
                following_count: "{user.data['public_metrics']['following_count']}",\
                tweet_count: "{user.data['public_metrics']['tweet_count']}",\
                protected: "{user.data['protected']}",\
                created_on: "{str(user.data['created_at'])[0:10]}"\
                }})''
        )

        # Import followers
        followers = client.get_users_followers(id=user.data['id'])
        for follower in followers.data:
            create_follows_relation(follower, username)
    
        # Import recent tweets (if existent)
        recent_tweets = client.search_recent_tweets(query=f'from:{username}')

        if recent_tweets.data:
            for tweet in recent_tweets.data:
                # Add tweet and authored by relation in neo4j
                tweet_id = tweet['id']
                text     = str(tweet['text']).replace('"', "'")
                transaction_commands.append(
                    f''MERGE (u:User{{username: "{username}"}})\
                      MERGE (t:Tweet{{id: "{tweet_id}", text: "{text}"}})\
                      CREATE (u)-[:AUTHORED]->(t)''
                ) 

                # Add likes/retweets into neo4j 
                likes    = client.get_liking_users(id=tweet['id'])
                retweets = client.get_retweeters(id=tweet['id'])
                if likes.data: 
                    for tmp_user in likes.data:
                        create_tweet_relation(tmp_user, tweet_id, 'LIKED')
                if retweets.data:
                    for tmp_user in retweets.data:
                        create_tweet_relation(tmp_user, tweet_id, 'RETWEETED')

        exec_transactions(session)
'''

if __name__ == "__main__":
    main();