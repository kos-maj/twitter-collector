import os
import json
from .neoconnection import NeoConnection

def extract_entities(conn: NeoConnection, tweet):
    if 'entities' in tweet:
        if 'mentions' in tweet['entities']:
            for user in tweet['entities']['mentions']:
                uid = user['id']

                # Add the following transaction to the queue
                conn.add_transactions(
                    f'''MERGE (u:User {{username: "{user['username']}", id: "{uid}"}}) \
                        MERGE (t:Tweet {{id: "{tweet['id']}"}}) \
                        MERGE (t)-[:MENTIONS]->(u)'''
                )
        
        if 'annotations' in tweet['entities']:
            for annotation in tweet['entities']['annotations']:
                
                # Add the following transcations to the queue
                conn.add_transactions(
                    f'''MERGE (a:{annotation['type']} {{description: "{annotation['normalized_text']}"}}) \
                        MERGE (t:Tweet {{id: "{tweet['id']}"}}) \
                        MERGE (t)-[:ANNOTATES {{probability: "{annotation['probability']}"}}]->(a)'''
                )

def extract_metrics(conn: NeoConnection, tweet):
    text = str(tweet['text']).replace('"', "'")

    conn.add_transactions(
        f'''MERGE (t:Tweet{{\
                created_at: "{tweet['created_at']}", \
                author_id: "{tweet['author_id']}", \
                retweets: "{tweet['public_metrics']['retweet_count']}", \
                replies: "{tweet['public_metrics']['reply_count']}", \
                likes: "{tweet['public_metrics']['like_count']}", \
                quotes: "{tweet['public_metrics']['quote_count']}", \
                text: "{text}", \
                id: "{tweet['id']}"}})
            MERGE (a:User {{id: "{tweet['author_id']}"}})
            MERGE (a)-[:AUTHORED]->(t)'''
    )

def push_data(conn:NeoConnection, folderpath):

    # Change directory to folder containing afghan data
    cwd = os.getcwd()
    path = f"{cwd}/{folderpath}"
    os.chdir(path)

    for file in os.listdir():
        f_path = f"{path}/{file}" if file.endswith(".json") else None
        if f_path is not None:
            
            # Read data from json file
            with open (f_path, 'r') as f:
                data = json.load(f)

            count = 0
            for tweet in data['data']:
                tid  = tweet['id']
        
                # Format text bodies
                text = str(tweet['text']).replace('"', "'")
                auth_description = str(tweet['author']['description']).replace('"', "'")

                location = tweet['author']['location'] if 'location' in tweet['author'] else 'N/A'

                # Push tweet and author data
                conn.add_transactions(
                    f'''MERGE (t:Tweet{{\
                            created_at: "{tweet['created_at']}", \
                            author_id: "{tweet['author_id']}", \
                            retweets: "{tweet['public_metrics']['retweet_count']}", \
                            replies: "{tweet['public_metrics']['reply_count']}", \
                            likes: "{tweet['public_metrics']['like_count']}", \
                            quotes: "{tweet['public_metrics']['quote_count']}", \
                            text: "{text}", \
                            id: "{tid}"}})
                        MERGE (a:User{{\
                            id: "{tweet['author']['id']}", \
                            name: "{tweet['author']['name']}", \
                            username: "{tweet['author']['username']}", \
                            location: "{location}", \
                            description: "{auth_description}", \
                            followers: "{tweet['author']['public_metrics']['followers_count']}", \
                            following: "{tweet['author']['public_metrics']['following_count']}", \
                            tweet_count: "{tweet['author']['public_metrics']['tweet_count']}", \
                            listed_count: "{tweet['author']['public_metrics']['listed_count']}"}})
                        MERGE (a)-[:AUTHORED]->(t)'''
                )
        
                # Push data regarding mentioned users/people/places
                if 'entities' in tweet: 
                    if 'mentions' in tweet['entities']:
                        for user in tweet['entities']['mentions']:
                            uid = user['id']
            
                            # Add the following transaction to the queue
                            conn.add_transactions(
                                f'''MERGE (u:User {{username: "{user['username']}", id: "{uid}"}}) \
                                    MERGE (t:Tweet {{id: "{tid}"}}) \
                                    MERGE (t)-[:MENTIONS]->(u)'''
                            )
                    
                    if 'annotations' in tweet['entities']:
                        for annotation in tweet['entities']['annotations']:
                            
                            conn.add_transactions(
                                f'''MERGE (a:{annotation['type']} {{description: "{annotation['normalized_text']}"}}) \
                                    MERGE (t:Tweet {{id: "{tid}"}}) \
                                    MERGE (t)-[:ANNOTATES {{probability: "{annotation['probability']}"}}]->(a)'''
                            )        
        
                # Push data regarding referenced tweets
                if 'referenced_tweets' in tweet:
                    for ref_tweet in tweet['referenced_tweets']:
                        if 'text' in ref_tweet:
                            extract_metrics(conn, ref_tweet)
                            extract_entities(conn, ref_tweet)
                            conn.add_transactions(
                                f'''MATCH (original:Tweet {{id: "{tid}"}}), (new:Tweet {{id: "{ref_tweet['id']}"}})\
                                    MERGE (original)-[:{ref_tweet['type']}]->(new)''' 
                            )
        
                # Execute transactions in neo4j every 80 iterations
                count += 1;
                if count % 80 == 0:
                    conn.exec_transactions()
                    count = 0