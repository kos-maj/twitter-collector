import config
import sys
import json
import os
from neo4j import GraphDatabase

'''
TO DO: Create network out of json data file (entities, relationships, etc.) -- DONE
TO DO: test centrality algorithms on the aforementioned networks
TO DO: implement run pageRank algorithm
TO DO: read multiple files/directories -- DONE
TO DO: Incorporate referenced tweets -- DONE
'''

class NeoConnection:
    def __init__(self, uri, user, pwd):
        self.uri = uri
        self.user = user
        self.pwd  = pwd
        self.db_conn = None
        self.transactions = []

        try:
            self.db_conn = GraphDatabase.driver(uri, auth=(self.user, self.pwd), encrypted=False)
            self.session = self.db_conn.session()
        except Exception as err:
            print(f"Failed to establish a connection: {err}")
    
    def exec_query(self, query, getResult):
        # Error handling
        if(self.db_conn is None or self.session is None):
            raise Exception("Connection not established... cannot execute transations!")

        if getResult:
            response = None
            try:
                response = list(self.session.run(query))
            except Exception as e:
                print(f"Query failed: {e}")
        
            return response
        else:
            try:
                self.session.run(query)
            except Exception as e:
                print(f"Query failed: {e}")

    def exec_transactions(self):
        # Error handling
        if(self.db_conn is None or self.session is None):
            raise Exception("Connection not established... cannot execute transations!")

        for i in self.transactions:
            try:
                self.session.run(i)
            except Exception as e:
                print(f"Transaction failed to execute: {e}")
        
        # Clear transactions
        self.transactions.clear()

    def run_pageRank(self, name, entities, rel, attribute):

        from pandas import DataFrame
    
        limit = 10
        # Create projection of data to run algorithms on
        query = f'''CALL gds.graph.project(
                    '{name}',
                    {entities},
                    '{rel}')'''
        self.exec_query(query, getResult = False)
    
        # Run pageRank algorithm
        query = f'''CALL gds.pageRank.stream('{name}')
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).{attribute} as {attribute}, score
                ORDER BY score DESC
                LIMIT {limit}'''    
    
        data = DataFrame([dict(_) for _ in self.exec_query(query, getResult=True)])

        # Display results
        length = 25
        print('-'*length, name, '-'*length, sep='')
        print(data.head(limit))
        print('='*(2*length+(len(name))))
        
        # Clean up
        query = f'''CALL gds.graph.drop('{name}')'''
        self.exec_query(query, getResult = False)

    def add_transactions(self, trans):
        if type(trans) is str:
            self.transactions.append(trans)
        elif type(trans) is list:
            self.transactions.extend(trans)
        else:
            print(f"Error: transaction(s) must be string or list in order to be added.")
    
    def close(self):
        if self.session is not None:
            self.session.close()
        if self.db_conn is not None:
            self.db_conn.close()
        

# Global variable which will be instantiated to neo4j connection
g_conn = None

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

def main():

    skipDataPush = False
    g_conn = NeoConnection(uri = "bolt://127.0.0.1:7687", user = "neo4j", pwd = "testing123")
    
    for arg in sys.argv:
        if(arg == '-s'):
            skipDataPush = True
            break
            
    if not skipDataPush:
        push_data(g_conn, folderpath='data')

    g_conn.run_pageRank(name='annotatedOrganizations', entities=['Organization','Tweet'], rel='ANNOTATES', attribute='description')
    g_conn.run_pageRank(name='mentionedUsers', entities=['User','Tweet'], rel='MENTIONS', attribute='username')
    g_conn.close()
    return 0
    

if __name__ == "__main__":
    main();