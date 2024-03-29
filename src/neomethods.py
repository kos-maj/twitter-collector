from .neoconnection import NeoConnection
from tweepy import Paginator
from elasticsearch import Elasticsearch
from .elasticmethods import merge_doc

def update_tweet(session, tweet_data):
    # Updates a tweet which already exists within the neo4j database
    session.run("MATCH (t:Tweet {id: $id})"
                "SET t.likes = $like_count, t.retweets = $rt_count, t.replies = $reply_count",
                id=tweet_data['id'], 
                like_count=tweet_data['public_metrics']['like_count'],
                rt_count=tweet_data['public_metrics']['retweet_count'],
                reply_count=tweet_data['public_metrics']['reply_count']
    )

def update_user(session, user_data):
    # Updates a user who already exists within the neo4j database
    session.run("MATCH (n:User{id: $id})"
                "SET n.followers = $followers, n.following = $following, n.tweet_count = $tweet_count",
                id=user_data['id'], 
                followers=user_data['public_metrics']['followers_count'], 
                following=user_data['public_metrics']['following_count'],
                tweet_count=user_data['public_metrics']['tweet_count']
    )

def get_users(connection: NeoConnection):
    return connection.exec_query("MATCH (n:User) RETURN (n.username) AS username", getResult=True)
    
def get_tweets(connection: NeoConnection):
    return connection.exec_query("MATCH (n:Tweet) RETURN (n.id) AS tweetId", getResult=True)

def tweet_exists(connection: NeoConnection, tweet_id):
    if len(connection.exec_query(
        f'MATCH (n:Tweet{{id: {tweet_id}}}) RETURN (n)',
        getResult=True
    )):
        return True
    return False

def user_exists(connection: NeoConnection, user_id):
    if len(connection.exec_query(
        f'MATCH (n:User{{id: {user_id}}}) RETURN (n)',
        getResult=True
    )):
        return True
    return False

def create_tweet(connection: NeoConnection, tweet_data, relations, es_index_name):
    # Creates a new tweet within the neo4j session provided.
    if tweet_exists(connection, tweet_data['id']):
        return

    # Push tweet to database 
    formatted_text = str(tweet_data['text']).replace('"', "'")
    connection.get_session().run(
        "CREATE (t:Tweet{\
        id: $tweet_id,\
        author_id: $author_id,\
        created_at: $created_at,\
        likes: $likes,\
        retweets: $retweets,\
        replies: $replies,\
        text: $text})",
        tweet_id = tweet_data['id'], 
        author_id = tweet_data['author_id'], 
        created_at = tweet_data['created_at'],
        likes = tweet_data['public_metrics']['like_count'],
        retweets = tweet_data['public_metrics']['retweet_count'],
        replies = tweet_data['public_metrics']['reply_count'], 
        text = formatted_text
    )

    # Link tweet to aux node
    connection.get_session().run(
        "MERGE (t:Tweet {id: $tweet_id})"
        "MERGE (a:Auxiliary {name: $index_name})"
        "MERGE (t)-[:BELONGS]->(a)",
        tweet_id = tweet_data['id'], index_name = es_index_name
    )

    # Push data regarding annotated entities (if specified in relations parameter)
    if "entities" in tweet_data:
        if ("mentions" in tweet_data["entities"] and "mention" in relations):
            for user in tweet_data["entities"]["mentions"]:
                connection.get_session().run(
                    "MERGE (u:User {username: $username, id: $id})"
                    "MERGE (t:Tweet {id: $tweet_id})"
                    "MERGE (t)-[:MENTIONS]->(u)",
                    username = user['username'], 
                    id = user['id'], 
                    tweet_id = tweet_data['id']
                )

        if ("annotations" in tweet_data["entities"] and "embed" in relations):
            for annotation in tweet_data["entities"]["annotations"]:
                transaction = "MERGE (a:{} {{description: $desc}})\
                                MERGE (t:Tweet {{id: $id}})\
                                MERGE (t)-[:ANNOTATES {{probability: $probability}}]->(a)".format(annotation['type'])
                connection.get_session().run(
                    transaction,
                    desc = annotation['normalized_text'], 
                    id = tweet_data['id'], 
                    probability = annotation['probability']
                )

def create_user(neo_connection:NeoConnection, neo_client, es_client: Elasticsearch, user_data, start_date, relations, es_index_name):
    # Creates a new user within the neo4j session provided. 
    # Also pulls all data relating to the user including their tweets and followers.
    if user_exists(neo_connection, user_data['id']):
        return

    # Import user
    neo_connection.get_session().run(
        "CREATE (:User{\
        username: $username,\
        id: $id,\
        description: $desc,\
        name: $name,\
        followers: $followers,\
        following: $following,\
        tweet_count: $tweet_count,\
        created_on: $created_on})",
        username = user_data['username'], 
        id = user_data['id'], 
        desc = user_data['description'], 
        name = user_data['name'],
        followers = user_data['public_metrics']['followers_count'], 
        following = user_data['public_metrics']['following_count'],
        tweet_count = user_data['public_metrics']['tweet_count'], 
        created_on = str(user_data['created_at'])[0:10]
    )

    # Link user to aux node
    neo_connection.get_session().run(
        "MERGE (u:User {id: $user_id})"
        "MERGE (a:Auxiliary {name: $index_name})"
        "MERGE (u)-[:BELONGS]->(a)",
        user_id = user_data['id'], index_name = es_index_name
    )

    # Import followers
    if "follow" in relations:
        followers = neo_client.get_users_followers(id=user_data["id"])
        for follower in followers.data:
            create_follower(neo_connection, follower, user_data['id'])

    # Import tweets
    for tweets in Paginator(
                neo_client.get_users_tweets,
                id=user_data["id"],
                start_time=start_date,
                max_results=100,
                tweet_fields=["author_id", "created_at", "public_metrics", "entities"],
    ):
        if tweets.data:
            for tweet in tweets.data:
                create_tweet(neo_connection, tweet, relations, es_index_name)
                create_author(neo_connection, user_data['id'], tweet['id'])

                # Format data for ES ingestion
                doc = {
                    'type': 'tweet',
                    'id': tweet.data['id'],
                    'created_on': tweet.data['created_at'],
                    'likes': tweet.data['public_metrics']['like_count'],
                    'retweets': tweet.data['public_metrics']['retweet_count'],
                    'replies': tweet.data['public_metrics']['reply_count'],
                    'text': tweet.data['text'],
                    'api_data': tweet.data
                }

                # Merge into elastic search (handles both update or creation)
                merge_doc(
                    client=es_client, 
                    index_name=es_index_name, 
                    doc_id=doc['id'], 
                    doc_data=doc
                )

                # Import likes/retweets
                if "like" in relations:
                    likes = neo_client.get_liking_users(id=tweet['id'])
                    if likes.data:
                        for tmp_user in likes.data:
                            create_tweet_relation(neo_connection, tmp_user, tweet['id'], 'LIKED')

                if "retweet" in relations:
                    retweets = neo_client.get_retweeters(id=tweet['id'])
                    if retweets.data:
                        for tmp_user in retweets.data:
                            create_tweet_relation(neo_connection, tmp_user, tweet['id'], 'RETWEETED')

def create_author(connection: NeoConnection, user_id, tweet_id):
    # Creates author relationship between provided user and tweet
    if (not user_exists(connection, user_id) or not tweet_exists(connection, tweet_id)):
        raise Exception("User/Tweet non-existent - failed to create author relation")

    connection.get_session().run(
        "MERGE (u:User{id: $user_id})"
        "MERGE (t:Tweet{id: $tweet_id})"
        "MERGE (u)-[:AUTHORED]->(t)",
        user_id=user_id, tweet_id=tweet_id
    ) 

def create_tweet_relation(connection: NeoConnection, user, tweet_id, relation):
    username = str(user["username"]).replace('"', "")
    name = str(user["name"]).replace('"', "")

    if user_exists(connection, user['id']):
        transaction = "MERGE (p:User {{username: $username}}), (t:Tweet {{id: $id}})\
                       MERGE (p)-[:{}]->(t)".format(relation)
        connection.get_session().run(
            transaction,
            username=username, id=tweet_id, relation=relation
        )
    else:
        transaction = "MERGE (p:Follower {{username: $username, id: $id, name: $name}})\
                       MERGE (t:Tweet {{id: $tweet_id}})\
                       MERGE (p)-[:{}]->(t)".format(relation)
        connection.get_session().run(
            transaction, 
            username=username, id=user['id'], name=name, tweet_id=tweet_id
        )

def create_follower(connection: NeoConnection, follower, user_id):
    follower_username = str(follower['username']).replace('"', "")
    follower_name = str(follower['name']).replace('"', "")

    if user_exists(connection, follower['id']):     # Follower exists as a User within graph
        connection.get_session().run(
            "MERGE (f:User {id: $f_id})"
            "MERGE (u:User {id: $user_id})"
            "MERGE (f)-[:FOLLOWS]->(u)",
            f_id=follower['id'], user_id=user_id 
        ) 
    else:
        connection.get_session().run(
            "MERGE (f:Follower {username: $f_username, id: $f_id, name: $f_name})"
            "MERGE (u:User {id: $user_id})"
            "MERGE (f)-[:FOLLOWS]->(u)",
            f_username=follower_username, f_id=follower['id'], f_name=follower_name,
            user_id=user_id
        )

def extract_identifiers(*, path: str, data: list):
    # Extracts the id's provided at the given path. Assumes each id is seperated by a newline character.
    #
    # Args:     path - path to file containing user(s)
    #           data - list to which extracted users/ids will be pushed to
    from os.path import exists

    while True:
        if exists(path):
            # Read all id's from file
            with open(path) as fin:
                while True:
                    line = fin.readline()
                    if not line:
                        break
                    else:
                        data.append(line.rstrip())
            break
        else:
            print("[-] Error: input file does not exist.")
